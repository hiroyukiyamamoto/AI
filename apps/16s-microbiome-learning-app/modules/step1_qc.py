import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from data_generator import generate_mock_fastq_quality

def render():
    st.header("Step 1: 生データ (FASTQ) と クオリティコントロール (QC)")
    
    st.markdown("""
    ### 🔬 16S rRNA 解析の第一歩：リード精度の評価とトリミング
    次世代シーケンサー (Illumina MiSeq/NextSeq 等) から出力される **FASTQ ファイル** には、塩基配列情報に加えて各塩基の **Phred クオリティスコア ($Q$)** が記録されています。
    
    #### 💡 Phred スコアとエラー確率の関係
    $$Q = -10 \\log_{10}(P_{error})$$
    
    * **$Q = 20$** : 正解率 **99.0%** (100塩基に1個のエラー)
    * **$Q = 30$** : 正解率 **99.9%** (1000塩基に1個のエラー) ← **臨床・研究での標準目標**
    * **$Q = 40$** : 正解率 **99.99%**
    """)
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ パラメータ設定シミュレーター")
        st.caption("DADA2 や QIIME 2 (filterAndTrim) で指定する主要トリミング引数")
        
        trunc_f = st.slider("Forward Lead Truncation Length (`trunc-len-f`) [bp]", 150, 300, 240, step=5)
        trunc_r = st.slider("Reverse Lead Truncation Length (`trunc-len-r`) [bp]", 150, 300, 200, step=5)
        max_ee_f = st.select_slider("Forward Max Expected Errors (`maxEE`)", options=[1, 2, 3, 5], value=2)
        max_ee_r = st.select_slider("Reverse Max Expected Errors (`maxEE`)", options=[1, 2, 3, 5], value=2)
        
        # Calculate overlap for V3-V4 (460bp target)
        amplicon_len = 460
        combined_len = trunc_f + trunc_r
        overlap = combined_len - amplicon_len
        
        st.info(f"📐 **V3-V4領域アンプリコン長 (約 {amplicon_len} bp)** に対する判定:")
        if overlap >= 20:
            st.success(f"✅ オーバーラップ量: **{overlap} bp** (推奨20bp以上を満たしています。Pairing結合可能です！)")
        elif overlap > 0:
            st.warning(f"⚠️ オーバーラップ量: **{overlap} bp** (20bp未満です。マージ時にリードが結合できず廃棄されるリスクがあります)")
        else:
            st.error(f"❌ オーバーラップ量: **{overlap} bp** (長さ不足！FとRが重ならずDADA2のマージに失敗します)")

    with col2:
        st.subheader("📊 配列位置ごとのクオリティスコアプロファイル")
        df_qc = generate_mock_fastq_quality()
        
        fig = go.Figure()
        
        # R1
        df_r1 = df_qc[df_qc['Read'] == 'Forward (R1)']
        fig.add_trace(go.Scatter(x=df_r1['Position'], y=df_r1['Mean'], mode='lines', name='Forward (R1) 平均Q', line=dict(color='#1f77b4', width=2.5)))
        
        # R2
        df_r2 = df_qc[df_qc['Read'] == 'Reverse (R2)']
        fig.add_trace(go.Scatter(x=df_r2['Position'], y=df_r2['Mean'], mode='lines', name='Reverse (R2) 平均Q', line=dict(color='#ff7f0e', width=2.5)))
        
        # Truncation lines
        fig.add_vline(x=trunc_f, line_dash="dash", line_color="#1f77b4", annotation_text=f"R1 Cut ({trunc_f}bp)")
        fig.add_vline(x=trunc_r, line_dash="dash", line_color="#ff7f0e", annotation_text=f"R2 Cut ({trunc_r}bp)")
        
        # Threshold line Q=30
        fig.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="Q30 (99.9% Accuracy)")
        
        fig.update_layout(
            xaxis_title="配列位置 (Base Position [bp])",
            yaxis_title="Phred Quality Score (Q)",
            yaxis=dict(range=[10, 42]),
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01),
            height=380
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    st.subheader("📈 トラッキング: フィルタリング通過リード数シミュレーション")
    
    # Simulate read retention rate based on parameters
    penalty_f = max(0, (trunc_f - 200) * 0.15) / (max_ee_f + 0.5)
    penalty_r = max(0, (trunc_r - 180) * 0.25) / (max_ee_r + 0.5)
    
    base_reads = 50000
    if overlap < 12:
        retained_reads = 0
    else:
        retention_rate = max(0.1, min(0.95, 0.92 - (penalty_f + penalty_r) * 0.05))
        retained_reads = int(base_reads * retention_rate)
        
    filtered_out = base_reads - retained_reads
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    metrics_col1.metric("総入力リード数", f"{base_reads:,} reads")
    metrics_col2.metric("QC・マージ通過リード数", f"{retained_reads:,} reads", delta=f"{retained_reads/base_reads*100:.1f}% 通過")
    metrics_col3.metric("破棄されたリード数", f"{filtered_out:,} reads", delta_color="inverse", delta=f"{filtered_out/base_reads*100:.1f}% 損失")

    st.markdown("""
    > 💡 **学べるポイント**:
    > * Illuminaの2x300bpシーケンスでは、**Reverseリード (R2) の後半でクオリティスコアが大きく低下**する傾向があります。
    > * 低クオリティ領域を切除 (`trunc-len`) することでシーケンスエラーの混入を防げますが、切りすぎると **Forward と Reverse が重ね合わさらなくなる** ため注意が必要です。
    """)
