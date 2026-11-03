# AIアプリ・ポートフォリオ

生命科学を中心とした、インタラクティブな学習アプリのソースコードを公開しています。
現在の公開版はローカル実行用です。ホスティングやオンラインデモのデプロイは行っていません。

| アプリ | 概要 | 起動方法 | ソース |
|---|---|---|---|
| 16S Microbiome Learning | 合成データでQC・菌叢構成・多様性・群間比較を学ぶStreamlit教材 | `streamlit run app.py` | [コードと手順](apps/16s-microbiome-learning-app/) |
| Immune Cell Learning | 免疫細胞の特徴・シナリオ・クイズを学ぶFastAPI教材 | `uvicorn main:app --host 127.0.0.1 --port 8000` | [コードと手順](apps/immune-app/) |

## はじめ方

Python 3.12を使用し、各アプリのディレクトリで仮想環境を作成してください。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

起動コマンド、データの扱い、制限は各アプリのREADMEを参照してください。

## 公開範囲と利用条件

- 既定データは生成した合成データまたはアプリ内の学習用説明・設問です。研究データセット、画像、PDF、データベースは同梱していません。
- 医療判断や検証済みの研究解析の代替を目的とするものではありません。
- このリポジトリ全体に一律のOSSライセンスは付与していません。ソースコードの再利用条件は別途確認してください。
- 外部ライブラリ・CDNのライセンスと利用条件は各提供元に従います。[依存関係・公開範囲](PUBLICATION.md)
