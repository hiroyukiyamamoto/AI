import streamlit as st
import pandas as pd
import numpy as np

# Set Streamlit page config
st.set_page_config(
    page_title="16S メタ解析 統合学習アプリ | Microbiome Workflow Hub",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .stApp [data-testid="stSidebar"] {
        background-color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

from data_generator import get_preset_datasets, generate_mock_16s_data
from modules import step1_qc, step2_denoise, step3_taxonomy, step4_diversity, step5_stats, step6_playground, quiz

def main():
    st.info("公開デモ: 既定データは学習用の合成データです。実測・臨床データではありません。統計手法の一部は説明用の近似です。")
    st.markdown('<div class="main-header">🧬 16S rRNA メタゲノム解析 インタラクティブ学習 Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">生データのクオリティコントロールから統計解析・バイオマーカー特定までの流れを実践学習</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🗺️ 解析ワークフロー")
    
    menu = st.sidebar.radio(
        "学習ステップの選択",
        [
            "🏠 ワークフロー概要 (Overview)",
            "🔬 Step 1: 生データ (FASTQ) と QC",
            "🧬 Step 2: Denoising & ASV 生成",
            "📚 Step 3: 分類群付与 & 菌叢構成",
            "📊 Step 4: 多様性解析 (α・β Diversity)",
            "🧪 Step 5: 統計解析 & バイオマーカー",
            "🎮 Step 6: 実践プレイグラウンド",
            "📝 Step 7: クイズ & 16S 用語辞典"
        ]
    )
    
    st.sidebar.divider()
    
    # Preset dataset selector in sidebar
    st.sidebar.subheader("⚙️ 共通データセット設定")
    presets = get_preset_datasets()
    selected_preset_name = st.sidebar.selectbox("解析対象データセット", list(presets.keys()))
    
    # Load dataset into session state or generate
    if "current_preset" not in st.session_state or st.session_state["current_preset"] != selected_preset_name:
        st.session_state["current_preset"] = selected_preset_name
        metadata, counts_df, taxonomy_df = generate_mock_16s_data(selected_preset_name)
        st.session_state["metadata"] = metadata
        st.session_state["counts_df"] = counts_df
        st.session_state["taxonomy_df"] = taxonomy_df
    else:
        metadata = st.session_state["metadata"]
        counts_df = st.session_state["counts_df"]
        taxonomy_df = st.session_state["taxonomy_df"]

    st.sidebar.caption(f"📌 **条件**: {metadata['Group'].unique()[0]} ({sum(metadata['Group'] == metadata['Group'].unique()[0])}検体) vs {metadata['Group'].unique()[1]} ({sum(metadata['Group'] == metadata['Group'].unique()[1])}検体)")

    # Route navigation
    if "Overview" in menu:
        render_overview()
    elif "Step 1" in menu:
        step1_qc.render()
    elif "Step 2" in menu:
        step2_denoise.render()
    elif "Step 3" in menu:
        step3_taxonomy.render(metadata, counts_df, taxonomy_df)
    elif "Step 4" in menu:
        step4_diversity.render(metadata, counts_df, taxonomy_df)
    elif "Step 5" in menu:
        step5_stats.render(metadata, counts_df, taxonomy_df)
    elif "Step 6" in menu:
        step6_playground.render()
    elif "Step 7" in menu:
        quiz.render()

def render_overview():
    st.markdown("""
    ### 🎯 本アプリの目的
    このWebアプリは、腸内細菌叢や環境菌叢の **16S rRNA アンプリコン解析 (16S Metagenomics / Amplicon Sequencing)** において、
    次世代シーケンサーからの生データ取得から出版レベルの統計解析・図表作成に到達するまでの標準ワークフローを体感的に学ぶための教材アプリです。
    """)
    
    st.divider()
    
    st.subheader("🗺️ 16S rRNA メタ解析パイプラインの全体ロードマップ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 1️⃣ 前処理・ノイズ除去
        * **Step 1: FASTQ & QC**
          Phredスコア確認, プライマー切除, クオリティトリミング
        * **Step 2: Denoising & ASV**
          DADA2/Deblur によるエラー学習, キメラ除去, 1塩基解像度 ASV 同定
        """)
        
    with col2:
        st.markdown("""
        #### 2️⃣ 分類アノテーション & 多様性
        * **Step 3: Taxonomy**
          SILVA データベース照合, 門・属レベル相対構成比グラフ
        * **Step 4: Diversity**
          希釈曲線, α多様性 (Shannon, Chao1), β多様性 (Bray-Curtis PCoA)
        """)
        
    with col3:
        st.markdown("""
        #### 3️⃣ 統計解析 & バイオマーカー
        * **Step 5: Differential Abundance**
          ANCOM-BC / LEfSe / FDR補正, ボルケーノプロット, LDAスコア
        * **Step 6 & 7: 実践 & クイズ**
          自作CSVでの一括解析, 多様性結果CSV出力, 習熟度テスト
        """)

    st.divider()
    
    st.subheader("📊 現在ロードされているサンプルデータセットの概要")
    metadata = st.session_state["metadata"]
    counts_df = st.session_state["counts_df"]
    taxonomy_df = st.session_state["taxonomy_df"]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("総検体数 (Samples)", f"{len(metadata)}")
    m2.metric("比較グループ (Groups)", f"{', '.join(metadata['Group'].unique())}")
    m3.metric("総アンプリコンバリアント (ASVs)", f"{counts_df.shape[1]}")
    m4.metric("総リード数 (Total Reads)", f"{counts_df.sum().sum():,}")

    st.subheader("サンプルメタデータプレビュー (Metadata Table)")
    st.dataframe(metadata, use_container_width=True)

if __name__ == "__main__":
    main()
