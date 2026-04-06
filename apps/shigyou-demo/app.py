"""
士業向け 顧問先離反予測デモアプリ
=================================
MVP #1: LightGBM + SHAP + 逆SHAP による離反予測・改善提案

対象: 税理士・社労士・行政書士事務所
核心機能:
  - 顧問先の離反リスクスコアリング
  - SHAP要因分析（なぜ離反リスクが高いか）
  - 逆SHAP改善提案（何を変えれば離反を防げるか）

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
import sys
import os

warnings.filterwarnings("ignore")
if not sys.warnoptions:
    warnings.simplefilter("ignore")

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import shap
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Dict, List, Optional, Tuple

# =====================================================================
# 共通ユーティリティ（自己完結型 — 外部modules不要）
# =====================================================================

# --- 日本語フォント ---
def setup_japanese_font():
    japanese_fonts = [
        "Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic",
        "MS Gothic", "Meiryo", "DejaVu Sans",
    ]
    available = [f.name for f in fm.fontManager.ttflist]
    for font in japanese_fonts:
        if font in available:
            plt.rcParams["font.family"] = font
            plt.rcParams["font.sans-serif"] = [font]
            plt.rcParams["axes.unicode_minus"] = False
            return font
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    return None

_font = setup_japanese_font()


def check_japanese_font_available() -> bool:
    available = [f.name for f in fm.fontManager.ttflist]
    return any(f in available for f in ["Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "MS Gothic", "Meiryo"])


# --- データ読み込み ---
def load_file(uploaded_file) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        st.error("CSVまたはExcelをアップロードしてください。")
        return None
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None


def display_data_info(df: pd.DataFrame, name: str = "データ"):
    c1, c2, c3 = st.columns(3)
    c1.metric("行数", f"{len(df):,}")
    c2.metric("列数", f"{len(df.columns):,}")
    c3.metric("欠損値", f"{df.isnull().sum().sum():,}")


# --- モデル ---
def preprocess_data(df, target_col=None, label_encoders=None, is_training=True):
    df_p = df.copy()
    if label_encoders is None:
        label_encoders = {}
    for col in df_p.columns:
        if target_col and col == target_col:
            continue
        if df_p[col].dtype == "object" or df_p[col].dtype.name == "category":
            if is_training:
                if col not in label_encoders:
                    label_encoders[col] = LabelEncoder()
                    vals = df_p[col].astype(str).fillna("__NA__")
                    df_p[col] = pd.Series(label_encoders[col].fit_transform(vals), index=df_p.index, dtype="int64")
            else:
                if col in label_encoders:
                    df_p[col] = df_p[col].astype(str).fillna("__NA__")
                    known = set(label_encoders[col].classes_)
                    df_p[col] = df_p[col].apply(lambda x: label_encoders[col].transform([x])[0] if x in known else -1)
    return df_p, label_encoders


def split_data(df, target_col, test_size=0.2, random_state=42):
    X = df.drop(columns=[target_col]).reset_index(drop=True)
    y = df[target_col].reset_index(drop=True)
    Xv, yv = X.values.copy(), y.values.copy()
    X_tr, X_te, y_tr, y_te = train_test_split(Xv, yv, test_size=test_size, random_state=random_state)
    return (pd.DataFrame(X_tr, columns=X.columns), pd.DataFrame(X_te, columns=X.columns),
            pd.Series(y_tr, name=y.name), pd.Series(y_te, name=y.name))


def train_model(X_train, y_train):
    model = lgb.LGBMRegressor(
        n_estimators=100, learning_rate=0.1, max_depth=6,
        random_state=42, verbose=-1, force_col_wise=True,
    )
    model.fit(X_train, y_train)
    return model


# --- 評価 ---
def calculate_metrics(y_true, y_pred):
    return {"MAE": mean_absolute_error(y_true, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
            "R2": r2_score(y_true, y_pred)}


def display_metrics(metrics):
    c1, c2, c3 = st.columns(3)
    c1.metric("MAE（平均絶対誤差）", f"{metrics['MAE']:.2f} ヶ月", help="小さいほど良い")
    c2.metric("RMSE", f"{metrics['RMSE']:.2f} ヶ月", help="外れ値に敏感。小さいほど良い")
    c3.metric("R²（決定係数）", f"{metrics['R2']:.3f}", help="1に近いほど良い。0.7以上で実用水準")


# --- SHAP ---
def calculate_shap_values(model, X, max_samples=500):
    X_s = X.sample(n=min(max_samples, len(X)), random_state=42) if len(X) > max_samples else X.copy()
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(X_s), X_s


def get_feature_importance(shap_values, feature_names):
    imp = np.abs(shap_values).mean(axis=0)
    return pd.DataFrame({"特徴量": feature_names, "重要度": imp}).sort_values("重要度", ascending=False).reset_index(drop=True)


# --- 逆SHAP ---

# 特徴量ごとの「すぐ実行できるアクション」テンプレート
# key=特徴量名, value=(改善方向が"上げる"時のアクション, "下げる"時のアクション, 1段階の改善幅)
ACTION_TEMPLATES = {
    # --- 既存特徴量 ---
    "直近3ヶ月連絡頻度": (
        "担当者からの情報提供メールを月1回追加する",
        None, 1,
    ),
    "直近6ヶ月面談回数": (
        "電話での簡易フォローを半年に1回追加する（対面不要）",
        None, 1,
    ),
    "質問数トレンド": (
        "こちらから「最近お困りのことはありますか？」と声がけする機会を作る",
        None, 0.5,
    ),
    "直近12ヶ月入金遅延回数": (
        None,
        "請求書発行を5日早め、リマインドメールを自動化する",
        1,
    ),
    "累計担当変更回数": (
        None,
        "担当変更時の引継ぎ面談（15分）を必須化する",
        1,
    ),
    "価格交渉フラグ": (
        None,
        "年1回の「サービス振り返りレポート」を送付し、提供価値を可視化する",
        1,
    ),
    "オプションサービス利用率": (
        "次回面談で未利用のオプションサービスを1つ紹介する",
        None, 0.1,
    ),
    # --- 新規追加特徴量 ---
    "最終面談からの経過日数": (
        None,
        "今週中に電話またはZoomで15分の近況確認を設定する",
        30,  # 30日短縮
    ),
    "直近12ヶ月顧問料改定": (
        None,  # 値上げ自体は操作しにくい
        "値上げ後1ヶ月以内に追加サービス（経営分析レポート等）を無償提供し、値上げの納得感を高める",
        1,
    ),
    "顧問先売上成長率": (
        "業績改善に直結する提案（補助金・助成金活用、経費削減策）を次回面談で実施する",
        None, 5,  # 5%改善
    ),
    "月次レポート提出遅延日数": (
        None,
        "月次レポートの作成テンプレートを整備し、提出期限を3日短縮する",
        3,  # 3日短縮
    ),
    # --- 操作不可の特徴量 ---
    "契約年数": (None, None, 0),
    "月額顧問料": (None, None, 0),
    "顧問先従業員規模": (None, None, 0),
    "顧問先業種": (None, None, 0),
}


def compute_feature_stats(df, feature_names):
    stats = {}
    for col in feature_names:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            stats[col] = {"mean": float(df[col].mean()), "median": float(df[col].median()),
                          "q25": float(df[col].quantile(0.25)), "q75": float(df[col].quantile(0.75))}
    return stats


def generate_action_suggestions(model, X, feature_names, feature_stats, target_direction="increase", top_n=5):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap_row = shap_values[0] if len(X.shape) > 1 and len(X) == 1 else np.mean(shap_values, axis=0) if len(X) > 1 else shap_values
    data_row = X.iloc[0] if len(X.shape) > 1 else X

    sorted_idx = np.argsort(shap_row) if target_direction == "increase" else np.argsort(-shap_row)
    suggestions = []
    for feat_idx in sorted_idx:
        if len(suggestions) >= top_n:
            break
        impact = float(shap_row[feat_idx])
        if target_direction == "increase" and impact >= 0:
            continue
        if target_direction == "decrease" and impact <= 0:
            continue

        fname = feature_names[feat_idx]
        current = data_row.iloc[feat_idx]

        # ACTION_TEMPLATESから実行しやすいアクションを取得
        tmpl = ACTION_TEMPLATES.get(fname)

        if not isinstance(current, (int, float, np.integer, np.floating)):
            if tmpl:
                action_text = tmpl[0] or tmpl[1] or f"「{fname}」を見直す"
            else:
                action_text = f"「{fname}」を見直す"
            suggestions.append({"feature": fname, "current": str(current), "target": "要検討",
                                "action": action_text,
                                "detail": f"推定効果: 残存月数 +{abs(impact):.1f}ヶ月",
                                "impact": round(abs(impact), 2), "effort": "低"})
            continue

        cv = float(current)
        stats = feature_stats.get(fname, {})
        median = stats.get("median", cv)
        step = tmpl[2] if tmpl else None

        # テンプレートがない or 操作不可（step==0）の特徴量はスキップ
        if tmpl and step == 0:
            continue

        # 改善方向と1段階改善を決定
        if tmpl:
            if cv > median and tmpl[1]:
                # 値が高くて悪影響 → 下げる方向のアクション
                action_text = tmpl[1]
                target = round(cv - step, 2)
            elif cv <= median and tmpl[0]:
                # 値が低くて悪影響 → 上げる方向のアクション
                action_text = tmpl[0]
                target = round(cv + step, 2)
            elif tmpl[0]:
                action_text = tmpl[0]
                target = round(cv + step, 2)
            elif tmpl[1]:
                action_text = tmpl[1]
                target = round(cv - step, 2)
            else:
                continue
        else:
            # テンプレートなし → 汎用メッセージ（1段階=現在値の10%改善）
            step = max(abs(cv * 0.1), 0.5)
            if cv > median:
                target = round(cv - step, 2)
                action_text = f"「{fname}」を {cv:.1f} → {target:.1f} に改善する"
            else:
                target = round(cv + step, 2)
                action_text = f"「{fname}」を {cv:.1f} → {target:.1f} に改善する"

        if abs(target - cv) < 0.01:
            continue

        # 実行コストの判定
        effort = "低" if tmpl else "中"

        suggestions.append({
            "feature": fname, "current": round(cv, 2), "target": target,
            "action": action_text,
            "detail": f"{fname}: {cv:.1f} → {target:.1f}（推定効果: 残存月数 +{abs(impact):.1f}ヶ月）",
            "impact": round(abs(impact), 2),
            "effort": effort,
        })
    return suggestions


# =====================================================================
# ページ設定
# =====================================================================
st.set_page_config(
    page_title="顧問先離反予測AI | 士業向けデモ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TARGET_COL = "解約までの予測月数"
RISK_HIGH = 12
RISK_MED = 24

# =====================================================================
# セッション状態
# =====================================================================
defaults = {
    "model": None, "trained": False, "label_encoders": None,
    "feature_cols": None, "metrics": None, "train_df": None,
    "X_test": None, "y_test": None, "shap_values": None,
    "X_shap_sample": None, "feature_stats": None,
    "using_default": False, "default_loaded": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _train(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        feat_cols = [c for c in df.columns if c not in [TARGET_COL, "顧問先ID"]]
        st.session_state.feature_cols = feat_cols
        df_work = df.drop(columns=["顧問先ID"], errors="ignore")
        df_proc, le = preprocess_data(df_work.copy(), TARGET_COL, is_training=True)
        X_tr, X_te, y_tr, y_te = split_data(df_proc.copy(), TARGET_COL)
        model = train_model(X_tr, y_tr)
        y_pred = model.predict(X_te)
        metrics = calculate_metrics(y_te, y_pred)
        sv, Xs = calculate_shap_values(model, X_te)
        stats = compute_feature_stats(df_work, feat_cols)
        st.session_state.update({
            "model": model, "label_encoders": le, "trained": True,
            "feature_cols": feat_cols, "X_test": X_te, "y_test": y_te,
            "metrics": metrics, "shap_values": sv, "X_shap_sample": Xs,
            "feature_stats": stats,
        })


# デフォルトデータ読み込み
if not st.session_state.default_loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "shigyou_train.csv")
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            st.session_state.train_df = df
            st.session_state.using_default = True
            _train(df)
        except Exception:
            pass
    st.session_state.default_loaded = True

# =====================================================================
# サイドバー
# =====================================================================
st.sidebar.markdown("# 🏛️ 顧問先離反予測AI")
st.sidebar.markdown("**士業事務所向けデモ**")
st.sidebar.markdown("---")

if st.session_state.using_default:
    st.sidebar.info("💡 デモデータ（150社）で自動学習済み。\n独自データのアップロードも可能です。")

st.sidebar.subheader("📁 データアップロード")
uploaded = st.sidebar.file_uploader("顧問先データ（CSV/Excel）", type=["csv", "xlsx", "xls"], key="up")

if uploaded is not None:
    new_df = load_file(uploaded)
    if new_df is not None and TARGET_COL in new_df.columns:
        st.session_state.train_df = new_df
        st.session_state.using_default = False
        st.sidebar.success(f"✅ {len(new_df)}件読み込み完了")
    elif new_df is not None:
        st.sidebar.error(f"❌ 「{TARGET_COL}」カラムが必要です")

st.sidebar.markdown("---")
if st.session_state.train_df is not None:
    lbl = "🔄 再学習" if st.session_state.trained else "▶️ モデル学習"
    if st.sidebar.button(lbl, type="primary", use_container_width=True):
        with st.spinner("学習中..."):
            _train(st.session_state.train_df)
        st.sidebar.success("✅ 学習完了")

st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("MVP #1 — 士業向け離反予測デモ v0.1")

# =====================================================================
# メインエリア
# =====================================================================
st.title("🏛️ 顧問先離反予測AI")
st.markdown(
    "LightGBM + SHAP + **逆SHAP** で、顧問先の離反リスクを予測し、"
    "**「何を変えれば離反を防げるか」**を具体的に提案します。"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 離反リスク一覧", "📈 モデル評価", "🔍 SHAP要因分析",
    "💡 改善提案（AIが分析）", "📋 データプレビュー",
])

# =====================================================================
# Tab 1: 離反リスク一覧
# =====================================================================
with tab1:
    st.header("顧問先 離反リスク一覧")
    if st.session_state.trained and st.session_state.train_df is not None:
        df = st.session_state.train_df.copy()
        model = st.session_state.model
        le = st.session_state.label_encoders
        feat_cols = st.session_state.feature_cols

        df_work = df.drop(columns=["顧問先ID", TARGET_COL], errors="ignore")
        df_proc, _ = preprocess_data(df_work.copy(), target_col=None, label_encoders=le, is_training=False)
        preds = model.predict(df_proc)
        df["予測残存月数"] = np.round(preds, 1)

        def _risk(m):
            if m <= RISK_HIGH:
                return "🔴 高リスク"
            if m <= RISK_MED:
                return "🟡 中リスク"
            return "🟢 低リスク"

        df["リスクレベル"] = df["予測残存月数"].apply(_risk)
        df_s = df.sort_values("予測残存月数").reset_index(drop=True)

        n_h = (df_s["予測残存月数"] <= RISK_HIGH).sum()
        n_m = ((df_s["予測残存月数"] > RISK_HIGH) & (df_s["予測残存月数"] <= RISK_MED)).sum()
        n_l = (df_s["予測残存月数"] > RISK_MED).sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("全顧問先数", f"{len(df)}社")
        c2.metric("🔴 高リスク", f"{n_h}社", help=f"{RISK_HIGH}ヶ月以内")
        c3.metric("🟡 中リスク", f"{n_m}社")
        c4.metric("🟢 低リスク", f"{n_l}社")

        # =====================================================================
        # 解約コスト試算バナー
        # =====================================================================
        # 年間顧問料の計算（月額 × 12）
        if "月額顧問料" in df_s.columns:
            df_s["年間顧問料"] = df_s["月額顧問料"] * 12
        else:
            df_s["年間顧問料"] = 0

        total_annual_revenue = df_s["年間顧問料"].sum()

        high_risk_df = df_s[df_s["予測残存月数"] <= RISK_HIGH]
        med_risk_df  = df_s[(df_s["予測残存月数"] > RISK_HIGH) & (df_s["予測残存月数"] <= RISK_MED)]

        high_loss = high_risk_df["年間顧問料"].sum()
        high_med_loss = high_loss + med_risk_df["年間顧問料"].sum()

        high_loss_man = high_loss / 10_000
        high_med_loss_man = high_med_loss / 10_000
        high_ratio = (high_loss / total_annual_revenue * 100) if total_annual_revenue > 0 else 0
        high_med_ratio = (high_med_loss / total_annual_revenue * 100) if total_annual_revenue > 0 else 0

        st.markdown("---")
        st.subheader("💸 解約コスト試算")

        st.error(
            f"⚠️ 離反リスク高の顧問先 **{len(high_risk_df)}社** を放置した場合の年間損失額: "
            f"**¥{high_loss_man:,.0f}万**　（全売上の **{high_ratio:.1f}%**）"
        )
        st.warning(
            f"🟡 中リスクも含めた場合の年間損失額: "
            f"**¥{high_med_loss_man:,.0f}万**　（全売上の **{high_med_ratio:.1f}%**）"
        )
        st.caption("※ 計算方法: 月額顧問料×12ヶ月の単純合算。実際の解約時期により変動します。")

        with st.expander("計算の内訳を見る"):
            _top3_cost = df_s[df_s["予測残存月数"] <= RISK_HIGH].nlargest(3, "年間顧問料")[
                ["顧問先ID", "月額顧問料", "年間顧問料"]
            ].copy() if "顧問先ID" in df_s.columns else df_s[df_s["予測残存月数"] <= RISK_HIGH].nlargest(3, "年間顧問料")[
                ["月額顧問料", "年間顧問料"]
            ].copy()
            _top3_cost = _top3_cost.rename(columns={"月額顧問料": "月額顧問料（円）", "年間顧問料": "年額（円）"})
            st.dataframe(_top3_cost.reset_index(drop=True), use_container_width=True, hide_index=True)

        # 解約インパクト メトリクス（3列）
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "高リスク顧問先数",
            f"{len(high_risk_df)}社",
            delta=None,
            help=f"予測残存月数が{RISK_HIGH}ヶ月以内の顧問先",
        )
        m2.metric(
            "推定年間損失額（高リスク）",
            f"¥{high_loss_man:,.0f}万",
            delta=None,
            help="高リスク顧問先の月額顧問料×12の合計",
        )
        m3.metric(
            "売上に対する損失比率",
            f"{high_ratio:.1f}%",
            delta=None,
            help="全顧問先年間売上に対する高リスク損失の割合",
        )

        # =====================================================================
        # 今すぐ対応すべき顧問先 TOP3 カード
        # =====================================================================
        st.markdown("---")
        st.subheader("🚨 今すぐ対応すべき顧問先 TOP3")
        st.caption("離反リスクが最も高い3社。各カードの詳細を開くと逆SHAP改善要因も確認できます。")

        top3 = df_s.head(3)
        _model  = st.session_state.model
        _le     = st.session_state.label_encoders
        _feat   = st.session_state.feature_cols

        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            client_id = row.get("顧問先ID", f"顧問先{rank}")
            pred_months = row["予測残存月数"]
            annual_fee  = row.get("年間顧問料", 0)
            risk_pct    = (pred_months / RISK_MED * 100) if RISK_MED > 0 else 0

            # 逆SHAP 上位3要因（このクライアント行で算出）
            try:
                _row_feat = df.drop(columns=["顧問先ID", TARGET_COL, "予測残存月数", "リスクレベル", "年間顧問料"], errors="ignore")
                _row_feat = _row_feat[df["顧問先ID"] == client_id].copy() if "顧問先ID" in df.columns else _row_feat.iloc[[rank - 1]]
                _row_proc, _ = preprocess_data(_row_feat.copy(), target_col=None, label_encoders=_le, is_training=False)
                _explainer = shap.TreeExplainer(_model)
                _sv = _explainer.shap_values(_row_proc)
                _sv_row = _sv[0] if len(_sv.shape) > 1 else _sv
                # 離反リスクを高める要因（SHAP値が負 = 残存月数を短くする）
                _factor_df = pd.DataFrame({
                    "特徴量": _feat,
                    "AI重要度スコア": _sv_row,
                }).sort_values("AI重要度スコア").head(3)
                top3_factors = [
                    f"**{r['特徴量']}**（{r['AI重要度スコア']:.1f}ヶ月）"
                    for _, r in _factor_df.iterrows()
                ]
            except Exception:
                top3_factors = ["（要因分析エラー）"]

            badge_color = "#EF4444" if pred_months <= RISK_HIGH else "#F59E0B"
            with st.expander(
                f"{'🥇' if rank==1 else '🥈' if rank==2 else '🥉'} "
                f"【{rank}位】{client_id}　"
                f"予測残存: {pred_months:.1f}ヶ月　年間顧問料: ¥{annual_fee/10_000:,.0f}万",
                expanded=(rank == 1),
            ):
                card_c1, card_c2, card_c3 = st.columns(3)
                card_c1.metric("離反まで（予測）", f"{pred_months:.1f}ヶ月")
                card_c2.metric("年間顧問料", f"¥{annual_fee/10_000:,.1f}万")
                card_c3.metric("リスク達成率", f"{risk_pct:.0f}%", help="残存月数/中リスク閾値。低いほど危険")

                st.markdown("**⚠️ 離反リスクを高める要因 TOP3（逆SHAP）**")
                for fi, factor_txt in enumerate(top3_factors, 1):
                    st.markdown(f"{fi}. {factor_txt}")

        st.markdown("---")
        st.subheader("🔴 要注意顧問先 TOP10")
        top10 = df_s.head(10)
        show = ["顧問先ID", "リスクレベル", "予測残存月数", "契約年数", "月額顧問料",
                "最終面談からの経過日数", "直近6ヶ月面談回数", "直近12ヶ月入金遅延回数",
                "質問数トレンド", "価格交渉フラグ"]
        show = [c for c in show if c in top10.columns]
        st.dataframe(top10[show], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("全顧問先リスク分布")
        setup_japanese_font()
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(df["予測残存月数"], bins=20, color="#2563EB", alpha=0.7, edgecolor="white")
        ax.axvline(RISK_HIGH, color="red", ls="--", label=f"高リスク ({RISK_HIGH}ヶ月)")
        ax.axvline(RISK_MED, color="orange", ls="--", label=f"中リスク ({RISK_MED}ヶ月)")
        ax.set_xlabel("予測残存月数")
        ax.set_ylabel("顧問先数")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        csv = df_s.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 リスク一覧をCSVでダウンロード", csv, "risk_list.csv", "text/csv", use_container_width=True)
    else:
        st.info("モデルを学習するとリスク一覧が表示されます")

# =====================================================================
# Tab 2: モデル評価
# =====================================================================
with tab2:
    st.header("モデル評価指標")
    if st.session_state.trained and st.session_state.metrics:
        _r2 = st.session_state.metrics.get("R2", 0)
        if _r2 > 0.7:
            _precision_label = "📊 予測精度: 高"
            _precision_color = "success"
        elif _r2 >= 0.4:
            _precision_label = "📊 予測精度: 中"
            _precision_color = "warning"
        else:
            _precision_label = "📊 予測精度: 低"
            _precision_color = "error"
        getattr(st, _precision_color)(_precision_label)
        display_metrics(st.session_state.metrics)
        st.markdown("---")
        st.markdown("""
        **評価指標の読み方**
        - **MAE**: 予測と実際の差（月数）の平均。小さいほど良い。
        - **RMSE**: 外れ値を重視した誤差指標。
        - **R²**: モデルの説明力（1.0が完璧）。0.7以上で実用水準。
        """)
    else:
        st.info("モデルを学習すると評価指標が表示されます")

# =====================================================================
# Tab 3: SHAP要因分析
# =====================================================================
with tab3:
    st.header("SHAP要因分析")
    st.markdown("**「なぜこの顧問先は離反リスクが高いのか？」**を可視化します。")

    if st.session_state.trained and st.session_state.shap_values is not None:
        sv = st.session_state.shap_values
        Xs = st.session_state.X_shap_sample

        setup_japanese_font()

        st.subheader("📊 SHAP Summary Plot")
        st.caption("赤=値が高い、青=値が低い。右に寄るほど予測残存月数を延ばす（離反防止）要因。")
        fig1, _ = plt.subplots(figsize=(10, 8))
        shap.summary_plot(sv, Xs, max_display=15, show=False, plot_size=None)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close("all")

        st.markdown("---")
        st.subheader("📊 特徴量重要度")
        fig2, _ = plt.subplots(figsize=(10, 8))
        shap.summary_plot(sv, Xs, plot_type="bar", max_display=15, show=False, plot_size=None)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close("all")

        st.markdown("---")
        st.subheader("📋 特徴量重要度ランキング")
        imp_df = get_feature_importance(sv, Xs.columns.tolist())
        st.dataframe(imp_df, use_container_width=True, hide_index=True)
    else:
        st.info("モデルを学習するとSHAP分析が表示されます")

# =====================================================================
# Tab 4: 改善提案（AIが分析）（★最大の差別化）
# =====================================================================
with tab4:
    st.header("💡 改善提案（AIが分析）")
    st.markdown("""
    | | 通常のSHAP | 逆SHAP |
    |---|---|---|
    | 問い | なぜ離反リスクが高いか？（Why） | **何を変えれば離反を防げるか？（How）** |
    | 出力 | 要因の説明 | **具体的アクション提案** |
    """)

    if st.session_state.trained and st.session_state.train_df is not None:
        df = st.session_state.train_df.copy()
        model = st.session_state.model
        le = st.session_state.label_encoders
        feat_cols = st.session_state.feature_cols
        stats = st.session_state.feature_stats

        df_work = df.drop(columns=["顧問先ID", TARGET_COL], errors="ignore")
        df_proc, _ = preprocess_data(df_work.copy(), target_col=None, label_encoders=le, is_training=False)
        preds = model.predict(df_proc)
        df["予測残存月数"] = np.round(preds, 1)

        high_risk = df[df["予測残存月数"] <= RISK_HIGH].sort_values("予測残存月数")

        if len(high_risk) == 0:
            st.success("🎉 高リスク顧問先は現在ありません！")
        else:
            st.warning(f"🔴 **{len(high_risk)}社** が高リスク（{RISK_HIGH}ヶ月以内に離反の恐れ）")
            client_ids = high_risk["顧問先ID"].tolist()
            selected = st.selectbox("改善提案を表示する顧問先を選択", client_ids)

            if selected:
                row = df[df["顧問先ID"] == selected].iloc[0]
                st.markdown(f"### 顧問先: **{selected}**")

                ic = st.columns(4)
                ic[0].metric("予測残存月数", f"{row['予測残存月数']:.1f}ヶ月")
                ic[1].metric("契約年数", f"{row['契約年数']}年")
                ic[2].metric("月額顧問料", f"¥{int(row['月額顧問料']):,}")
                ic[3].metric("面談回数(6M)", f"{int(row['直近6ヶ月面談回数'])}回")

                st.markdown("---")
                st.subheader("🎯 改善アクション提案")

                row_feat = df_work[df["顧問先ID"] == selected].copy()
                row_proc, _ = preprocess_data(row_feat.copy(), target_col=None, label_encoders=le, is_training=False)

                suggestions = generate_action_suggestions(model, row_proc, feat_cols, stats, "increase", top_n=5)

                if suggestions:
                    for i, s in enumerate(suggestions, 1):
                        effort_badge = {"低": "🟢 すぐできる", "中": "🟡 少し工夫が必要", "高": "🔴 要検討"}.get(s.get("effort", "中"), "🟡")
                        with st.container():
                            st.markdown(f"### 提案 {i}: {s['action']}")
                            st.caption(s.get("detail", ""))
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("推定効果", f"+{s['impact']:.1f} ヶ月")
                            col_b.metric("現在値 → 目標値", f"{s['current']} → {s['target']}")
                            col_c.metric("実行コスト", effort_badge)
                        st.markdown("---")
                else:
                    st.info("数値ベースの改善提案を生成できませんでした。定性的要因の見直しを検討してください。")

                st.subheader("📊 この顧問先の要因分解")
                explainer = shap.TreeExplainer(model)
                sv = explainer.shap_values(row_proc)
                factor_df = pd.DataFrame({
                    "特徴量": feat_cols,
                    "AI重要度スコア": np.round(sv[0], 3),
                    "影響方向": ["⬇️ 離反リスク上昇" if v < 0 else "⬆️ 離反防止" for v in sv[0]],
                }).sort_values("AI重要度スコア").reset_index(drop=True)
                st.dataframe(factor_df, use_container_width=True, hide_index=True)
    else:
        st.info("モデルを学習すると改善提案が表示されます")

# =====================================================================
# Tab 5: データプレビュー
# =====================================================================
with tab5:
    st.header("データプレビュー")
    if st.session_state.train_df is not None:
        df = st.session_state.train_df
        if st.session_state.using_default:
            st.info("💡 デモデータ（150社の合成顧問先データ）を表示しています")
        display_data_info(df, "顧問先データ")
        st.markdown("##### 先頭20行")
        st.dataframe(df.head(20), use_container_width=True)
        st.markdown("---")
        st.subheader("📊 基本統計量")
        st.dataframe(df.describe(), use_container_width=True)
    else:
        st.info("サイドバーからデータをアップロードしてください")

# =====================================================================
# 定期運用チェックリスト
# =====================================================================
st.markdown("---")
st.markdown("### 📋 定期運用チェックリスト")
with st.expander("週次チェック"):
    st.markdown("- □ 離反リスク上位5件を確認\n- □ 逆SHAP提案に基づく改善アクション実施")
with st.expander("月次チェック"):
    st.markdown("- □ 全顧問先のリスクスコア再計算\n- □ 月次レポートと突合して財務変化を確認")

# =====================================================================
# フッター: 関連ツールカード
# =====================================================================
st.markdown("---")
st.markdown("### 🔗 関連ツール")
ft1, ft2, ft3 = st.columns(3)
with ft1:
    st.markdown(
        """
        <div style="border:1px solid #E2E8F0;border-radius:12px;padding:20px;text-align:center;height:100%;background:#F8FAFC;">
        <div style="font-size:2rem;">📊</div>
        <h4 style="margin:8px 0 4px 0;">クロスセル分析</h4>
        <p style="color:#64748B;font-size:0.9rem;">離反リスクの低い顧問先に追加提案</p>
        <a href="https://shigyou-crosssell.streamlit.app" target="_blank"
           style="display:inline-block;margin-top:8px;padding:6px 20px;background:#3B82F6;color:white;border-radius:8px;text-decoration:none;font-size:0.9rem;">
           ツールを開く →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
