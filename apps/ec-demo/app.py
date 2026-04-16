"""
EC向け 顧客離脱予測＋需要予測デモアプリ
=======================================
MVP #2: LightGBM分類(離脱) + LightGBM回帰(需要) + SHAP + 逆SHAP
"""
import streamlit as st
import pandas as pd
import numpy as np
import warnings, sys, os
warnings.filterwarnings("ignore")
if not sys.warnoptions:
    warnings.simplefilter("ignore")
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             roc_auc_score, f1_score, precision_score, recall_score,
                             confusion_matrix, roc_curve)
import shap
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Dict, List, Optional

# === Utilities ===
def setup_japanese_font():
    for f in ["Noto Sans CJK JP","Noto Sans JP","Yu Gothic","MS Gothic","Meiryo","DejaVu Sans"]:
        if f in [x.name for x in fm.fontManager.ttflist]:
            plt.rcParams["font.family"]=f; plt.rcParams["font.sans-serif"]=[f]; plt.rcParams["axes.unicode_minus"]=False; return f
    plt.rcParams["font.family"]="sans-serif"; plt.rcParams["axes.unicode_minus"]=False; return None
_font=setup_japanese_font()

def load_file(uf):
    if uf is None: return None
    try:
        if uf.name.endswith(".csv"): return pd.read_csv(uf)
        elif uf.name.endswith((".xlsx",".xls")): return pd.read_excel(uf)
    except Exception as e: st.error(f"読み込みエラー: {e}")
    return None

def display_data_info(df,name="データ"):
    c1,c2,c3=st.columns(3); c1.metric("行数",f"{len(df):,}"); c2.metric("列数",f"{len(df.columns):,}"); c3.metric("欠損値",f"{df.isnull().sum().sum():,}")

def preprocess_data(df,target_col=None,label_encoders=None,is_training=True):
    dp=df.copy()
    if label_encoders is None: label_encoders={}
    for col in dp.columns:
        if target_col and col==target_col: continue
        if dp[col].dtype=="object" or dp[col].dtype.name=="category":
            if is_training:
                if col not in label_encoders:
                    label_encoders[col]=LabelEncoder(); v=dp[col].astype(str).fillna("__NA__")
                    dp[col]=pd.Series(label_encoders[col].fit_transform(v),index=dp.index,dtype="int64")
            else:
                if col in label_encoders:
                    dp[col]=dp[col].astype(str).fillna("__NA__"); k=set(label_encoders[col].classes_)
                    dp[col]=dp[col].apply(lambda x: label_encoders[col].transform([x])[0] if x in k else -1)
    return dp,label_encoders

def split_data(df,target_col,test_size=0.2,random_state=42):
    X=df.drop(columns=[target_col]).reset_index(drop=True); y=df[target_col].reset_index(drop=True)
    Xv,yv=X.values.copy(),y.values.copy()
    Xtr,Xte,ytr,yte=train_test_split(Xv,yv,test_size=test_size,random_state=random_state,stratify=yv if len(set(yv))<=20 else None)
    return (pd.DataFrame(Xtr,columns=X.columns),pd.DataFrame(Xte,columns=X.columns),pd.Series(ytr,name=y.name),pd.Series(yte,name=y.name))

def calculate_shap_values(model,X,max_samples=500):
    Xs=X.sample(n=min(max_samples,len(X)),random_state=42) if len(X)>max_samples else X.copy()
    ex=shap.TreeExplainer(model); return ex.shap_values(Xs),Xs

def get_feature_importance(sv,fnames):
    vals=sv[1] if isinstance(sv,list) else sv
    imp=np.abs(vals).mean(axis=0)
    return pd.DataFrame({"特徴量":fnames,"重要度":imp}).sort_values("重要度",ascending=False).reset_index(drop=True)

# === EC ACTION_TEMPLATES ===
ACTION_TEMPLATES={
    "直近購入からの経過日数":(None,"購入後30日経過した顧客にリマインドメールを送信する",7),
    "過去90日購入回数":("次回購入で使える限定クーポン（¥500）をメールで配布する",None,1),
    "直近30日ログイン回数":("新着商品のプッシュ通知を週1回配信する",None,1),
    "メール開封率":("メール件名をパーソナライズし、配信時間を最適化する",None,5),
    "カート放棄回数":(None,"カート放棄から1時間以内にリマインドメールを自動送信する",1),
    "問い合わせ回数":(None,"FAQ充実+チャットボット導入でCS負荷を軽減する",1),
    "決済失敗回数":(None,"決済失敗時にSMS+メールで別決済手段をご案内する",1),
    "クーポン利用率":("購入履歴に基づくパーソナライズクーポンを発行する",None,5),
    "購入カテゴリ数":("未購入カテゴリのおすすめ商品をレコメンドメールで紹介する",None,1),
    "直近レビュー投稿からの日数":(None,"購入後7日にレビュー依頼メール（ポイント付与）を送信する",30),
    "累計購入金額":("VIP向けロイヤルティプログラム（ポイント2倍・限定セール招待）を案内する",None,0),
    "平均注文単価":("関連商品のバンドルセット（10%OFF）をカート画面でレコメンドする",None,0),
    "会員歴月数":(None,None,0),"流入チャネル":(None,None,0),
}

