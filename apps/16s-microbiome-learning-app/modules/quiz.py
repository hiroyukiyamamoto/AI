import streamlit as st

def render():
    st.header("Step 7: 理解度チェッククイズ & 16S 解析用語集")
    
    tab_quiz, tab_dict = st.tabs(["📝 理解度チェッククイズ", "📖 16S 専門用語辞典 (Glossary)"])
    
    with tab_quiz:
        st.subheader("💡 16S メタ解析 習熟度テスト")
        st.caption("全5問の選択式クイズです。回答を選択して「答え合わせ」を押してください。")
        
        score = 0
        
        # Q1
        st.markdown("#### Q1. FASTQ の Phred クオリティスコア Q = 30 の意味として正しいものはどれ？")
        q1_ans = st.radio("Q1 選択肢", [
            "塩基解読エラー確率が 10% (精度 90%)",
            "塩基解読エラー確率が 1% (精度 99%)",
            "塩基解読エラー確率が 0.1% (精度 99.9%)",
            "塩基解読エラー確率が 0.01% (精度 99.99%)"
        ], index=None, key="q1")
        
        # Q2
        st.markdown("#### Q2. 従来の手法である 97% OTU と比較した現代標準 ASV (DADA2 / Deblur) の主な強みは？")
        q2_ans = st.radio("Q2 選択肢", [
            "クラスタリング計算時間が 100倍速い",
            "配列のエラー確率モデルを学習し、1塩基の違いを正確に区別できる",
            "アンプリコンシーケンスではなくホールメタゲノム解析専用である",
            "データベース参照が不要で、必ず「種名」まで100%特定できる"
        ], index=None, key="q2")
        
        # Q3
        st.markdown("#### Q3. サンプル内の菌種の多様性・複雑さを表す α多様性指標のうち、種数だけでなく「均等度 (Evenness)」を大きく考慮する指標は？")
        q3_ans = st.radio("Q3 選択肢", [
            "Chao1 指標",
            "Observed ASVs (検出種数)",
            "Shannon インデックス",
            "Bray-Curtis 距離"
        ], index=None, key="q3")
        
        # Q4
        st.markdown("#### Q4. サンプル群間の菌叢全体の構成の違い (β多様性) を統計的に多変量比較・検定する手法として標準的なものは？")
        q4_ans = st.radio("Q4 選択肢", [
            "PERMANOVA (Adonis)",
            "Student's t-test",
            "Pearson 相関係数",
            "Chi-Square (カイ二乗) 検定"
        ], index=None, key="q4")
        
        # Q5
        st.markdown("#### Q5. 多重統計検定において、偽陽性 (Type I error) の増大を防ぐために行う p-value 補正法は？")
        q5_ans = st.radio("Q5 選択肢", [
            "Principal Component Analysis (PCA)",
            "FDR (Benjamini-Hochberg 補正 / q-value)",
            "Log2 Fold Change 変換",
            "Min-Max Normalization"
        ], index=None, key="q5")
        
        if st.button("正解チェック (Check Answers)", type="primary"):
            c1 = (q1_ans == "塩基解読エラー確率が 0.1% (精度 99.9%)")
            c2 = (q2_ans == "配列のエラー確率モデルを学習し、1塩基の違いを正確に区別できる")
            c3 = (q3_ans == "Shannon インデックス")
            c4 = (q4_ans == "PERMANOVA (Adonis)")
            c5 = (q5_ans == "FDR (Benjamini-Hochberg 補正 / q-value)")
            
            total_correct = sum([c1, c2, c3, c4, c5])
            
            if total_correct == 5:
                st.balloons()
                st.success(f"🎉 パーフェクト！ 5 / 5 問正解です！ 16Sメタ解析のマスターレベルです！")
            else:
                st.info(f"📊 得点: {total_correct} / 5 問正解")
                
            st.markdown(r"""
            * **Q1**: {'✅ 正解' if c1 else '❌ 不正解'} ($Q = -10 \log_{10} P \rightarrow Q=30$ は Error rate $10^{-3} = 0.1\%$)
            * **Q2**: {'✅ 正解' if c2 else '❌ 不正解'} (ASVは統計的エラーモデルにより1塩基多型を認識可能)
            * **Q3**: {'✅ 正解' if c3 else '❌ 不正解'} (Shannon 指標は豊かさ(Richness)と均等度(Evenness)の両方を評価)
            * **Q4**: {'✅ 正解' if c4 else '❌ 不正解'} (PERMANOVA は距離行列に基づく非パラメトリック多変量分散分析)
            * **Q5**: {'✅ 正解' if c5 else '❌ 不正解'} (多数の菌種を同時検定する際は Benjamini-Hochberg 法による FDR (q-value) 補正が必須)
            """)

    with tab_dict:
        st.subheader("📖 16S メタ解析 専門用語辞典")
        
        search_kw = st.text_input("用語検索 (Search Term)", "")
        
        terms = {
            "16S rRNA 遺伝子": "原核生物 (細菌・古細菌) のリボソーム小サブユニットをコードする遺伝子。全細菌に保存された共通領域と、種ごとに異なる9つのハイパーバリアブル領域 (V1-V9) を持ち、細菌同定のバーコードとして利用される。",
            "ASV (Amplicon Sequence Variant)": "アンプリコン配列バリアント。DADA2などの統計的エラーモデルによりシーケンスエラーを除去した、1塩基解像度の正確な生物学的配列。従来の 97% OTU に代わる現代標準。",
            "Phred Quality Score (Q)": "シーケンサーが各塩基をどれだけ正確に読めたかを示す指標。Q30 は正解率 99.9% (エラー率 0.1%) を意味する。",
            "Chimeras (キメラ配列)": "PCR増幅時に異なる菌の16S断片が結合して生じる人工産物。DADA2等のノイズ除去段階で数学的に検出・除去される。",
            "SILVA / Greengenes": "16S rRNA 遺伝子配列と系統分類情報が登録された代表的な参照データベース。",
            "Rarefaction Curve (希釈曲線)": "サブサンプリング深度に対する検出種数の増加を表す曲線。データ取得量が十分か (飽和しているか) を評価する。",
            "Alpha Diversity (α多様体)": "単一のサンプル内の微生物群集の多様性 (Richness, Shannon, Simpson, Chao1)。",
            "Beta Diversity (β多様体)": "サンプル間での微生物群集構成の「違い」や「距離」(Bray-Curtis, Jaccard, UniFrac)。",
            "PCoA (Principal Coordinate Analysis)": "主座標分析。サンプル間の距離行列 (Bray-Curtis 等) から主要な変動軸を取り出し、2次元または3次元空間にプロットする手法。",
            "PERMANOVA (Adonis)": "距離行列に基づく非パラメトリック多変量分散分析。実験群間で菌叢構造全体に有意差があるかを検定する。",
            "ANCOM-BC / LEfSe": "群間で優位に存在する変動細菌 (バイオマーカー) を同定するための統計解析アルゴリズム。",
            "FDR (False Discovery Rate)": "偽発見率。数百〜数千の菌種を同時に統計検定する際、偽陽性が多発する多重性の問題を抑えるための p-value 補正指標 (q-value)。"
        }
        
        for term, desc in terms.items():
            if search_kw.lower() in term.lower() or search_kw.lower() in desc.lower():
                with st.expander(f"📌 {term}"):
                    st.write(desc)
