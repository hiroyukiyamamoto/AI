import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.manifold import MDS
from sklearn.decomposition import PCA

def compute_alpha_diversity(counts_df):
    results = []
    for sample_id, row in counts_df.iterrows():
        counts = row.values[row.values > 0]
        total = counts.sum()
        props = counts / total
        
        # Shannon
        shannon = -np.sum(props * np.log(props))
        # Simpson
        simpson = 1.0 - np.sum(props ** 2)
        # Observed
        observed = len(counts)
        # Chao1 estimate
        f1 = np.sum(counts == 1)
        f2 = np.sum(counts == 2)
        chao1 = observed + (f1 * (f1 - 1)) / (2 * (f2 + 1)) if f2 > 0 else observed + (f1 * (f1 - 1)) / 2
        
        results.append({
            "SampleID": sample_id,
            "Observed_ASVs": observed,
            "Shannon": shannon,
            "Simpson": simpson,
            "Chao1": chao1
        })
    return pd.DataFrame(results)

def compute_bray_curtis(counts_df):
    rel = counts_df.div(counts_df.sum(axis=1), axis=0).values
    n = rel.shape[0]
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            bc = np.sum(np.abs(rel[i] - rel[j])) / np.sum(rel[i] + rel[j])
            dist[i, j] = bc
            dist[j, i] = bc
    return dist

def compute_jaccard(counts_df):
    presence = (counts_df > 0).astype(int).values
    n = presence.shape[0]
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            intersection = np.sum((presence[i] == 1) & (presence[j] == 1))
            union = np.sum((presence[i] == 1) | (presence[j] == 1))
            jac = 1.0 - (intersection / union if union > 0 else 0)
            dist[i, j] = jac
            dist[j, i] = jac
    return dist

