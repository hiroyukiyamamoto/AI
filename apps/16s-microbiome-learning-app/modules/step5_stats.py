import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

def compute_differential_abundance(metadata, counts_df, taxonomy_df):
    groups = metadata['Group'].unique()
    g1_samples = metadata[metadata['Group'] == groups[0]]['SampleID'].values
    g2_samples = metadata[metadata['Group'] == groups[1]]['SampleID'].values
    
    # Calculate relative abundances (plus small pseudocount 1e-6)
    rel = counts_df.div(counts_df.sum(axis=1), axis=0) + 1e-6
    
    results = []
    
    for asv_id in rel.columns:
        vals1 = rel.loc[g1_samples, asv_id].values
        vals2 = rel.loc[g2_samples, asv_id].values
        
        mean1 = np.mean(vals1)
        mean2 = np.mean(vals2)
        
        # Log2 fold change (g2 / g1)
        log2_fc = np.log2(mean2 / mean1)
        
        # Mann-Whitney U test
        stat, pval = stats.mannwhitneyu(vals1, vals2)
        
        # LDA score estimation (approximate LEfSe algorithm)
        delta_mean = abs(mean1 - mean2)
        lda_score = np.log10(1 + delta_mean * 1e5) * (3.0 if pval < 0.05 else 1.0)
        
        taxon_info = taxonomy_df.loc[asv_id]
        genus_species = f"{taxon_info['Genus'].replace('g__', '')} {taxon_info['Species'].replace('s__', '')}"
        phylum = taxon_info['Phylum'].replace('p__', '')
        
        results.append({
            "ASV_ID": asv_id,
            "Phylum": phylum,
            "Genus_Species": genus_species,
            "Taxon_String": taxon_info['Taxon_String'],
            "Mean_G1": mean1,
            "Mean_G2": mean2,
            "Log2_FC": log2_fc,
            "p_value": pval,
            "LDA_Score": lda_score,
            "Enriched_In": groups[1] if log2_fc > 0 else groups[0]
        })
        
    df_res = pd.DataFrame(results)
    
    # False Discovery Rate (FDR) Benjamini-Hochberg correction
    _, qvals, _, _ = multipletests(df_res['p_value'], method='fdr_bh')
    df_res['q_value (FDR)'] = qvals
    df_res['-log10(p_value)'] = -np.log10(df_res['p_value'])
    
    return df_res, groups

