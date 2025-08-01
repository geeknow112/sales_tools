# Sales Tools API Integration Project

Sales Tools APIを使用した商品価格分析システム

## 概要

このプロジェクトは、Sales Tools APIを使用してAmazon商品の価格情報を取得・分析するシステムです。
AWS Lambda、CodePipeline、GitHub Actionsを使用したCI/CDパイプラインを構築しています。

## アーキテクチャ

```
GitHub → GitHub Actions → CodePipeline → CodeBuild → Lambda
```

## 機能

- Amazon商品の価格情報取得
- 価格履歴の分析
- 価格トレンドの可視化
- REST API形式でのデータ提供
- **商品トラッキング自動設定**（新機能）

## 商品トラッキング自動設定

### 🎯 手動ログイン + 自動トラッキング設定

ログインブロックを回避するため、ログインは手動で行い、トラッキング設定のみを自動化する手法を採用。

#### 実行方法

```bash
# 仮想環境アクティベート
source venv/bin/activate

# 必要なパッケージインストール
pip install selenium webdriver-manager

# トラッキング設定実行
cd src
python manual_login_auto_tracking.py
```

#### 実行フロー

1. **🖥️ Chromeブラウザ起動**
2. **🏠 Sales Toolsサイト表示**
3. **🔐 手動ログイン**（ユーザーが手動で実行）
4. **🤖 自動トラッキング設定**
   - 商品ページアクセス
   - Trackタブクリック
   - Amazon価格トラッキング有効化
   - 閾値95%設定
   - 送信ボタンクリック

#### 特徴

- **ブロック回避**: 手動ログインによりセキュリティ制限を回避
- **確実性**: 人間の操作とSelenium自動化の組み合わせ
- **フォールバック**: 自動化失敗時は手動操作を案内
- **詳細ログ**: 各ステップの進行状況を表示

#### 成功実績

- **対象商品**: B08CDYX378（コカ・コーラ カナダドライ）
- **実行結果**: ✅ 成功
- **トラッキング設定**: 完了
- **証跡**: スクリーンショット・ログ保存

## セットアップ

### 1. 前提条件

- Python 3.9+
- AWS CLI設定済み
- Sales Tools APIキー
- GitHub Personal Access Token
- **Chrome WebDriver**（トラッキング設定用）

### 2. ローカル環境構築

```bash
# リポジトリクローン
git clone <repository-url>
cd sales_tools

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# Selenium関連パッケージ（トラッキング設定用）
pip install selenium webdriver-manager

# 環境変数設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 3. AWS インフラ構築

```bash
# CloudFormationスタックデプロイ
aws cloudformation create-stack \
  --stack-name sales-tools-api-stack \
  --template-body file://infrastructure/cloudformation/sales-tools-api-stack.yml \
  --parameters ParameterKey=SalesToolsApiKey,ParameterValue=YOUR_API_KEY \
               ParameterKey=GitHubToken,ParameterValue=YOUR_GITHUB_TOKEN \
               ParameterKey=GitHubOwner,ParameterValue=YOUR_GITHUB_USERNAME \
               ParameterKey=GitHubRepo,ParameterValue=sales_tools \
  --capabilities CAPABILITY_IAM
```

### 4. GitHub Secrets設定

以下のSecretsをGitHubリポジトリに設定：

- `SALES_TOOLS_API_KEY_TEST`: テスト用Sales Tools APIキー
- `AWS_ACCESS_KEY_ID`: AWS アクセスキー
- `AWS_SECRET_ACCESS_KEY`: AWS シークレットキー

## 使用方法

### ローカルテスト

```bash
# 単体テスト実行
python -m pytest tests/unit/ -v

# Lambda関数のローカルテスト
cd src
python lambda_function.py
```

### 商品トラッキング設定

```bash
# 手動ログイン + 自動トラッキング設定
cd src
python manual_login_auto_tracking.py
```

### API呼び出し例

```python
import json

# 価格分析
event = {
    'asin': 'B0B5SDFLTB',
    'domain': 'JP',
    'action': 'analyze'
}

# 商品情報取得
event = {
    'asin': 'B0B5SDFLTB',
    'action': 'info'
}
```

## CI/CD パイプライン

### 🚀 自動デプロイフロー

```
PR作成 → GitHub Actions (テスト) → mainマージ → CodePipeline → Lambda デプロイ
```

#### GitHub Actions
- **プルリクエスト時**: 自動テスト実行
- **mainブランチプッシュ時**: CodePipelineトリガー

#### CodePipeline
1. **Source**: GitHubからソースコード取得
2. **Build**: CodeBuildでテスト・ビルド・デプロイ

### 📋 セットアップ手順

#### 1. GitHub Secrets設定
```bash
# 必要なSecrets
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
SALES_TOOLS_API_KEY_TEST=your_test_api_key
```

#### 2. CodePipelineデプロイ
```bash
# 環境変数設定
export GITHUB_TOKEN=your_github_token
export SALES_TOOLS_API_KEY=your_api_key

# パイプラインデプロイ
./scripts/deploy-pipeline.sh
```

#### 3. 自動デプロイ確認
```bash
# テスト用ブランチ作成
git checkout -b feature/test-deploy
git push origin feature/test-deploy

# PRを作成してテスト実行を確認
# mainにマージして自動デプロイを確認
```

## 費用見積もり

月額約$3.02（約450円）
- CodePipeline: $1.00
- CodeBuild: $0.50
- Lambda: $0.10
- その他: $1.42

※Sales Tools API費用は別途

## 注意事項

- Sales Tools APIの利用規約を遵守してください
- レート制限に注意してAPI呼び出しを行ってください
- 本番環境での直接デプロイは避け、必ずPR経由で行ってください
- **トラッキング設定は手動ログインが必要です**

## トラブルシューティング

### よくある問題

1. **APIキーエラー**: 環境変数の設定を確認
2. **レート制限**: API呼び出し頻度を調整
3. **Lambda実行エラー**: CloudWatch Logsを確認
4. **Seleniumエラー**: ChromeDriverのバージョン確認
5. **ログインブロック**: 手動ログイン方式を使用

## ライセンス

このプロジェクトは社内利用を目的としています。
