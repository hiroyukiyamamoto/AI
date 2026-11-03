import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render(metadata, counts_df, taxonomy_df):
    st.header("Step 3: 分類群の付与 (Taxonomic Assignment) と 菌叢組成")
    
    st.markdown("""
    ### 📚 16S 配列データベースと分類アノテーション
    ノイズ除去された各 ASV の 16S 配列は、参照データベース (SILVA, Greengenes2, GTDB など) と機械学習分類器 (Naive Bayes Classifier) や VSEARCH 検索によって同定されます。
    
    * **界 (Domain/Kingdom)** $\\rightarrow$ **門 (Phylum)** $\\rightarrow$ **綱 (Class)** $\\rightarrow$ **目 (Order)** $\\rightarrow$ **科 (Family)** $\\rightarrow$ **属 (Genus)** $\\rightarrow$ **種 (Species)**
    """)
    
    st.divider()
    
    st.subheader("☀️ 細菌群集の幾何学階層構造 (Taxonomic Sunburst Chart)")
    
    # Merge taxonomy and total counts across samples
    taxa_counts = counts_df.sum(axis=0).to_frame(name="TotalReads")
    merged_taxa = taxonomy_df.join(taxa_counts)
    merged_taxa['Phylum_clean'] = merged_taxa['Phylum'].str.replace('p__', '')
    merged_taxa['Class_clean'] = merged_taxa['Class'].str.replace('c__', '')
    merged_taxa['Order_clean'] = merged_taxa['Order'].str.replace('o__', '')
    merged_taxa['Family_clean'] = merged_taxa['Family'].str.replace('f__', '')
    merged_taxa['Genus_clean'] = merged_taxa['Genus'].str.replace('g__', '')
    merged_taxa['Species_clean'] = merged_taxa['Species'].str.replace('s__', '')
    
    fig_sunburst = px.sunburst(
        merged_taxa,
        path=['Phylum_clean', 'Family_clean', 'Genus_clean'],
        values='TotalReads',
        color='Phylum_clean',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="16S 検出菌叢の分類階層サンバースト図 (クリックで階層移動可能)"
    )
    fig_sunburst.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    st.divider()
    
    st.subheader("📊 菌叢相対構成比の比較 (Taxonomic Composition Stacked Bar)")
    
    col_level, col_grouping = st.columns(2)
    with col_level:
        tax_level = st.selectbox("表示する分類階層", ["Phylum (門)", "Family (科)", "Genus (属)"], index=0)
    with col_grouping:
        group_by_sample = st.radio("表示単位", ["グループ平均 (Group Average)", "検体個別 (Individual Samples)"])
        
    level_col = "Phylum_clean" if "Phylum" in tax_level else ("Family_clean" if "Family" in tax_level else "Genus_clean")
    
    # Calculate relative abundances
    rel_counts = counts_df.div(counts_df.sum(axis=1), axis=0) * 100.0
    
    # Aggregate by selected taxonomic level
    taxa_mapping = merged_taxa[level_col].to_dict()
    rel_counts_taxa = rel_counts.groupby(taxa_mapping, axis=1).sum()
    
    if group_by_sample == "グループ平均 (Group Average)":
        plot_df = rel_counts_taxa.join(metadata.set_index('SampleID')['Group']).groupby('Group').mean().reset_index()
        id_vars = ['Group']
        x_var = 'Group'
    else:
        plot_df = rel_counts_taxa.join(metadata.set_index('SampleID')['Group']).rename_axis('SampleID').reset_index()
        id_vars = ['SampleID', 'Group']
        x_var = 'SampleID'
        
    melted_df = pd.melt(plot_df, id_vars=id_vars, var_name='Taxon', value_name='RelativeAbundance')
    
    fig_bar = px.bar(
        melted_df,
        x=x_var,
        y='RelativeAbundance',
        color='Taxon',
        title=f"相対構成比 (%) [{tax_level}]",
        labels={'RelativeAbundance': '相対存在量 (%)', x_var: '検体 / グループ'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_bar.update_layout(
        barmode='stack',
        height=450,
        yaxis=dict(range=[0, 100]),
        legend=dict(title=tax_level, x=1.05, y=1, xanchor='left', yanchor='top')
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("""
    > 💡 **学べるポイント**:
    > * 健常者の腸内では **Bacillota (旧Firmicutes)** と **Bacteroidota (旧Bacteroidetes)** が優占的です。
    > * 炎症状態や疾患群では **Pseudomonadota (旧Proteobacteria: 腸内細菌科など)** の比率が上昇する「Dysbiosis (菌叢不均衡)」が見られることが多くあります。
    """)
