import streamlit as st
import pandas as pd
import numpy as np
import io
from data_generator import get_preset_datasets, generate_mock_16s_data
from upload_validation import parse_uploads
from modules.step4_diversity import compute_alpha_diversity, compute_bray_curtis
from modules.step5_stats import compute_differential_abundance

def render():
    st.header("Step 6: 実践プレイグラウンド (End-to-End Sandbox)")
    
    st.markdown("""
    ### 🎮 自由にデータセットを選んで / アップロードして解析を実行してみよう！
    学んだ一連の流れ（QC $\\rightarrow$ Denoising $\\rightarrow$ Taxonomy $\\rightarrow$ α/β Diversity $\\rightarrow$ Differential Abundance）を、データセットを切り替えながらシミュレーション・実践できます。
    """)
    
    data_mode = st.radio("データソースの選択", ["プリセットデータセットを使用", "独自のCSVデータをアップロード (Upload Custom CSV)"], horizontal=True)
    
    if data_mode == "プリセットデータセットを使用":
        presets = get_preset_datasets()
        chosen_preset = st.selectbox("学習用プリセットデータセットの選択", list(presets.keys()))
        metadata, counts_df, taxonomy_df = generate_mock_16s_data(chosen_preset)
        st.success(f"📂 選択されたデータセット: **{chosen_preset}** ({presets[chosen_preset]['description']})")
    else:
        st.subheader("📤 自作 CSV ファイルのアップロード")
        st.caption("各CSVは2 MiB以下、4〜100検体、2〜500 ASV、各群2検体以上の2群です。IDとGroupは英数字で始まる英数字・空白・_・.・-のみ。個人情報や機密情報は入力しないでください。")
        
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            up_meta = st.file_uploader("1. Metadata CSV (SampleID, Group 列が必須)", type=["csv"])
        with col_u2:
            up_counts = st.file_uploader("2. Counts CSV (SampleID 行, ASV_ID 列)", type=["csv"])
            
        if up_meta is not None and up_counts is not None:
            try:
                metadata, counts_df = parse_uploads(up_meta.getvalue(), up_counts.getvalue())
            except ValueError as error:
                st.error(str(error))
                return
            # Create dummy taxonomy if missing
            asv_ids = counts_df.columns
            taxonomy_df = pd.DataFrame({
                "ASV_ID": asv_ids,
                "Kingdom": "d__Bacteria",
                "Phylum": "p__Unclassified",
                "Class": "c__Unclassified",
                "Order": "o__Unclassified",
                "Family": "f__Unclassified",
                "Genus": "g__Unclassified",
                "Species": "s__Unclassified",
                "Taxon_String": "d__Bacteria; p__Unclassified"
            }).set_index("ASV_ID")
            st.success("✅ カスタムデータセットが正常に読み込まれました！")
        else:
            st.info("💡 上記のアップローダーからファイルを選択するか、プリセットデータをご使用ください。テンプレート用デフォルトデータを表示中:")
            metadata, counts_df, taxonomy_df = generate_mock_16s_data()

    st.divider()
    
    st.subheader("⚡ 1-Click 一括解析 & レポート出力")
    
    if st.button("🚀 フルパイプライン解析の実行 (Run Complete Pipeline Analysis)", type="primary"):
        with st.spinner("16S メタ解析を実行中..."):
            # 1. Diversity
            df_alpha = compute_alpha_diversity(counts_df)
            df_alpha_meta = df_alpha.merge(metadata, on='SampleID')
            
            # 2. Stats
            df_diff, groups = compute_differential_abundance(metadata, counts_df, taxonomy_df)
            
            st.markdown("### 📋 解析サマリーダッシュボード")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("総検体数", f"{len(metadata)} samples")
            m2.metric("総検出ASV数", f"{counts_df.shape[1]} ASVs")
            m3.metric("平均リード数/検体", f"{int(counts_df.sum(axis=1).mean()):,} reads")
            m4.metric("有意変動バイオマーカー菌種", f"{(df_diff['p_value'] < 0.05).sum()} taxa")
            
            st.subheader("📄 解析結果 CSV ダウンロード")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            
            # CSV Download 1: Alpha diversity
            csv_alpha = df_alpha_meta.to_csv(index=False).encode('utf-8')
            col_d1.download_button(
                label="📥 α多様性結果 (CSV)",
                data=csv_alpha,
                file_name="alpha_diversity_summary.csv",
                mime="text/csv"
            )
            
            # CSV Download 2: Differential Abundance
            csv_diff = df_diff.to_csv(index=False).encode('utf-8')
            col_d2.download_button(
                label="📥 統計変動解析結果 (CSV)",
                data=csv_diff,
                file_name="differential_abundance_summary.csv",
                mime="text/csv"
            )
            
            # CSV Download 3: Relative Abundance
            rel_counts = counts_df.div(counts_df.sum(axis=1), axis=0) * 100.0
            csv_rel = rel_counts.to_csv().encode('utf-8')
            col_d3.download_button(
                label="📥 相対存在量テーブル (CSV)",
                data=csv_rel,
                file_name="relative_abundance_table.csv",
                mime="text/csv"
            )
            
            st.balloons()
