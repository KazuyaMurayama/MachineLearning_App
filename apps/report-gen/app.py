"""
月次レポート自動生成ツール
========================
freee/MFのCSV試算表から前月比・前年同月比・異常値を自動検知し、
顧問先向け月次レポートを自動生成するStreamlitアプリ
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import date

# === 日本語フォント ===
def setup_japanese_font():
    candidates=["Noto Sans CJK JP","Noto Sans JP","Yu Gothic","MS Gothic","Meiryo","DejaVu Sans"]
    available={f.name for f in fm.fontManager.ttflist}
    for fn in candidates:
        if fn in available:
            plt.rcParams["font.family"]=fn; plt.rcParams["axes.unicode_minus"]=False; return fn
    plt.rcParams["font.family"]="DejaVu Sans"; return "DejaVu Sans"

# === 定数 ===
KEY_ACCOUNTS=["売上高","売上原価","売上総利益","販売管理費計","営業利益","経常利益"]
ANOMALY_THRESHOLD=0.30  # 30%以上の変動を異常値とする

# === 分析関数 ===
def load_csv(path_or_file):
    """CSVファイルを読み込む"""
    try:
        if isinstance(path_or_file,str):
            return pd.read_csv(path_or_file,encoding="utf-8-sig")
        return pd.read_csv(path_or_file,encoding="utf-8-sig")
    except:
        try: return pd.read_csv(path_or_file,encoding="cp932")
        except: return None

def calc_mom(df):
    """前月比を計算（最新月 vs 前月）"""
    if len(df)<2: return {}
    latest=df.iloc[-1]; prev=df.iloc[-2]
    result={}
    for col in df.columns:
        if col=="年月": continue
        try:
            cur=float(latest[col]); prv=float(prev[col])
            if prv!=0:
                pct=(cur-prv)/abs(prv)*100
                result[col]={"current":cur,"previous":prv,"change":cur-prv,"pct":round(pct,1)}
        except: pass
    return result

def calc_yoy(df_cur,df_prev):
    """前年同月比を計算（当期最新月 vs 前期同月）"""
    if len(df_cur)==0 or len(df_prev)==0: return {}
    latest_idx=len(df_cur)-1
    if latest_idx>=len(df_prev): return {}
    latest=df_cur.iloc[latest_idx]; prev_yr=df_prev.iloc[latest_idx]
    result={}
    for col in df_cur.columns:
        if col=="年月": continue
        try:
            cur=float(latest[col]); prv=float(prev_yr[col])
            if prv!=0:
                pct=(cur-prv)/abs(prv)*100
                result[col]={"current":cur,"prev_year":prv,"change":cur-prv,"pct":round(pct,1)}
        except: pass
    return result

def estimate_cause_and_action(acct,direction,pct,mom):
    """異常値に対する推定原因と推奨アクションを返す"""
    pct_abs=abs(pct)
    # 売上高の増減
    if acct=="売上高":
        if direction=="増加":
            cost_data=mom.get("売上原価",{})
            if cost_data and cost_data.get("pct",0)>0:
                return ("売上原価も連動増加→取引量増加が主因",
                        "利益率が維持されているか確認を推奨")
            return ("売上増加の主因を特定してください",
                    "価格改定・新規取引先・季節要因を確認")
        else:
            return ("売上減少→取引量減少または単価下落の可能性",
                    "主要取引先別の売上内訳を確認を推奨")
    # 売上原価
    if acct=="売上原価":
        sales_data=mom.get("売上高",{})
        if direction=="増加":
            if sales_data and sales_data.get("pct",0)>0:
                return ("売上増加に伴う原価増",
                        "粗利率が悪化していないか確認を推奨")
            return ("売上横ばいで原価増→仕入単価上昇の可能性",
                    "仕入先との価格交渉を検討")
        else:
            return ("原価減少→仕入量減少または単価改善",
                    "売上への影響がないか確認を推奨")
    # 売上総利益
    if acct=="売上総利益":
        if direction=="増加":
            return ("粗利改善→売上増または原価率改善",
                    "改善要因を特定し、継続施策を検討")
        else:
            return ("粗利悪化→原価率上昇の可能性",
                    "原価内訳の精査と改善策の検討を推奨")
    # 販売管理費計
    if acct=="販売管理費計":
        if direction=="増加":
            return (f"前月比+{pct_abs:.0f}%増。一時的経費増の可能性",
                    "一時的支出か恒常的増加か確認を推奨")
        else:
            return ("販管費減少→コスト削減効果の可能性",
                    "必要な投資まで削減していないか確認")
    # 営業利益
    if acct=="営業利益":
        if direction=="減少":
            sg_data=mom.get("販売管理費計",{})
            sales_data=mom.get("売上高",{})
            if sg_data:
                cur_sales=sales_data.get("current",1) if sales_data else 1
                prev_sales=sales_data.get("previous",1) if sales_data else 1
                sg_cur=sg_data.get("current",0)
                sg_prev=sg_data.get("previous",0)
                if prev_sales!=0 and cur_sales!=0:
                    rate_cur=sg_cur/cur_sales*100
                    rate_prev=sg_prev/prev_sales*100
                    return (f"販管費率が{rate_prev:.1f}%→{rate_cur:.1f}%に悪化",
                            "経費見直しを推奨")
            return ("営業利益悪化→売上減少または経費増加",
                    "PL科目別の増減分析を推奨")
        else:
            return ("営業利益改善→売上増加または経費削減効果",
                    "改善要因の特定と継続性を確認")
    # 経常利益
    if acct=="経常利益":
        if direction=="減少":
            return ("経常利益悪化→営業外損益の影響を確認",
                    "借入金利息・為替差損等の確認を推奨")
        else:
            return ("経常利益改善→本業収益力の向上",
                    "営業利益との乖離がないか確認")
    # 広告宣伝費などその他の経費科目
    if "費" in acct or "経費" in acct:
        if direction=="増加":
            return (f"前月比+{pct_abs:.0f}%増。一時的キャンペーンか確認",
                    "予算対比と費用対効果の確認を推奨")
        else:
            return (f"前月比{pct_abs:.0f}%減少",
                    "削減が業務に影響していないか確認")
    # デフォルト
    return (f"前月比{pct_abs:.0f}%の{direction}",
            "原因の特定と影響範囲の確認を推奨")

def detect_anomalies(mom,yoy,threshold=ANOMALY_THRESHOLD):
    """異常値（前月比or前年同月比でthreshold以上変動）を検出"""
    anomalies=[]
    for acct,data in mom.items():
        if abs(data["pct"])>=threshold*100:
            direction="増加" if data["pct"]>0 else "減少"
            cause,action=estimate_cause_and_action(acct,direction,data["pct"],mom)
            anomalies.append({"科目":acct,"種別":"前月比","変動率":f"{data['pct']:+.1f}%","方向":direction,
                "当月":f"{data['current']:,.0f}万円","前月":f"{data['previous']:,.0f}万円",
                "差額":f"{data['change']:+,.0f}万円","severity":"🔴" if abs(data["pct"])>=50 else "🟡",
                "推定原因":cause,"推奨アクション":action})
    for acct,data in yoy.items():
        if abs(data["pct"])>=threshold*100:
            direction="増加" if data["pct"]>0 else "減少"
            cause,action=estimate_cause_and_action(acct,direction,data["pct"],mom)
            anomalies.append({"科目":acct,"種別":"前年同月比","変動率":f"{data['pct']:+.1f}%","方向":direction,
                "当月":f"{data['current']:,.0f}万円","前年同月":f"{data['prev_year']:,.0f}万円",
                "差額":f"{data['change']:+,.0f}万円","severity":"🔴" if abs(data["pct"])>=50 else "🟡",
                "推定原因":cause,"推奨アクション":action})
    return sorted(anomalies,key=lambda x:abs(float(x["変動率"].replace("%","").replace("+",""))),reverse=True)

def generate_report_md(df_cur,df_prev,mom,yoy,anomalies,client_name,report_month):
    """Markdown形式の月次レポートを生成"""
    lines=[f"# 月次経営レポート",f"",f"**顧問先**: {client_name}",f"**対象月**: {report_month}",
        f"**作成日**: {date.today().strftime('%Y年%m月%d日')}",f"",f"---",f""]
    # 主要指標サマリー
    lines.append("## 1. 主要指標サマリー\n")
    lines.append("| 科目 | 当月 | 前月比 | 前年同月比 |")
    lines.append("|------|------|--------|-----------|")
    for acct in KEY_ACCOUNTS:
        cur_val=mom.get(acct,{}).get("current","-")
        mom_pct=mom.get(acct,{}).get("pct","-")
        yoy_pct=yoy.get(acct,{}).get("pct","-")
        cur_str=f"¥{cur_val:,.0f}万" if isinstance(cur_val,(int,float)) else "-"
        mom_str=f"{mom_pct:+.1f}%" if isinstance(mom_pct,(int,float)) else "-"
        yoy_str=f"{yoy_pct:+.1f}%" if isinstance(yoy_pct,(int,float)) else "-"
        lines.append(f"| {acct} | {cur_str} | {mom_str} | {yoy_str} |")
    lines.append("")
    # 異常値アラート
    if anomalies:
        lines.append("## 2. 異常値アラート\n")
        lines.append(f"以下の{len(anomalies)}件の科目で、通常より大きな変動が検出されました。\n")
        for a in anomalies:
            lines.append(f"- {a['severity']} **{a['科目']}**（{a['種別']}）: {a['変動率']} {a['方向']}（{a.get('当月','')} / {a.get('前月',a.get('前年同月',''))}）")
        lines.append("")
    else:
        lines.append("## 2. 異常値アラート\n\n大きな変動は検出されませんでした。\n")
    # コメント
    lines.append("## 3. 所見・コメント\n")
    if anomalies:
        top=anomalies[0]
        lines.append(f"今月の注目点は**{top['科目']}**の{top['方向']}（{top['変動率']}）です。")
        if len(anomalies)==1:
            lines.append("他の科目は概ね安定しています。上記1件の原因確認をお勧めします。\n")
        elif len(anomalies)<=3:
            accts=", ".join([a['科目'] for a in anomalies[:3]])
            lines.append(f"加えて、{accts} で通常より大きな変動があります。各科目の原因確認を優先してください。\n")
        else:
            lines.append(f"今月は**{len(anomalies)}件**の異常値が検出されており、全体的に変動が大きい月です。")
            lines.append("特に経費科目の増加傾向がないか、前年同月比も合わせてご確認ください。\n")
    else:
        lines.append("今月は大きな変動は見られず、概ね安定した推移です。")
        lines.append("引き続き現在の施策を維持いただければ問題ありません。\n")
    lines.append("---\n")
    lines.append(f"*本レポートはAI経営パートナーの月次レポート自動生成ツールで作成されました。*")
    return "\n".join(lines)

# === Page Config ===
st.set_page_config(page_title="月次レポート自動生成",page_icon="📊",layout="wide",initial_sidebar_state="expanded")

# === Custom CSS ===
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    text-align: center;
}
.hero-section h1 {
    color: white;
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.hero-section p {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin: 0;
}
.kpi-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-card h3 {
    color: #64748b;
    font-size: 0.85rem;
    margin-bottom: 0.3rem;
}
.kpi-card .value {
    color: #1e293b;
    font-size: 1.5rem;
    font-weight: bold;
}
.kpi-card .delta-pos { color: #16a34a; font-size: 0.9rem; }
.kpi-card .delta-neg { color: #dc2626; font-size: 0.9rem; }
.section-divider {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #2563EB, #e2e8f0);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# === Session State ===
for k,v in {"df_cur":None,"df_prev":None,"loaded":False,"client_name":"株式会社サンプル商事"}.items():
    if k not in st.session_state: st.session_state[k]=v

# === Auto-load sample data ===
if not st.session_state.loaded:
    p_cur=os.path.join(os.path.dirname(__file__),"sample_data","trial_balance_current.csv")
    p_prev=os.path.join(os.path.dirname(__file__),"sample_data","trial_balance_prev.csv")
    if os.path.exists(p_cur): st.session_state.df_cur=load_csv(p_cur)
    if os.path.exists(p_prev): st.session_state.df_prev=load_csv(p_prev)
    st.session_state.loaded=True

# === Sidebar ===
st.sidebar.markdown("# 📊 月次レポート自動生成")
st.sidebar.markdown("**freee/MF試算表CSVから自動でレポートを作成**")
st.sidebar.markdown("---")

# サイドバー: 使い方ガイド
st.sidebar.markdown("### 📖 使い方ガイド")
st.sidebar.markdown("""
**Step 1**: 当期CSVアップロード（必須）
**Step 2**: 前期CSVアップロード（任意・YoY比較用）
**Step 3**: 対象月を選択してレポート生成
""")
st.sidebar.markdown("""
<details><summary>📄 CSVフォーマット</summary>