with ft2:
    st.markdown(
        """
        <div style="border:1px solid #E2E8F0;border-radius:12px;padding:20px;text-align:center;height:100%;background:#F8FAFC;">
        <div style="font-size:2rem;">📝</div>
        <h4 style="margin:8px 0 4px 0;">月次レポート</h4>
        <p style="color:#64748B;font-size:0.9rem;">顧問先の財務状況を月次で把握</p>
        <a href="https://shigyou-report.streamlit.app" target="_blank"
           style="display:inline-block;margin-top:8px;padding:6px 20px;background:#3B82F6;color:white;border-radius:8px;text-decoration:none;font-size:0.9rem;">
           ツールを開く →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
with ft3:
    st.markdown(
        """
        <div style="border:1px solid #E2E8F0;border-radius:12px;padding:20px;text-align:center;height:100%;background:#F8FAFC;">
        <div style="font-size:2rem;">🏛️</div>
        <h4 style="margin:8px 0 4px 0;">士業ポータル</h4>
        <p style="color:#64748B;font-size:0.9rem;">全ツール一覧</p>
        <a href="https://shigyou-ai-tools.streamlit.app" target="_blank"
           style="display:inline-block;margin-top:8px;padding:6px 20px;background:#6366F1;color:white;border-radius:8px;text-decoration:none;font-size:0.9rem;">
           ポータルを開く →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
