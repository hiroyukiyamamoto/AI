# Immune Cell Learning

免疫細胞の特徴をカードで学び、シナリオとクイズで復習する教材です。FastAPIが静的画面と学習用データを配信します。

## 起動

Python 3.12で、このディレクトリから実行します。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

`http://127.0.0.1:8000`を開きます。

## 公開版の内容

- 学習用の細胞説明・シナリオ・設問をコード内に保持し、研究データや個人情報は同梱しません。
- APIキー・DB・外部AIは不要です。APIは学習用データの読み取りのみです。
- 見た目とアイコンのため、ブラウザはTailwind CSS 3.4.17とLucide 0.468.0をCDNから取得します。版とSRIハッシュを固定しています。インターネット接続がない場合は表示が簡素になることがあります。
- 教材として単純化した表現を含みます。細胞カードの能力値は学習用の比喩で、実測値ではありません。
- 現版はローカルデモ向けです。Tailwind Play CDNの利用を含むため、本番ホスティングの前にはCSSの事前ビルド等が必要です。

依存ライブラリ・CDNの条件は[公開範囲の説明](../../PUBLICATION.md)を参照してください。