def render(metadata, counts_df, taxonomy_df):
    st.header("Step 5: 統計解析・変動細菌の同定 (Differential Abundance & Biomarker Discovery)")
    
    st.markdown("""
    ### 🔬 メタ解析の核心: 群間で優位に変動する細菌 (Biomarker) の特定
    単に全細菌の量を直接比較すると、シーケンス深度の差や高自由度過剰ゼロ (Zero-inflation) の影響を受けます。
    そのため、現代の16S解析では **ANCOM-BC**, **LEfSe**, **DESeq2 / ALDEx2**, **FDR (Benjamini-Hochberg) 補正** が標準適用されます。
    """)
    
    df_diff, groups = compute_differential_abundance(metadata, counts_df, taxonomy_df)
    
    st.divider()
    
    col_thresh1, col_thresh2 = st.columns(2)
    with col_thresh1:
        p_cutoff = st.slider("有意差閾値 (p-value cutoff)", 0.001, 0.10, 0.05, step=0.005)
    with col_thresh2:
        fc_cutoff = st.slider("変化倍率閾値 (|Log2 Fold Change| cutoff)", 0.0, 3.0, 1.0, step=0.2)
        
    df_diff['Significant'] = (df_diff['p_value'] < p_cutoff) & (df_diff['Log2_FC'].abs() > fc_cutoff)
    
    tab_volcano, tab_lefse, tab_box = st.tabs([
        "🌋 1. ボルケーノプロット (Volcano Plot)",
        "📊 2. LEfSe LDA スコア解析 (Biomarker Size)",
        "📦 3. 特定菌の存在量比較 (Boxplot)"
    ])
    
    # --- TAB 1: Volcano ---
    with tab_volcano:
        st.subheader("ボルケーノプロット (Volcano Plot)")
        st.caption(f"横軸: 変化の大きさ (Log2 FC), 縦軸: 統計的確からしさ (-Log10 p-value). 左: {groups[0]}で濃縮, 右: {groups[1]}で濃縮")
        
        fig_volc = px.scatter(
            df_diff,
            x='Log2_FC',
            y='-log10(p_value)',
            color='Significant',
            hover_name='Genus_Species',
            hover_data=['Phylum', 'p_value', 'q_value (FDR)'],
            color_discrete_map={True: '#e74c3c', False: '#bdc3c7'},
            title="差分発現 / 変動細菌の分布",
            labels={'Log2_FC': f'Log2 Fold Change ({groups[1]} / {groups[0]})', '-log10(p_value)': '-Log10 (p-value)'}
        )
        
        fig_volc.add_vline(x=fc_cutoff, line_dash="dash", line_color="gray")
        fig_volc.add_vline(x=-fc_cutoff, line_dash="dash", line_color="gray")
        fig_volc.add_hline(y=-np.log10(p_cutoff), line_dash="dash", line_color="gray")
        
        fig_volc.update_traces(marker=dict(size=10, opacity=0.85))
        fig_volc.update_layout(height=450)
        st.plotly_chart(fig_volc, use_container_width=True)
        
        sig_count = df_diff['Significant'].sum()
        st.success(f"🔍 判定結果: 選択された閾値条件を満たす特定バイオマーカー細菌は **{sig_count} 種類** 検出されました。")

    # --- TAB 2: LEfSe ---
    with tab_lefse:
        st.subheader("LEfSe (Linear Discriminant Analysis Effect Size)")
        st.caption("各群の特徴となる細菌種を LDA スコア (効果量) の大きさで順位付けします。")
        
        df_sig = df_diff[df_diff['Significant']].sort_values(by='LDA_Score', ascending=True)
        
        if len(df_sig) > 0:
            fig_lefse = px.bar(
                df_sig,
                y='Genus_Species',
                x='LDA_Score',
                color='Enriched_In',
                orientation='h',
                title="LEfSe 特徴バイオマーカー菌種 (LDA Score)",
                labels={'LDA_Score': 'LDA Score (log 10)', 'Genus_Species': '細菌種 (Genus species)'},
                color_discrete_map={groups[0]: '#3498db', groups[1]: '#e74c3c'}
            )
            fig_lefse.update_layout(height=max(350, len(df_sig) * 28))
            st.plotly_chart(fig_lefse, use_container_width=True)
        else:
            st.warning("⚠️ 現在の閾値条件を満たす有意な菌種が存在しません。スライダーで p-value または Fold Change 閾値を緩和してください。")

    # --- TAB 3: Boxplot for candidate taxa ---
    with tab_box:
        st.subheader("特定細菌種の検体群間存在量比較")
        
        selected_taxon = st.selectbox("観察する細菌種を選択", df_diff['Genus_Species'].unique(), index=0)
        
        asv_match = df_diff[df_diff['Genus_Species'] == selected_taxon]['ASV_ID'].values[0]
        
        # Build DataFrame for plotting
        rel_counts = counts_df.div(counts_df.sum(axis=1), axis=0) * 100.0
        tax_series = rel_counts[asv_match].to_frame(name="Relative_Abundance_Percent")
        plot_df = tax_series.merge(metadata.set_index('SampleID'), left_index=True, right_index=True).rename_axis('SampleID').reset_index()
        
        fig_taxon_box = px.box(
            plot_df,
            x='Group',
            y='Relative_Abundance_Percent',
            color='Group',
            points='all',
            hover_name='SampleID',
            title=f"{selected_taxon} の相対存在量 (%) 比較",
            labels={'Relative_Abundance_Percent': '相対存在量 (%)', 'Group': '実験群'},
            color_discrete_map={groups[0]: '#3498db', groups[1]: '#e74c3c'}
        )
        fig_taxon_box.update_layout(height=420)
        st.plotly_chart(fig_taxon_box, use_container_width=True)
        
        info_row = df_diff[df_diff['ASV_ID'] == asv_match].iloc[0]
        st.info(f"""
        📌 **統計詳細データ ({selected_taxon})**:
        * **所属門 (Phylum)**: {info_row['Phylum']}
        * **{groups[0]} 群の平均** : {info_row['Mean_G1']*100:.3f}%
        * **{groups[1]} 群の平均** : {info_row['Mean_G2']*100:.3f}%
        * **p-value (Raw)** : {info_row['p_value']:.4e}
        * **q-value (FDR補正後)** : {info_row['q_value (FDR)']:.4e}
        """)
