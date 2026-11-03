import numpy as np
import pandas as pd

def get_preset_datasets():
    return {
        "腸内細菌叢：炎症性腸疾患 (IBD vs 健常者) [Gut IBD Study]": {
            "description": "健常群(Healthy: 12検体) vs IBD群(IBD: 12検体) の腸内細菌叢16S V3-V4解析データ",
            "condition_a": "Healthy",
            "condition_b": "IBD",
            "seed": 42
        },
        "益生菌(プロバイオティクス) 摂取介入試験 [Probiotic Intervention]": {
            "description": "プラセボ群(Placebo: 12検体) vs プロバイオティクス摂取群(Probiotic: 12検体) の糞便菌叢データ",
            "condition_a": "Placebo",
            "condition_b": "Probiotic",
            "seed": 101
        },
        "食事介入試験：高食物繊維食 vs 高脂質食 [Diet Intervention]": {
            "description": "高食物繊維食(High_Fiber: 12検体) vs 高脂質食(High_Fat: 12検体) の腸内メタゲノム16Sデータ",
            "condition_a": "High_Fiber",
            "condition_b": "High_Fat",
            "seed": 202
        }
    }

def generate_mock_16s_data(dataset_key="腸内細菌叢：炎症性腸疾患 (IBD vs 健常者) [Gut IBD Study]"):
    presets = get_preset_datasets()
    preset_info = presets.get(dataset_key, list(presets.values())[0])
    
    seed = preset_info["seed"]
    np.random.seed(seed)
    
    group_a_name = preset_info["condition_a"]
    group_b_name = preset_info["condition_b"]
    
    n_a = 12
    n_b = 12
    n_samples = n_a + n_b
    
    sample_ids = [f"Sample_{i+1:02d}" for i in range(n_samples)]
    groups = [group_a_name] * n_a + [group_b_name] * n_b
    ages = np.random.randint(22, 65, size=n_samples)
    bmi = np.round(np.random.normal(23.5, 3.2, size=n_samples), 1)
    seq_depths = np.random.randint(25000, 60000, size=n_samples)
    
    metadata = pd.DataFrame({
        "SampleID": sample_ids,
        "Group": groups,
        "Age": ages,
        "BMI": bmi,
        "SequencingDepth": seq_depths
    })
    
    # 25 realistic taxonomy entries
    taxa_definitions = [
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Ruminococcaceae", "genus": "Faecalibacterium", "species": "prausnitzii", "base_a": 0.18, "base_b": 0.04},
        {"phylum": "Bacteroidota", "class": "Bacteroidia", "order": "Bacteroidales", "family": "Bacteroidaceae", "genus": "Bacteroides", "species": "fragilis", "base_a": 0.12, "base_b": 0.19},
        {"phylum": "Bacteroidota", "class": "Bacteroidia", "order": "Bacteroidales", "family": "Bacteroidaceae", "genus": "Bacteroides", "species": "vulgatus", "base_a": 0.10, "base_b": 0.12},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Lachnospiraceae", "genus": "Blautia", "species": "wexlerae", "base_a": 0.08, "base_b": 0.06},
        {"phylum": "Verrucomicrobiota", "class": "Verrucomicrobiae", "order": "Verrucomicrobiales", "family": "Akkermansiaceae", "genus": "Akkermansia", "species": "muciniphila", "base_a": 0.07, "base_b": 0.015},
        {"phylum": "Actinomycetota", "class": "Actinomycetia", "order": "Bifidobacteriales", "family": "Bifidobacteriaceae", "genus": "Bifidobacterium", "species": "longum", "base_a": 0.06, "base_b": 0.02},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Lachnospiraceae", "genus": "Roseburia", "species": "intestinalis", "base_a": 0.06, "base_b": 0.01},
        {"phylum": "Bacteroidota", "class": "Bacteroidia", "order": "Bacteroidales", "family": "Prevotellaceae", "genus": "Prevotella", "species": "copri", "base_a": 0.05, "base_b": 0.03},
        {"phylum": "Pseudomonadota", "class": "Gammaproteobacteria", "order": "Enterobacterales", "family": "Enterobacteriaceae", "genus": "Escherichia", "species": "coli", "base_a": 0.01, "base_b": 0.11},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Lachnospiraceae", "genus": "Ruminococcus", "species": "gnavus", "base_a": 0.015, "base_b": 0.08},
        {"phylum": "Bacillota", "class": "Bacilli", "order": "Lactobacillales", "family": "Lactobacillaceae", "genus": "Lactobacillus", "species": "rhamnosus", "base_a": 0.03, "base_b": 0.01},
        {"phylum": "Bacillota", "class": "Bacilli", "order": "Lactobacillales", "family": "Streptococcaceae", "genus": "Streptococcus", "species": "salivarius", "base_a": 0.02, "base_b": 0.05},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Lachnospiraceae", "genus": "Coprococcus", "species": "eutactus", "base_a": 0.04, "base_b": 0.015},
        {"phylum": "Bacteroidota", "class": "Bacteroidia", "order": "Bacteroidales", "family": "Rikenellaceae", "genus": "Alistipes", "species": "putredinis", "base_a": 0.03, "base_b": 0.03},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Eubacteriaceae", "genus": "Eubacterium", "species": "rectale", "base_a": 0.04, "base_b": 0.01},
        {"phylum": "Pseudomonadota", "class": "Gammaproteobacteria", "order": "Enterobacterales", "family": "Enterobacteriaceae", "genus": "Klebsiella", "species": "pneumoniae", "base_a": 0.005, "base_b": 0.04},
        {"phylum": "Actinomycetota", "class": "Coriobacteriia", "order": "Coriobacteriales", "family": "Coriobacteriaceae", "genus": "Collinsella", "species": "aerofaciens", "base_a": 0.02, "base_b": 0.025},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Oscillospiraceae", "genus": "Oscillibacter", "species": "valericigenes", "base_a": 0.015, "base_b": 0.01},
        {"phylum": "Bacteroidota", "class": "Bacteroidia", "order": "Bacteroidales", "family": "Porphyromonadaceae", "genus": "Parabacteroides", "species": "distasonis", "base_a": 0.02, "base_b": 0.025},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Lachnospiraceae", "genus": "Dorea", "species": "longicatena", "base_a": 0.015, "base_b": 0.02},
        {"phylum": "Pseudomonadota", "class": "Betaproteobacteria", "order": "Burkholderiales", "family": "Sutterellaceae", "genus": "Sutterella", "species": "wadsworthensis", "base_a": 0.01, "base_b": 0.02},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Peptostreptococcaceae", "genus": "Intestinibacter", "species": "bartlettii", "base_a": 0.005, "base_b": 0.015},
        {"phylum": "Actinomycetota", "class": "Actinomycetia", "order": "Bifidobacteriales", "family": "Bifidobacteriaceae", "genus": "Bifidobacterium", "species": "adolescentis", "base_a": 0.025, "base_b": 0.01},
        {"phylum": "Fusobacteriota", "class": "Fusobacteriia", "order": "Fusobacteriales", "family": "Fusobacteriaceae", "genus": "Fusobacterium", "species": "nucleatum", "base_a": 0.002, "base_b": 0.025},
        {"phylum": "Bacillota", "class": "Clostridia", "order": "Eubacteriales", "family": "Clostridiaceae", "genus": "Clostridium", "species": "perfringens", "base_a": 0.003, "base_b": 0.015}
    ]
    
    asv_ids = [f"ASV_{i+1:03d}" for i in range(len(taxa_definitions))]
    
    # Build taxonomy DataFrame
    taxonomy_rows = []
    for i, t in enumerate(taxa_definitions):
        taxonomy_rows.append({
            "ASV_ID": asv_ids[i],
            "Kingdom": "d__Bacteria",
            "Phylum": f"p__{t['phylum']}",
            "Class": f"c__{t['class']}",
            "Order": f"o__{t['order']}",
            "Family": f"f__{t['family']}",
            "Genus": f"g__{t['genus']}",
            "Species": f"s__{t['species']}",
            "Taxon_String": f"d__Bacteria; p__{t['phylum']}; c__{t['class']}; o__{t['order']}; f__{t['family']}; g__{t['genus']}; s__{t['species']}"
        })
    taxonomy_df = pd.DataFrame(taxonomy_rows).set_index("ASV_ID")
    
    # Generate count matrix
    count_matrix = np.zeros((n_samples, len(asv_ids)), dtype=int)
    
    for s_idx in range(n_samples):
        depth = seq_depths[s_idx]
        is_group_a = (s_idx < n_a)
        
        # Dirichlet parameters
        alpha = []
        for t in taxa_definitions:
            base_prop = t["base_a"] if is_group_a else t["base_b"]
            alpha.append(base_prop * 80.0) # concentration
            
        proportions = np.random.dirichlet(alpha)
        counts = np.random.multinomial(depth, proportions)
        count_matrix[s_idx, :] = counts
        
    counts_df = pd.DataFrame(count_matrix, index=sample_ids, columns=asv_ids)
    
    return metadata, counts_df, taxonomy_df

def generate_mock_fastq_quality():
    """Generates positional Phred quality score profile for R1 and R2 reads"""
    positions = np.arange(1, 301)
    
    # R1: Starts high (~38), drops slowly to ~30 at 300bp
    r1_mean = 38 - (positions / 300.0) ** 1.8 * 10
    r1_q25 = r1_mean - 2.5
    r1_q75 = r1_mean + 1.5
    
    # R2: Starts high (~37), drops faster to ~20 at 300bp
    r2_mean = 37 - (positions / 300.0) ** 1.5 * 18
    r2_q25 = r2_mean - 3.5
    r2_q75 = r2_mean + 2.0
    
    df_r1 = pd.DataFrame({"Position": positions, "Mean": r1_mean, "Q25": r1_q25, "Q75": r1_q75, "Read": "Forward (R1)"})
    df_r2 = pd.DataFrame({"Position": positions, "Mean": r2_mean, "Q25": r2_q25, "Q75": r2_q75, "Read": "Reverse (R2)"})
    
    return pd.concat([df_r1, df_r2], ignore_index=True)
