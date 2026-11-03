import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render():
    st.header("Step 2: ノイズ除去 (Denoising) と ASV/OTU の生成")
    
    st.markdown("""
    ### 🧬 従来の 97% OTU vs 現代標準の ASV (Amplicon Sequence Variant)
    かつては 97% 類似度で配列をクラスタリングする **OTU (Operational Taxonomic Unit)** が主流でしたが、
    現在では 1 領域の 1 塩基の違いまで高精度に区別できる **ASV (DADA2 / Deblur)** がデファクトスタンダードです。
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **【従来手法】97% OTU (QIIME1 / Mothur)**
        * 配列間の距離を計算し、97% 似ているものを1つの枠組み(OTU)にまとめる。
        * ⚠️ **課題**: シーケンスエラーと本物の1塩基多型(SNV)が混同される。データベース依存性が高い。
        """)
    with col2:
        st.success("""
        **【現代手法】ASV (DADA2 / Deblur / QIIME2)**
        * シーケンスエラー率の統計モデル(Error Model)を学習し、**エラーによる変異を数学的に除去**。
        * 基準値なしで **1塩基解像度** の完全な配列バリアントを同定可能。研究間での再評価が容易！
        """)
        
    st.divider()
    
    st.subheader("🔄 DADA2 ノイズ除去パイプラインの進行状況")
    
    # Interactive DADA2 Step Simulation
    st.caption("DADA2 の各ステップにおけるリード保持数の推移 (1検体あたり平均)")
    
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        error_learning_rate = st.slider("エラー学習精度 (Training iterations)", 1, 10, 5)
    with col_param2:
        chimera_method = st.radio("キメラ除去手法 (Chimera Detection)", ["consensus (推奨)", "pooled", "per-sample"])
        
    # Generate DADA2 pipeline counts
    raw = 50000
    filtered = 45500
    denoised_f = 44200 + (error_learning_rate * 100)
    denoised_r = 43100 + (error_learning_rate * 120)
    merged = 41000
    
    chimera_loss = 2800 if chimera_method == "consensus (推奨)" else (4200 if chimera_method == "pooled" else 1500)
    non_chimera = merged - chimera_loss
    
    steps = ["1. Raw Input", "2. Filtered", "3. Denoised (F)", "4. Denoised (R)", "5. Merged", "6. Non-Chimeric (ASV)"]
    values = [raw, filtered, denoised_f, denoised_r, merged, non_chimera]
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "Read Counts",
        orientation = "v",
        measure = ["absolute", "relative", "relative", "relative", "relative", "total"],
        x = steps,
        textposition = "outside",
        text = [f"{v:,}" for v in values],
        y = [raw, filtered-raw, denoised_f-filtered, denoised_r-denoised_f, merged-denoised_r, non_chimera],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":"#ef553b"}},
        increasing = {"marker":{"color":"#636efa"}},
        totals = {"marker":{"color":"#00cc96"}}
    ))
    
    fig_waterfall.update_layout(
        title="DADA2 パイプラインにおけるリード残存トラッキング (Waterfall Chart)",
        yaxis_title="リード数 (Reads)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    st.markdown(f"""
    #### ⚠️ 注目概念：キメラ配列 (Chimera) とは？
    PCR増幅の過程で、途中で伸びが止まった16S遺伝子断片が**別の菌の16S配列にハイブリダイズ**して延伸されることで生まれる人工的な擬似配列です。
    DADA2 では親配列の組み合わせパターンを照合し、今回の設定 (`{chimera_method}`) では **{chimera_loss:,} リード ({chimera_loss/merged*100:.1f}%)** のキメラを除去しました。
    """)
