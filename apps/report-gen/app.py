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

def detect_anomalies(mom,yoy,threshold=ANOMALY_THRESHOLD):
    """異常値（前月比or前年同月比でthreshold以上変動）を検出"""
    anomalies=[]
    for acct,data in mom.items():
        if abs(data["pct"])>=threshold*100:
            direction="増加" if data["pct"]>0 else "減少"
            anomalies.append({"科目":acct,"種別":"前月比","変動率":f"{data['pct']:+.1f}%","方向":direction,
                "当月":f"{data['current']:,.0f}万円","前月":f"{data['previous']:,.0f}万円",
                "差額":f"{data['change']:+,.0f}万円","severity":"🔴" if abs(data["pct"])>=50 else "🟡"})
    for acct,data in yoy.items():
        if abs(data["pct"])>=threshold*100:
            direction="増加" if data["pct"]>0 else "減少"
            anomalies.append({"科目":acct,"種別":"前年同月比","変動率":f"{data['pct']:+.1f}%","方向":direction,
                "当月":f"{data['current']:,.0f}万円","前年同月":f"{data['prev_year']:,.0f}万円",
                "差額":f"{data['change']:+,.0f}万円","severity":"🔴" if abs(data["pct"])>=50 else "🟡"})
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
        lines.append("原因の確認と、必要に応じた対策の検討をお勧めします。\n")
    lines.append("---\n")
    lines.append(f"*本レポートはAI経営パートナーの月次レポート自動生成ツールで作成されました。*")
    return "\n".join(lines)

# === Page Config ===
st.set_page_config(page_title="月次レポート自動生成",page_icon="📊",layout="wide",initial_sidebar_state="expanded")

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
st.sidebar.caption("月次レポート自動生成 v1.0")

# === Main ===
st.title("📊 月次レポート自動生成ツール")
st.markdown("freee/MFの試算表CSVをアップロードするだけで、**前月比・前年同月比・異常値検知**を自動実行し、顧問先向けレポートを生成します。")

if st.session_state.df_cur is not None:
    df_cur=st.session_state.df_cur
    df_prev=st.session_state.df_prev
    report_month=df_cur.iloc[-1]["年月"] if "年月" in df_cur.columns else "最新月"

    # 分析実行
    mom=calc_mom(df_cur)
    yoy=calc_yoy(df_cur,df_prev) if df_prev is not None else {}
    anomalies=detect_anomalies(mom,yoy)
    report_md=generate_report_md(df_cur,df_prev,mom,yoy,anomalies,client_name,report_month)

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
                fig,ax=plt.subplots(figsize=(10,3))
                vals_cur=df_cur[acct].values.astype(float)
                ax.bar(range(len(months)),vals_cur,color="#2563EB",alpha=0.7,label="当期")
                if df_prev is not None and acct in df_prev.columns:
                    vals_prev=df_prev[acct].values.astype(float)
                    n=min(len(vals_cur),len(vals_prev))
                    ax.plot(range(n),vals_prev[:n],color="#94A3B8",linewidth=2,marker="o",markersize=4,label="前期",ls="--")
                ax.set_title(acct,fontsize=13,fontweight="bold")
                ax.set_xticks(range(len(months))); ax.set_xticklabels([m[-3:] for m in months],fontsize=9)
                ax.set_ylabel("万円"); ax.legend(loc="upper left"); plt.tight_layout()
                st.pyplot(fig); plt.close(fig)

    with tab3:
        st.header("⚠️ 異常値アラート")
        st.markdown(f"前月比・前年同月比で**{int(ANOMALY_THRESHOLD*100)}%以上の変動**があった科目を表示します。")
        if anomalies:
            st.warning(f"**{len(anomalies)}件**の異常値が検出されました。")
            adf=pd.DataFrame(anomalies)
            show_cols=[c for c in ["severity","科目","種別","変動率","方向","当月","前月","前年同月","差額"] if c in adf.columns]
            st.dataframe(adf[show_cols],use_container_width=True,hide_index=True)
        else:
            st.success("異常値は検出されませんでした。")

    with tab4:
        st.header("📊 データプレビュー")
        st.subheader("当期データ")
        st.dataframe(df_cur,use_container_width=True)
        if df_prev is not None:
            st.subheader("前期データ")
            st.dataframe(df_prev,use_container_width=True)
else:
    st.info("サイドバーから試算表CSVをアップロードしてください。\n\nデモデータが自動で読み込まれている場合は、そのままご利用いただけます。")