def compute_feature_stats(df,fnames):
    s={}
    for c in fnames:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            s[c]={"mean":float(df[c].mean()),"median":float(df[c].median()),"q25":float(df[c].quantile(0.25)),"q75":float(df[c].quantile(0.75))}
    return s

def generate_action_suggestions(model,X,fnames,fstats,top_n=5):
    ex=shap.TreeExplainer(model); sv=ex.shap_values(X)
    # For binary classifier, sv is list of [class0, class1] — use class1 (churn)
    sr=sv[1][0] if isinstance(sv,list) else sv[0]
    dr=X.iloc[0]
    sorted_idx=np.argsort(-sr)  # highest SHAP = most pushing toward churn
    suggestions=[]
    for fi in sorted_idx:
        if len(suggestions)>=top_n: break
        impact=float(sr[fi])
        if impact<=0: continue
        fn=fnames[fi]; cur=dr.iloc[fi]
        tmpl=ACTION_TEMPLATES.get(fn)
        if not isinstance(cur,(int,float,np.integer,np.floating)):
            if tmpl and (tmpl[0] or tmpl[1]):
                suggestions.append({"feature":fn,"current":str(cur),"target":"要検討","action":tmpl[0] or tmpl[1],"detail":f"推定効果: 離脱確率 -{impact:.2f}","impact":round(impact,3),"effort":"低"})
            continue
        cv=float(cur); stats=fstats.get(fn,{}); median=stats.get("median",cv)
        if tmpl:
            step=tmpl[2]
            if step==0:
                if tmpl[0] or tmpl[1]:
                    action_text=tmpl[0] or tmpl[1]
                    suggestions.append({"feature":fn,"current":round(cv,2),"target":"施策実行","action":action_text,
                        "detail":f"推定効果: 離脱確率 -{impact:.2f}","impact":round(impact,3),"effort":"中"})
                continue
            if cv>median and tmpl[1]: action_text=tmpl[1]; target=round(cv-step,2)
            elif cv<=median and tmpl[0]: action_text=tmpl[0]; target=round(cv+step,2)
            elif tmpl[1]: action_text=tmpl[1]; target=round(cv-step,2)
            elif tmpl[0]: action_text=tmpl[0]; target=round(cv+step,2)
            else: continue
        else:
            step=max(abs(cv*0.1),0.5)
            target=round(cv-step,2) if cv>median else round(cv+step,2)
            action_text=f"「{fn}」を {cv:.1f} → {target:.1f} に改善する"
        if abs(target-cv)<0.01: continue
        suggestions.append({"feature":fn,"current":round(cv,2),"target":target,"action":action_text,
            "detail":f"{fn}: {cv:.1f} → {target:.1f}（推定効果: 離脱確率 -{impact:.2f}）","impact":round(impact,3),"effort":"低" if tmpl else "中"})
    return suggestions

# === Page Config ===
st.set_page_config(page_title="EC顧客離脱予測AI",page_icon="🛒",layout="wide",initial_sidebar_state="expanded")
TARGET_COL="90日以内離脱"
CHURN_TH=0.5

# === Session State ===
for k,v in {"churn_model":None,"churn_trained":False,"churn_le":None,"churn_feat":None,
    "churn_metrics":None,"churn_df":None,"churn_Xte":None,"churn_yte":None,
    "churn_sv":None,"churn_Xs":None,"churn_stats":None,"churn_probs":None,
    "demand_model":None,"demand_trained":False,"demand_le":None,"demand_metrics":None,"demand_df":None,
    "demand_Xte":None,"demand_yte":None,"demand_yp":None,
    "using_default":False,"default_loaded":False}.items():
    if k not in st.session_state: st.session_state[k]=v