列名例:
`年月, 売上高, 売上原価, 売上総利益, 販売管理費計, 営業利益, 経常利益`

- 1行目: ヘッダー（列名）
- 2行目以降: 月次データ（万円単位）
- 年月列の形式: `2025-04` など

</details>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("📁 当期データ")
up_cur=st.sidebar.file_uploader("当期試算表CSV",type=["csv"],key="up_cur")
if up_cur:
    df=load_csv(up_cur)
    if df is not None: st.session_state.df_cur=df; st.sidebar.success(f"✅ {len(df)}行読込")
st.sidebar.subheader("📁 前期データ（任意）")
up_prev=st.sidebar.file_uploader("前期試算表CSV",type=["csv"],key="up_prev")
if up_prev:
    df=load_csv(up_prev)
    if df is not None: st.session_state.df_prev=df; st.sidebar.success(f"✅ {len(df)}行読込")
st.sidebar.markdown("---")
client_name=st.sidebar.text_input("顧問先名",value=st.session_state.client_name)
st.session_state.client_name=client_name
st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("月次レポート自動生成 v1.1")

# === Main: Hero Section ===
st.markdown("""
<div class="hero-section">
<h1>📊 月次レポート自動生成</h1>
<p>freee/MFの試算表CSVをアップロードするだけで、<br>前月比・前年同月比・異常値検知を自動実行します。</p>
</div>
""", unsafe_allow_html=True)

