# Keepa API Web UI テストツール

ローカル環境でKeepa APIの動作をテストするためのWeb UIツールです。

## 機能

- 🔍 API接続テスト
- 📊 商品価格分析
- 📝 商品情報取得
- 🌐 ブラウザベースの直感的なUI

## セットアップ

### 1. 依存関係のインストール

```bash
# Web UIディレクトリに移動
cd web_ui

# 必要なパッケージをインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
# プロジェクトルートに.envファイルを作成
cd ..
cp .env.example .env

# .envファイルを編集してKeepa APIキーを設定
# KEEPA_API_KEY=your_actual_api_key_here
```

### 3. Web UI起動

```bash
# Web UIディレクトリで起動
cd web_ui
python run.py

# または直接app.pyを実行
python app.py
```

## 使用方法

1. **ブラウザでアクセス**
   - http://localhost:5000 を開く

2. **API接続テスト**
   - 「API接続テスト」ボタンをクリック
   - 環境変数の設定状況を確認

3. **商品情報テスト**
   - ASIN入力（例: B0B5SDFLTB）
   - ドメイン選択（日本: JP）
   - アクション選択（価格分析 or 商品情報取得）
   - 「実行」ボタンをクリック

## 画面構成

### メイン画面
- API接続ステータス表示
- 商品検索フォーム
- 実行結果表示エリア

### 機能詳細

#### 価格分析 (analyze)
```json
{
  "asin": "B0B5SDFLTB",
  "title": "商品名",
  "current_price": 1500.0,
  "currency": "JPY",
  "min_price": 1200.0,
  "max_price": 2000.0,
  "avg_price": 1600.0,
  "analysis_date": "2025-08-01 15:00:00"
}
```

#### 商品情報取得 (info)
```json
{
  "asin": "B0B5SDFLTB",
  "title": "商品名",
  "current_price": 1500.0
}
```

## トラブルシューティング

### よくある問題

1. **「KEEPA_API_KEY環境変数が設定されていません」**
   - `.env`ファイルの作成・設定を確認
   - APIキーの有効性を確認

2. **「Keepa APIクライアントが利用できません」**
   - `pip install keepa`でパッケージをインストール
   - Python環境の確認

3. **「商品が見つかりません」**
   - ASINの正確性を確認
   - ドメイン設定の確認

4. **レート制限エラー**
   - API呼び出し頻度を調整
   - Keepa APIプランの確認

## 開発者向け情報

### ファイル構成
```
web_ui/
├── app.py              # Flaskアプリケーション
├── run.py              # 起動スクリプト
├── requirements.txt    # 依存関係
├── templates/
│   └── index.html     # HTMLテンプレート
└── README.md          # このファイル
```

### API エンドポイント

- `GET /`: メインページ
- `POST /api/product`: 商品情報取得
- `GET /api/test`: API接続テスト

### カスタマイズ

HTMLテンプレート(`templates/index.html`)を編集することで、UIをカスタマイズできます。

## 注意事項

- このツールは開発・テスト用途です
- 本番環境での使用は推奨されません
- Keepa APIの利用規約を遵守してください