def _train_churn(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fc=[c for c in df.columns if c not in [TARGET_COL,"顧客ID"]]
        dw=df.drop(columns=["顧客ID"],errors="ignore")
        dp,le=preprocess_data(dw.copy(),TARGET_COL,is_training=True)
        Xtr,Xte,ytr,yte=split_data(dp.copy(),TARGET_COL)
        m=lgb.LGBMClassifier(n_estimators=100,learning_rate=0.1,max_depth=6,random_state=42,verbose=-1,force_col_wise=True)
        m.fit(Xtr,ytr)
        yp=m.predict_proba(Xte)[:,1]
        auc=roc_auc_score(yte,yp); ypc=(yp>=CHURN_TH).astype(int)
        metrics={"AUC":auc,"F1":f1_score(yte,ypc),"Precision":precision_score(yte,ypc,zero_division=0),"Recall":recall_score(yte,ypc,zero_division=0)}
        sv,Xs=calculate_shap_values(m,Xte)
        stats=compute_feature_stats(dw,fc)
        st.session_state.update({"churn_model":m,"churn_le":le,"churn_trained":True,"churn_feat":fc,
            "churn_Xte":Xte,"churn_yte":yte,"churn_metrics":metrics,"churn_sv":sv,"churn_Xs":Xs,"churn_stats":stats,"churn_probs":yp})

def _train_demand(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tc="販売数量"
        drop_cols=[tc,"日付","SKU","売上金額","単価"]
        fc=[c for c in df.columns if c not in drop_cols]
        dw=df.drop(columns=["日付","SKU"],errors="ignore")
        dp,le=preprocess_data(dw.copy(),tc,is_training=True)
        # Time-based split (last 20%)
        dp=dp.sort_index()
        n=int(len(dp)*0.8)
        Xtr=dp.iloc[:n].drop(columns=[tc]+["売上金額","単価"],errors="ignore")
        yte_full=dp.iloc[n:]
        Xte=yte_full.drop(columns=[tc]+["売上金額","単価"],errors="ignore")
        ytr=dp.iloc[:n][tc]; yte=yte_full[tc]
        # Align columns
        common=Xtr.columns.intersection(Xte.columns)
        Xtr=Xtr[common]; Xte=Xte[common]
        m=lgb.LGBMRegressor(n_estimators=100,learning_rate=0.1,max_depth=6,random_state=42,verbose=-1,force_col_wise=True)
        m.fit(Xtr,ytr); yp=m.predict(Xte)
        metrics={"MAE":mean_absolute_error(yte,yp),"RMSE":np.sqrt(mean_squared_error(yte,yp)),"R2":r2_score(yte,yp)}
        st.session_state.update({"demand_model":m,"demand_trained":True,"demand_le":le,"demand_metrics":metrics,"demand_Xte":Xte,"demand_yte":yte,"demand_yp":yp})

# Auto-load
if not st.session_state.default_loaded:
    p1=os.path.join(os.path.dirname(__file__),"sample_data","ec_customers_train.csv")
    p2=os.path.join(os.path.dirname(__file__),"sample_data","ec_sales_train.csv")
    try:
        if os.path.exists(p1):
            df1=pd.read_csv(p1); st.session_state.churn_df=df1; st.session_state.using_default=True; _train_churn(df1)
        if os.path.exists(p2):
            df2=pd.read_csv(p2); st.session_state.demand_df=df2; _train_demand(df2)
    except Exception: pass
    st.session_state.default_loaded=True

# === Sidebar ===
st.sidebar.markdown("# 🛒 EC顧客離脱予測AI")
st.sidebar.markdown("**小売/EC事業者向けデモ**")
st.sidebar.markdown("---")
if st.session_state.using_default:
    st.sidebar.info("💡 デモデータ（1,000顧客）で自動学習済み。\n独自データのアップロードも可能です。")
st.sidebar.subheader("📁 顧客データ")
up1=st.sidebar.file_uploader("顧客離脱予測用CSV",type=["csv","xlsx","xls"],key="up1")
if up1:
    ndf=load_file(up1)
    if ndf is not None and TARGET_COL in ndf.columns:
        st.session_state.churn_df=ndf; st.session_state.using_default=False; st.sidebar.success(f"✅ {len(ndf)}件読込")
st.sidebar.subheader("📁 売上データ")
up2=st.sidebar.file_uploader("需要予測用CSV",type=["csv","xlsx","xls"],key="up2")
if up2:
    ndf2=load_file(up2)
    if ndf2 is not None and "販売数量" in ndf2.columns:
        st.session_state.demand_df=ndf2; st.sidebar.success(f"✅ {len(ndf2)}件読込")
st.sidebar.markdown("---")
if st.session_state.churn_df is not None:
    if st.sidebar.button("🔄 再学習" if st.session_state.churn_trained else "▶️ 学習",type="primary",use_container_width=True):
        with st.spinner("学習中..."):
            _train_churn(st.session_state.churn_df)
            if st.session_state.demand_df is not None: _train_demand(st.session_state.demand_df)
        st.sidebar.success("✅ 学習完了")
if st.session_state.churn_trained and st.session_state.churn_df is not None:
    st.sidebar.markdown("---"); st.sidebar.subheader("📊 ビジネスKPI")
    _df_kpi=st.session_state.churn_df.copy(); _m_kpi=st.session_state.churn_model; _le_kpi=st.session_state.churn_le
    _dw_kpi=_df_kpi.drop(columns=["顧客ID","90日以内離脱"],errors="ignore")
    _dp_kpi,_=preprocess_data(_dw_kpi.copy(),target_col=None,label_encoders=_le_kpi,is_training=False)
    _probs_kpi=_m_kpi.predict_proba(_dp_kpi)[:,1]
    _n_high=(_probs_kpi>=0.7).sum()
    _avg_ltv=_df_kpi["累計購入金額"].mean() if "累計購入金額" in _df_kpi.columns else 50000
    _est_loss=_n_high*_avg_ltv
    st.sidebar.metric("🔴 高リスク顧客",f"{_n_high}人")
    st.sidebar.metric("推定年間離脱損失",f"¥{_est_loss:,.0f}")
    st.sidebar.metric("L2サービス ROI",f"{_est_loss/(120000*12):.1f}倍",help="年間¥144万のサービス費用に対する回収倍率")
st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("MVP #2 — EC向け離脱予測デモ v0.2")

# === Main ===
st.title("🛒 EC顧客離脱予測AI")
st.markdown("LightGBM + SHAP + **逆SHAP** で、顧客の離脱リスクを予測し、**「何を変えれば離脱を防げるか」**を具体的に提案します。")
tab1,tab2,tab3,tab4,tab5,tab6,tab7=st.tabs(["📊 離脱リスク一覧","📈 売上/需要予測","📉 モデル評価","🔍 SHAP要因分析","💡 逆SHAP改善提案","📦 在庫ABC分析","📋 データプレビュー"])

# === Tab1: Churn Risk List ===
with tab1:
    st.header("顧客 離脱リスク一覧")
    if st.session_state.churn_trained and st.session_state.churn_df is not None:
        df=st.session_state.churn_df.copy(); m=st.session_state.churn_model; le=st.session_state.churn_le; fc=st.session_state.churn_feat
        dw=df.drop(columns=["顧客ID",TARGET_COL],errors="ignore")
        dp,_=preprocess_data(dw.copy(),target_col=None,label_encoders=le,is_training=False)
        probs=m.predict_proba(dp)[:,1]; df["離脱確率"]=np.round(probs,3)
        def _risk(p):
            if p>=0.7: return "🔴 高リスク"
            if p>=0.4: return "🟡 中リスク"
            return "🟢 低リスク"
        df["リスクレベル"]=df["離脱確率"].apply(_risk)
        ds=df.sort_values("離脱確率",ascending=False).reset_index(drop=True)
        nh=(ds["離脱確率"]>=0.7).sum(); nm=((ds["離脱確率"]>=0.4)&(ds["離脱確率"]<0.7)).sum(); nl=(ds["離脱確率"]<0.4).sum()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("全顧客数",f"{len(df):,}人"); c2.metric("🔴 高リスク",f"{nh:,}人"); c3.metric("🟡 中リスク",f"{nm:,}人"); c4.metric("🟢 低リスク",f"{nl:,}人")
        st.markdown("---"); st.subheader("🔴 離脱リスク TOP10")
        def _top_action(row):
            try:
                rf=row.drop(labels=["顧客ID","90日以内離脱","離脱確率","リスクレベル"],errors="ignore").to_frame().T
                rp,_=preprocess_data(rf.copy(),target_col=None,label_encoders=le,is_training=False)
                sugs=generate_action_suggestions(m,rp,fc,st.session_state.churn_stats,top_n=1)
                return sugs[0]["action"] if sugs else "—"
            except: return "—"
        top10=ds.head(10).copy(); top10["推奨アクション"]=top10.apply(_top_action,axis=1)
        show=["顧客ID","リスクレベル","離脱確率","推奨アクション","直近購入からの経過日数","過去90日購入回数"]
        show=[c for c in show if c in top10.columns]
        st.dataframe(top10[show],use_container_width=True,hide_index=True)
        st.markdown("---"); st.subheader("離脱確率分布")
        setup_japanese_font(); fig,ax=plt.subplots(figsize=(10,4))
        ax.hist(df["離脱確率"],bins=30,color="#10B981",alpha=0.7,edgecolor="white")
        ax.axvline(0.7,color="red",ls="--",label="高リスク(70%)"); ax.axvline(0.4,color="orange",ls="--",label="中リスク(40%)")
        ax.set_xlabel("離脱確率"); ax.set_ylabel("顧客数"); ax.legend(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        csv=ds.to_csv(index=False,encoding="utf-8-sig")
        st.download_button("📥 リスク一覧CSV",csv,"ec_risk_list.csv","text/csv",use_container_width=True)
    else: st.info("モデルを学習するとリスク一覧が表示されます")

# === Tab2: Demand Forecast ===
with tab2:
    st.header("売上/需要予測")
    if st.session_state.demand_trained and st.session_state.demand_df is not None:
        ddf=st.session_state.demand_df
        st.markdown(f"**{ddf['SKU'].nunique()} SKU × {ddf['日付'].nunique()} 日間**の販売データで学習済み（目的変数: 販売数量）")
        dm=st.session_state.demand_metrics
        c1,c2,c3=st.columns(3)
        c1.metric("MAE",f"{dm['MAE']:.1f} 個"); c2.metric("RMSE",f"{dm['RMSE']:.1f} 個"); c3.metric("R²",f"{dm['R2']:.3f}")
        if st.session_state.demand_yte is not None and st.session_state.demand_yp is not None:
            st.markdown("---"); st.subheader("📈 実績 vs 予測（テスト期間）")
            setup_japanese_font()
            fig_d,ax_d=plt.subplots(figsize=(12,4))
            n_show=min(200,len(st.session_state.demand_yte))
            ax_d.plot(range(n_show),st.session_state.demand_yte.values[:n_show],label="実績",alpha=0.7,color="#10B981")
            ax_d.plot(range(n_show),st.session_state.demand_yp[:n_show],label="予測",alpha=0.7,color="#3B82F6",ls="--")
            ax_d.set_xlabel("テストデータ Index"); ax_d.set_ylabel("販売数量"); ax_d.legend(); plt.tight_layout(); st.pyplot(fig_d); plt.close(fig_d)
        st.markdown("---"); st.subheader("カテゴリ別 売上サマリー")
        cat_summary=ddf.groupby("カテゴリ").agg({"売上金額":["sum","mean","count"]}).round(0)
        cat_summary.columns=["合計売上","平均日次売上","データ件数"]
        cat_summary["合計売上"]=cat_summary["合計売上"].apply(lambda x:f"¥{x:,.0f}")
        cat_summary["平均日次売上"]=cat_summary["平均日次売上"].apply(lambda x:f"¥{x:,.0f}")
        st.dataframe(cat_summary,use_container_width=True)
        st.markdown("---"); st.subheader("📊 カテゴリ別 月次売上推移")
        setup_japanese_font()
        ddf_trend=ddf.copy(); ddf_trend["月次"]=pd.to_datetime(ddf_trend["日付"]).dt.to_period("M").astype(str)
        monthly=ddf_trend.groupby(["月次","カテゴリ"])["売上金額"].sum().unstack(fill_value=0)
        fig_trend,ax_trend=plt.subplots(figsize=(12,5))
        monthly.div(10000).plot(kind="bar",stacked=True,ax=ax_trend,alpha=0.8,colormap="Set2")
        ax_trend.set_ylabel("売上（万円）"); ax_trend.set_xlabel("月")
        ax_trend.legend(title="カテゴリ",bbox_to_anchor=(1.02,1),loc="upper left")
        plt.xticks(rotation=45); plt.tight_layout(); st.pyplot(fig_trend); plt.close(fig_trend)
    else: st.info("売上データを読み込むと需要予測が表示されます")

# === Tab3: Model Evaluation ===
with tab3:
    st.header("モデル評価指標")
    if st.session_state.churn_trained:
        st.subheader("🛒 離脱予測モデル（分類）")
        cm=st.session_state.churn_metrics
        c1,c2,c3,c4=st.columns(4)
        c1.metric("AUC",f"{cm['AUC']:.3f}",help="0.75以上で実用水準")
        c2.metric("F1",f"{cm['F1']:.3f}"); c3.metric("Precision",f"{cm['Precision']:.3f}"); c4.metric("Recall",f"{cm['Recall']:.3f}")
        if st.session_state.churn_probs is not None:
            st.markdown("---"); st.subheader("📊 混同行列")
            setup_japanese_font()
            yp_bin=(st.session_state.churn_probs>=CHURN_TH).astype(int)
            cm_mat=confusion_matrix(st.session_state.churn_yte,yp_bin)
            fig_cm,ax_cm=plt.subplots(figsize=(6,5))
            im=ax_cm.imshow(cm_mat,cmap="Blues")
            for i in range(2):
                for j in range(2):
                    total=cm_mat.sum()
                    ax_cm.text(j,i,f"{cm_mat[i,j]}\n({cm_mat[i,j]/total:.1%})",ha="center",va="center",fontsize=14,color="white" if cm_mat[i,j]>cm_mat.max()/2 else "black")
            ax_cm.set_xticks([0,1]); ax_cm.set_yticks([0,1])
            ax_cm.set_xticklabels(["継続","離脱"]); ax_cm.set_yticklabels(["継続","離脱"])
            ax_cm.set_xlabel("予測"); ax_cm.set_ylabel("実際")
            plt.colorbar(im,ax=ax_cm); plt.tight_layout(); st.pyplot(fig_cm); plt.close(fig_cm)
            fn_count=cm_mat[1,0]
            st.caption(f"⚠️ FN（見逃し）: {fn_count}人 — 実際に離脱する顧客をモデルが見逃した数。1人あたり平均LTVを¥5万とすると、約¥{fn_count*5:,}万の機会損失リスク。")
            st.markdown("---"); st.subheader("📈 ROC曲線")
            fpr,tpr,thresholds=roc_curve(st.session_state.churn_yte,st.session_state.churn_probs)
            fig_roc,ax_roc=plt.subplots(figsize=(7,5))
            ax_roc.plot(fpr,tpr,color="#10B981",lw=2,label=f"ROC曲線 (AUC={cm['AUC']:.3f})")
            ax_roc.plot([0,1],[0,1],color="gray",ls="--",lw=1,label="ランダム")
            idx_05=np.argmin(np.abs(thresholds-0.5))
            ax_roc.scatter([fpr[idx_05]],[tpr[idx_05]],color="red",s=100,zorder=5,label=f"閾値=0.5 (FPR={fpr[idx_05]:.2f}, TPR={tpr[idx_05]:.2f})")
            ax_roc.set_xlabel("偽陽性率 (FPR)"); ax_roc.set_ylabel("真陽性率 (TPR)")
            ax_roc.legend(loc="lower right"); ax_roc.set_title("ROC曲線 — 離脱予測モデル")
            plt.tight_layout(); st.pyplot(fig_roc); plt.close(fig_roc)
    if st.session_state.demand_trained:
        st.markdown("---"); st.subheader("📈 需要予測モデル（回帰）")
        dm=st.session_state.demand_metrics
        c1,c2,c3=st.columns(3)
        c1.metric("MAE",f"{dm['MAE']:.1f} 個"); c2.metric("RMSE",f"{dm['RMSE']:.1f} 個"); c3.metric("R²",f"{dm['R2']:.3f}")
    if not st.session_state.churn_trained: st.info("モデルを学習すると評価指標が表示されます")

# === Tab4: SHAP ===
with tab4:
    st.header("SHAP要因分析")
    st.markdown("**「なぜこの顧客は離脱しそうか？」**を可視化します。")
    if st.session_state.churn_trained and st.session_state.churn_sv is not None:
        sv=st.session_state.churn_sv; Xs=st.session_state.churn_Xs
        sv_c1=sv[1] if isinstance(sv,list) else sv
        setup_japanese_font()
        st.subheader("📊 SHAP Summary Plot（離脱クラス）")
        st.caption("赤=値が高い、青=値が低い。右に寄るほど離脱確率を上げる要因。")
        fig1,_=plt.subplots(figsize=(10,8)); shap.summary_plot(sv_c1,Xs,max_display=14,show=False,plot_size=None); plt.tight_layout(); st.pyplot(fig1); plt.close("all")
        st.markdown("---"); st.subheader("📊 特徴量重要度")
        fig2,_=plt.subplots(figsize=(10,8)); shap.summary_plot(sv_c1,Xs,plot_type="bar",max_display=14,show=False,plot_size=None); plt.tight_layout(); st.pyplot(fig2); plt.close("all")
        st.markdown("---"); st.subheader("📋 特徴量重要度ランキング")
        imp=get_feature_importance(sv,Xs.columns.tolist()); st.dataframe(imp,use_container_width=True,hide_index=True)
    else: st.info("モデルを学習するとSHAP分析が表示されます")

# === Tab5: Reverse SHAP ===
with tab5:
    st.header("💡 逆SHAP改善提案")
    st.markdown("""
    | | 通常のSHAP | 逆SHAP |
    |---|---|---|
    | 問い | なぜ離脱しそうか？（Why） | **何を変えれば離脱を防げるか？（How）** |
    | 出力 | 要因の説明 | **具体的アクション提案** |
    """)
    if st.session_state.churn_trained and st.session_state.churn_df is not None:
        df=st.session_state.churn_df.copy(); m=st.session_state.churn_model; le=st.session_state.churn_le
        fc=st.session_state.churn_feat; stats=st.session_state.churn_stats
        dw=df.drop(columns=["顧客ID",TARGET_COL],errors="ignore")
        dp,_=preprocess_data(dw.copy(),target_col=None,label_encoders=le,is_training=False)
        probs=m.predict_proba(dp)[:,1]; df["離脱確率"]=np.round(probs,3)
        hr=df[df["離脱確率"]>=0.7].sort_values("離脱確率",ascending=False)
        if len(hr)==0: st.success("🎉 高リスク顧客は現在いません！")
        else:
            st.warning(f"🔴 **{len(hr):,}人** が高リスク（離脱確率70%以上）")
            cids=hr["顧客ID"].tolist(); sel=st.selectbox("改善提案を表示する顧客",cids)
            if sel:
                row=df[df["顧客ID"]==sel].iloc[0]
                st.markdown(f"### 顧客: **{sel}**")
                ic=st.columns(4)
                ic[0].metric("離脱確率",f"{row['離脱確率']:.1%}")
                ic[1].metric("経過日数",f"{int(row['直近購入からの経過日数'])}日")
                ic[2].metric("購入回数(90日)",f"{int(row['過去90日購入回数'])}回")
                ic[3].metric("累計購入額",f"¥{int(row['累計購入金額']):,}")
                st.markdown("---"); st.subheader("🎯 改善アクション提案")
                rf=dw[df["顧客ID"]==sel].copy()
                rp,_=preprocess_data(rf.copy(),target_col=None,label_encoders=le,is_training=False)
                sugs=generate_action_suggestions(m,rp,fc,stats,top_n=5)
                if sugs:
                    _avg_ltv=df["累計購入金額"].mean() if "累計購入金額" in df.columns else 50000
                    _n_hr=len(hr)
                    for i,s in enumerate(sugs,1):
                        eb={"低":"🟢 すぐできる","中":"🟡 少し工夫が必要"}.get(s.get("effort","中"),"🟡")
                        _est_rev=s['impact']*_n_hr*_avg_ltv/100
                        st.markdown(f"### 提案 {i}: {s['action']}"); st.caption(s.get("detail",""))
                        ca,cb,cc=st.columns(3); ca.metric("推定効果",f"-{s['impact']:.2f}"); cb.metric("現在値→目標値",f"{s['current']}→{s['target']}"); cc.metric("実行コスト",eb)
                        st.caption(f"💰 推定年間インパクト: 約 **¥{_est_rev:,.0f}**（高リスク{_n_hr}人 × 平均LTV ¥{_avg_ltv:,.0f} × 効果{s['impact']:.2f}）")
                        st.markdown("---")
                else: st.info("この顧客には改善提案を生成できませんでした。")
                st.subheader("📊 この顧客の要因分解")
                ex=shap.TreeExplainer(m); sv=ex.shap_values(rp)
                sv1=sv[1][0] if isinstance(sv,list) else sv[0]
                fdf=pd.DataFrame({"特徴量":fc,"SHAP値":np.round(sv1,3),"影響方向":["⬆️ 離脱促進" if v>0 else "⬇️ 離脱抑制" for v in sv1]}).sort_values("SHAP値",ascending=False).reset_index(drop=True)
                st.dataframe(fdf,use_container_width=True,hide_index=True)
    else: st.info("モデルを学習すると改善提案が表示されます")

# === Tab6: ABC Analysis ===
with tab6:
    st.header("📦 在庫ABC分析")
    st.markdown("SKU別の売上貢献度を**ABC分類**し、在庫最適化の優先度を可視化します。")
    if st.session_state.demand_df is not None:
        ddf_abc=st.session_state.demand_df
        sku_summary=ddf_abc.groupby(["SKU","カテゴリ"]).agg({"売上金額":"sum","販売数量":"sum"}).reset_index()
        sku_summary=sku_summary.sort_values("売上金額",ascending=False).reset_index(drop=True)
        total_sales=sku_summary["売上金額"].sum()
        sku_summary["売上構成比"]=sku_summary["売上金額"]/total_sales
        sku_summary["累積構成比"]=sku_summary["売上構成比"].cumsum()
        def _abc(cum):
            if cum<=0.70: return "A"
            if cum<=0.90: return "B"
            return "C"
        sku_summary["ABCランク"]=sku_summary["累積構成比"].apply(_abc)
        na=(sku_summary["ABCランク"]=="A").sum(); nb=(sku_summary["ABCランク"]=="B").sum(); nc=(sku_summary["ABCランク"]=="C").sum()
        sa=sku_summary[sku_summary["ABCランク"]=="A"]["売上金額"].sum()
        sb=sku_summary[sku_summary["ABCランク"]=="B"]["売上金額"].sum()
        sc=sku_summary[sku_summary["ABCランク"]=="C"]["売上金額"].sum()
        c1,c2,c3=st.columns(3)
        c1.metric("🅰️ Aランク",f"{na} SKU",f"売上の{sa/total_sales:.0%}を占める")
        c2.metric("🅱️ Bランク",f"{nb} SKU",f"売上の{sb/total_sales:.0%}")
        c3.metric("🅲 Cランク",f"{nc} SKU",f"売上の{sc/total_sales:.0%} — 最適化対象")
        holding_cost_rate=0.20
        c_rank_holding=sc*holding_cost_rate
        st.info(f"💡 **Cランク {nc}品目の在庫最適化で、年間約 ¥{c_rank_holding:,.0f} の在庫保持コスト削減余地**（在庫保持コスト率20%想定）")
        st.markdown("---"); st.subheader("📊 パレート図（ABC分析）")
        setup_japanese_font()
        fig_abc,ax_abc1=plt.subplots(figsize=(12,5))
        colors_abc={"A":"#10B981","B":"#F59E0B","C":"#EF4444"}
        bar_colors=[colors_abc[r] for r in sku_summary["ABCランク"]]
        ax_abc1.bar(range(len(sku_summary)),sku_summary["売上金額"]/10000,color=bar_colors,alpha=0.7)
        ax_abc1.set_ylabel("売上金額（万円）"); ax_abc1.set_xlabel("SKU（売上順）")
        ax_abc2=ax_abc1.twinx()
        ax_abc2.plot(range(len(sku_summary)),sku_summary["累積構成比"]*100,color="#1E40AF",linewidth=2,marker="o",markersize=3)
        ax_abc2.set_ylabel("累積構成比（%）")
        ax_abc2.axhline(70,color="#10B981",ls="--",alpha=0.5,label="70%（A/B境界）")
        ax_abc2.axhline(90,color="#F59E0B",ls="--",alpha=0.5,label="90%（B/C境界）")
        ax_abc2.legend(loc="center right"); ax_abc1.set_xticks([])
        plt.tight_layout(); st.pyplot(fig_abc); plt.close(fig_abc)
        st.markdown("---"); st.subheader("📋 SKU別ABC分類一覧")
        disp_abc=sku_summary.copy()
        disp_abc["売上金額"]=disp_abc["売上金額"].apply(lambda x:f"¥{x:,.0f}")
        disp_abc["売上構成比"]=disp_abc["売上構成比"].apply(lambda x:f"{x:.1%}")
        disp_abc["累積構成比"]=disp_abc["累積構成比"].apply(lambda x:f"{x:.1%}")
        st.dataframe(disp_abc[["SKU","カテゴリ","ABCランク","販売数量","売上金額","売上構成比","累積構成比"]],use_container_width=True,hide_index=True)
        st.markdown("---"); st.subheader("📊 カテゴリ別ABC構成")
        cat_abc=sku_summary.groupby(["カテゴリ","ABCランク"]).size().unstack(fill_value=0)
        st.dataframe(cat_abc,use_container_width=True)
        csv_abc=sku_summary.to_csv(index=False,encoding="utf-8-sig")
        st.download_button("📥 ABC分析CSV",csv_abc,"abc_analysis.csv","text/csv",use_container_width=True)
    else: st.info("売上データを読み込むとABC分析が表示されます")

# === Tab7: Data Preview ===
with tab7:
    st.header("データプレビュー")
    if st.session_state.churn_df is not None:
        st.subheader("🛒 顧客データ")
        if st.session_state.using_default: st.info("💡 デモデータ（1,000顧客の合成データ）を表示")
        display_data_info(st.session_state.churn_df); st.dataframe(st.session_state.churn_df.head(20),use_container_width=True)
    if st.session_state.demand_df is not None:
        st.markdown("---"); st.subheader("📈 売上データ")
        display_data_info(st.session_state.demand_df); st.dataframe(st.session_state.demand_df.head(20),use_container_width=True)
    if st.session_state.churn_df is None: st.info("データをアップロードしてください")