def render(metadata, counts_df, taxonomy_df):
    st.header("Step 4: 多様性解析 (Alpha & Beta Diversity Analysis)")
    
    st.markdown("""
    菌叢データの多様性は、**1つのサンプル内の複雑さ (α多様性)** と **サンプル間の構成の違い (β多様性)** に分けて評価します。
    """)
    
    tab_rare, tab_alpha, tab_beta = st.tabs([
        "📈 1. 希釈曲線 (Rarefaction Curve)",
        "📊 2. α多様体解析 (Alpha Diversity)",
        "🌐 3. β多様体解析 (Beta Diversity & PCoA)"
    ])
    
    # --- TAB 1: Rarefaction ---
    with tab_rare:
        st.subheader("シーケンシング深度の充足性確認 (Rarefaction Curve)")
        st.caption("サンプリング深度を徐々に増やした際に検出種数 (ASV数) が飽和するかを観察します。")
        
        step_depths = np.linspace(1000, counts_df.sum(axis=1).min(), 10, dtype=int)
        rare_data = []
        
        sample_groups = metadata.set_index('SampleID')['Group'].to_dict()
        
        for sample_id, row in counts_df.iterrows():
            grp = sample_groups[sample_id]
            counts = row.values
            total = counts.sum()
            prob = counts / total
            
            for depth in step_depths:
                # Expectation of observed species under multinomial subsampling
                prob_not_drawn = (1 - prob) ** depth
                obs_expected = np.sum(1 - prob_not_drawn)
                rare_data.append({
                    "SampleID": sample_id,
                    "Group": grp,
                    "Depth": depth,
                    "Observed_ASVs": obs_expected
                })
                
        df_rare = pd.DataFrame(rare_data)
        
        fig_rare = px.line(
            df_rare,
            x='Depth',
            y='Observed_ASVs',
            color='Group',
            line_group='SampleID',
            title="希釈曲線 (シーケンシング深度 vs 検出ASV数)",
            labels={'Depth': 'サブサンプリングリード数 (Sequencing Depth)', 'Observed_ASVs': '検出ASV数'}
        )
        fig_rare.update_layout(height=420)
        st.plotly_chart(fig_rare, use_container_width=True)
        st.info("💡 曲線が右側で平坦 (飽和) に達していれば、菌叢構成を網羅するのに十分なシーケンス深度が得られていることを意味します。")

    # --- TAB 2: Alpha Diversity ---
    with tab_alpha:
        st.subheader("α多様性指標の群間比較")
        
        df_alpha = compute_alpha_diversity(counts_df)
        df_alpha_meta = df_alpha.merge(metadata, on='SampleID')
        
        col_metric, col_test = st.columns(2)
        with col_metric:
            selected_alpha = st.selectbox("比較する指標", ["Shannon", "Simpson", "Observed_ASVs", "Chao1"], index=0)
        with col_test:
            test_type = st.radio("統計検定手法", ["Mann-Whitney U 検定 (非パラメトリック)", "Welch's t-test (パラメトリック)"])
            
        groups = df_alpha_meta['Group'].unique()
        g1_vals = df_alpha_meta[df_alpha_meta['Group'] == groups[0]][selected_alpha].values
        g2_vals = df_alpha_meta[df_alpha_meta['Group'] == groups[1]][selected_alpha].values
        
        if "Mann-Whitney" in test_type:
            stat, pval = stats.mannwhitneyu(g1_vals, g2_vals)
            test_name = "Mann-Whitney U"
        else:
            stat, pval = stats.ttest_ind(g1_vals, g2_vals, equal_var=False)
            test_name = "Welch's t-test"
            
        fig_alpha = px.box(
            df_alpha_meta,
            x='Group',
            y=selected_alpha,
            color='Group',
            points="all",
            title=f"α多様性: {selected_alpha} Index ({groups[0]} vs {groups[1]})",
            labels={selected_alpha: selected_alpha, 'Group': '実験群'}
        )
        fig_alpha.update_layout(height=420)
        st.plotly_chart(fig_alpha, use_container_width=True)
        
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("検定統計量 (Statistic)", f"{stat:.3f}")
        res_col2.metric("有意差 p-value", f"{pval:.4e}", delta="有意差あり (p < 0.05)" if pval < 0.05 else "有意差なし (p >= 0.05)")

    # --- TAB 3: Beta Diversity ---
    with tab_beta:
        st.subheader("β多様性・主座標分析 (PCoA: Principal Coordinate Analysis)")
        
        col_dist, col_dim = st.columns(2)
        with col_dist:
            dist_metric = st.selectbox("距離行列の定義", ["Bray-Curtis (定量: 菌の存在量重視)", "Jaccard (定性: 菌の有無重視)"], index=0)
        with col_dim:
            plot_dim = st.radio("次元数", ["2D PCoA", "3D PCoA"])
            
        if "Bray-Curtis" in dist_metric:
            dist_matrix = compute_bray_curtis(counts_df)
        else:
            dist_matrix = compute_jaccard(counts_df)
            
        # PCoA calculation using Classical Multidimensional Scaling (MDS)
        mds = MDS(n_components=3, dissimilarity="precomputed", random_state=42)
        pcoa_coords = mds.fit_transform(dist_matrix)
        
        df_pcoa = pd.DataFrame(pcoa_coords, columns=['PCoA1', 'PCoA2', 'PCoA3'])
        df_pcoa['SampleID'] = counts_df.index
        df_pcoa = df_pcoa.merge(metadata, on='SampleID')
        
        if plot_dim == "2D PCoA":
            fig_beta = px.scatter(
                df_pcoa,
                x='PCoA1',
                y='PCoA2',
                color='Group',
                hover_name='SampleID',
                title=f"PCoA 散布図 ({dist_metric.split()[0]} Distance)",
                labels={'PCoA1': 'Axis 1 (主座標1)', 'PCoA2': 'Axis 2 (主座標2)'}
            )
            fig_beta.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='DarkSlateGrey')))
            fig_beta.update_layout(height=480)
            st.plotly_chart(fig_beta, use_container_width=True)
        else:
            fig_beta = px.scatter_3d(
                df_pcoa,
                x='PCoA1',
                y='PCoA2',
                z='PCoA3',
                color='Group',
                hover_name='SampleID',
                title=f"3D PCoA 空間視覚化 ({dist_metric.split()[0]} Distance)",
                labels={'PCoA1': 'Axis 1', 'PCoA2': 'Axis 2', 'PCoA3': 'Axis 3'}
            )
            fig_beta.update_traces(marker=dict(size=8, opacity=0.85))
            fig_beta.update_layout(height=520)
            st.plotly_chart(fig_beta, use_container_width=True)
            
        # Simplified PERMANOVA simulation
        st.subheader("🧪 PERMANOVA (Adonis) 多変量分散分析")
        
        # Calculate Pseudo-F statistic
        groups_list = df_pcoa['Group'].values
        unique_grps = np.unique(groups_list)
        
        # Total sum of squares
        n = dist_matrix.shape[0]
        SST = np.sum(dist_matrix**2) / (2 * n)
        
        # Within-group sum of squares
        SSW = 0
        for g in unique_grps:
            idx = np.where(groups_list == g)[0]
            sub_dist = dist_matrix[np.ix_(idx, idx)]
            SSW += np.sum(sub_dist**2) / (2 * len(idx))
            
        SSA = SST - SSW
        a = len(unique_grps)
        df_between = a - 1
        df_within = n - a
        
        f_stat = (SSA / df_between) / (SSW / df_within)
        r2 = SSA / SST
        
        # P-value calculation using permutation
        n_perm = 99
        f_perms = []
        for _ in range(n_perm):
            perm_grps = np.random.permutation(groups_list)
            ssw_p = 0
            for g in unique_grps:
                idx = np.where(perm_grps == g)[0]
                sub_dist = dist_matrix[np.ix_(idx, idx)]
                ssw_p += np.sum(sub_dist**2) / (2 * len(idx))
            ssa_p = SST - ssw_p
            f_p = (ssa_p / df_between) / (ssw_p / df_within)
            f_perms.append(f_p)
            
        perm_p = (np.sum(np.array(f_perms) >= f_stat) + 1) / (n_perm + 1)
        
        perma_col1, perma_col2, perma_col3 = st.columns(3)
        perma_col1.metric("Pseudo-F 値", f"{f_stat:.3f}")
        perma_col2.metric("寄与率 (R²)", f"{r2*100:.2f}%")
        perma_col3.metric("PERMANOVA p-value", f"{perm_p:.4f}", delta="群間に有意な菌叢差異あり" if perm_p < 0.05 else "有意差なし")
