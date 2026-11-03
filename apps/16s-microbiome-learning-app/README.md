# 16S Microbiome Learning

16S rRNA解析のQC、ノイズ除去の考え方、分類、α・β多様性、群間比較を体験するStreamlit教材です。

## 起動

Python 3.12で、このディレクトリから実行します。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

表示された`http://127.0.0.1:8501`を開きます。APIキー・外部データのダウンロードは不要です。

## データ

3種類の既定プリセットは乱数生成した合成データです。年齢やBMIを含め実在する被験者の情報ではありません。QC・Denoising等の表示は説明用のシミュレーションで、実際のFASTQ処理ではありません。群間比較はMann–Whitney検定とFDR補正を用い、LEfSe等の表示には説明用の近似を含みます。

CSV入力は各2 MiB以下、4〜100検体、2〜500 ASV、各群2検体以上の2群に制限しています。

Metadata CSV:

```csv
SampleID,Group
S1,A
S2,A
S3,B
S4,B
```

Counts CSV:

```csv
SampleID,ASV1,ASV2
S1,12,3
S2,10,5
S3,4,11
S4,3,12
```

ID・Groupは英数字で始まる80文字以下の英数字・空白・`_`・`.`・`-`にしてください。Metadataに追加の個人属性列は受け付けません。カウントは0〜10億の有限な整数で、各検体の合計は正である必要があります。

個人情報・非公開の研究データは入力しないでください。入力は起動したサーバーのメモリで処理されます。公開サーバーへの運用はこのデモの対象外です。