st.info("💡 **導入効果**: レポート作成時間 **3時間→15分**（年間約120時間の工数削減、約¥180万相当）")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

if st.session_state.df_cur is not None:
    df_cur=st.session_state.df_cur
    df_prev=st.session_state.df_prev
    # 月選択
    months_list=df_cur["年月"].tolist() if "年月" in df_cur.columns else []
    if months_list:
        sel_month=st.selectbox("📅 レポート対象月を選択",months_list,index=len(months_list)-1)
        sel_idx=months_list.index(sel_month)
        report_month=sel_month
    else:
        sel_idx=len(df_cur)-1; report_month="最新月"

    # KPIサマリーカード
    row=df_cur.iloc[sel_idx]
    kc1,kc2,kc3,kc4=st.columns(4)
    prev_row=df_cur.iloc[sel_idx-1] if sel_idx>0 else None
    for col_widget,acct in zip([kc1,kc2,kc3,kc4],["売上高","売上総利益","営業利益","経常利益"]):
        if acct in df_cur.columns:
            val=float(row[acct]); delta=None; delta_val=0
            if prev_row is not None and acct in df_cur.columns:
                pv=float(prev_row[acct])
                if pv!=0:
                    delta_val=(val-pv)/abs(pv)*100
                    delta=f"{delta_val:+.1f}%"
            col_widget.metric(acct,f"¥{val:,.0f}万",delta)

    # === 利益率指標（粗利率・営業利益率・販管費率）===
    def _safe_rate(numerator_acct, denominator_acct, r):
        """安全に比率を算出（%単位）"""
        if numerator_acct in df_cur.columns and denominator_acct in df_cur.columns:
            denom=float(r[denominator_acct])
            if denom!=0:
                return float(r[numerator_acct])/denom*100
        return None

    gross_margin=_safe_rate("売上総利益","売上高",row)
    op_margin=_safe_rate("営業利益","売上高",row)
    sga_ratio=_safe_rate("販売管理費計","売上高",row)

    gross_margin_prev=_safe_rate("売上総利益","売上高",prev_row) if prev_row is not None else None
    op_margin_prev=_safe_rate("営業利益","売上高",prev_row) if prev_row is not None else None
    sga_ratio_prev=_safe_rate("販売管理費計","売上高",prev_row) if prev_row is not None else None

    rc1,rc2,rc3=st.columns(3)
    for col_w,label,cur_val,prev_val in [
        (rc1,"粗利率",gross_margin,gross_margin_prev),
        (rc2,"営業利益率",op_margin,op_margin_prev),
        (rc3,"販管費率",sga_ratio,sga_ratio_prev),
    ]:
        if cur_val is not None:
            delta_str=None
            if prev_val is not None:
                diff=cur_val-prev_val
                delta_str=f"{diff:+.1f}pp"
            col_w.metric(label,f"{cur_val:.1f}%",delta_str,
                         delta_color="inverse" if label=="販管費率" else "normal")
        else:
            col_w.metric(label,"N/A",None)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 分析実行（選択月ベース）
    df_cur_to=df_cur.iloc[:sel_idx+1]
    mom=calc_mom(df_cur_to)
    yoy=calc_yoy(df_cur_to,df_prev) if df_prev is not None else {}
    anomalies=detect_anomalies(mom,yoy)
    # 異常値科目セットを作成（グラフハイライト用）
    anomaly_accounts=set(a["科目"] for a in anomalies)
    report_md=generate_report_md(df_cur_to,df_prev,mom,yoy,anomalies,client_name,report_month)

    # === 冒頭インサイト1行 ===
    insight_parts=[]
    if op_margin is not None:
        if op_margin_prev is not None and op_margin>op_margin_prev:
            insight_parts.append(f"営業利益率が{op_margin:.1f}%に改善")
        elif op_margin_prev is not None and op_margin<op_margin_prev:
            insight_parts.append(f"営業利益率が{op_margin:.1f}%に悪化")
        else:
            insight_parts.append(f"営業利益率は{op_margin:.1f}%")
    sales_mom=mom.get("売上高",{})
    if sales_mom:
        sales_pct=sales_mom.get("pct",0)
        if sales_pct>0:
            # 売上原価が連動増加しているか確認
            cost_mom=mom.get("売上原価",{})
            if cost_mom and cost_mom.get("pct",0)>0:
                insight_parts.append(f"売上成長+{sales_pct:.1f}%を牽引したのは取引量増加")
            else:
                insight_parts.append(f"売上は前月比+{sales_pct:.1f}%の成長")
        elif sales_pct<0:
            insight_parts.append(f"売上は前月比{sales_pct:.1f}%")
    if insight_parts:
        insight_msg="📊 今月の注目: "+"。".join(insight_parts)
        if op_margin is not None and op_margin_prev is not None and op_margin<op_margin_prev:
            st.warning(insight_msg)
        else:
            st.info(insight_msg)

    # タブ
    tab1,tab2,tab3,tab4=st.tabs(["📋 レポートプレビュー","📈 月次推移グラフ","⚠️ 異常値アラート","📊 データプレビュー"])

    with tab1:
        st.markdown(report_md)
        st.download_button("📥 レポートをダウンロード（Markdown）",report_md,
            f"月次レポート_{report_month}.md","text/markdown",use_container_width=True)

    with tab2:
        st.header("📈 主要科目 月次推移")
        setup_japanese_font()
        months=df_cur["年月"].tolist()
        for acct in KEY_ACCOUNTS:
            if acct in df_cur.columns:
                fig,ax=plt.subplots(figsize=(10,3.5))
                vals_cur=df_cur[acct].values.astype(float)
                # 選択月ハイライト: 選択月は別色、それ以外は通常色
                bar_colors=["#f97316" if i==sel_idx else "#2563EB" for i in range(len(months))]
                bar_alphas=[1.0 if i==sel_idx else 0.7 for i in range(len(months))]
                bars=ax.bar(range(len(months)),vals_cur,color=bar_colors,alpha=0.85,label="当期")
                # 選択月のバーだけアルファ調整
                for i,b in enumerate(bars):
                    b.set_alpha(bar_alphas[i])
                if df_prev is not None and acct in df_prev.columns:
                    vals_prev=df_prev[acct].values.astype(float)
                    n=min(len(vals_cur),len(vals_prev))
                    ax.plot(range(n),vals_prev[:n],color="#94A3B8",linewidth=2.5,
                        marker="o",markersize=5,label="前期",ls="--",alpha=0.9)
                # 異常値科目は赤タイトル
                title_color="#dc2626" if acct in anomaly_accounts else "#1e293b"
                title_prefix="⚠ " if acct in anomaly_accounts else ""
                ax.set_title(f"{title_prefix}{acct}",fontsize=13,fontweight="bold",color=title_color)
                ax.set_xticks(range(len(months)))
                ax.set_xticklabels([m[-3:] if len(m)>=3 else m for m in months],fontsize=9)
                ax.set_ylabel("万円")
                ax.legend(loc="upper left",framealpha=0.9)
                ax.grid(axis="y",alpha=0.3,linestyle="--")
                ax.set_axisbelow(True)
                plt.tight_layout()
                st.pyplot(fig); plt.close(fig)

    with tab3:
        st.header("⚠️ 異常値アラート")
        st.markdown(f"前月比・前年同月比で**{int(ANOMALY_THRESHOLD*100)}%以上の変動**があった科目を表示します。")
        if anomalies:
            st.warning(f"**{len(anomalies)}件**の異常値が検出されました。")
            adf=pd.DataFrame(anomalies)
            show_cols=[c for c in ["severity","科目","種別","変動率","方向","当月","前月","前年同月","差額","推定原因","推奨アクション"] if c in adf.columns]
            st.dataframe(adf[show_cols],use_container_width=True,hide_index=True)
            # 異常値CSVダウンロード
            anomaly_csv=adf[show_cols].to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 異常値一覧をCSVダウンロード",anomaly_csv,
                f"異常値アラート_{report_month}.csv","text/csv",use_container_width=True)
        else:
            st.success("異常値は検出されませんでした。")

    with tab4:
        st.header("📊 データプレビュー")
        st.subheader("当期データ")
        st.dataframe(df_cur,use_container_width=True)
        cur_csv=df_cur.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 当期データをCSVダウンロード",cur_csv,
            "当期データ.csv","text/csv",use_container_width=True,key="dl_cur")
        if df_prev is not None:
            st.subheader("前期データ")
            st.dataframe(df_prev,use_container_width=True)
            prev_csv=df_prev.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 前期データをCSVダウンロード",prev_csv,
                "前期データ.csv","text/csv",use_container_width=True,key="dl_prev")
else:
    st.info("サイドバーから試算表CSVをアップロードしてください。\n\nデモデータが自動で読み込まれている場合は、そのままご利用いただけます。")

# フッター: 関連ツールカード（3列）
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1,fc2,fc3=st.columns(3)
fc1.markdown("🔴 **入金遅延アラート**  \n入金遅延を自動検知・催促  \n[▶ ツールを開く](https://shigyou-payment.streamlit.app)")
fc2.markdown("🏢 **離反予測**  \n顧問先の離反リスクをAI予測  \n[▶ ツールを開く](https://shigyou-churn.streamlit.app)")
fc3.markdown("🏠 **士業ポータル**  \nAI経営パートナー総合メニュー  \n[▶ ツールを開く](https://shigyou-ai-tools.streamlit.app)")
st.caption("AI経営パートナー × データサイエンス | 月次レポート自動生成 v1.1")
