# Sales Tools API - プロジェクト状況サマリー

## 🎯 プロジェクト概要

Sales Tools APIを使用したAmazon商品価格分析システム。
ECS Fargate + CodePipeline による完全自動デプロイ環境を構築済み。

## ✅ 現在の稼働状況

### ECSデプロイ環境
- **ECSクラスター**: `sales-tools-cluster` - ✅ 稼働中
- **現在のタスク**: `c9dcf30e1c9b42beb38c38912a7d1728` - ✅ RUNNING
- **パブリックIP**: `18.183.208.157:8080`
- **アプリケーションバージョン**: `1.1.0`
- **ヘルスチェック**: http://18.183.208.157:8080/health - ✅ 正常

### CI/CDパイプライン
- **CodePipeline**: `ecs-standard-3stage-pipeline-fixed` - ✅ 稼働中
- **最新実行**: `630e9131-9237-4b72-be7a-9559fffdc4aa` - ✅ Succeeded
- **GitHub Webhook**: ✅ 自動トリガー設定済み
- **デプロイフロー**: PR Merge → Webhook → CodePipeline → ECS Deploy

## 📁 プロジェクト構成

### 重要ファイル
```
├── src/
│   ├── app.py                 # ECS Fargate Flask アプリケーション
│   ├── lambda_function.py     # Lambda関数（参考用）
│   ├── sales_tools_api_client.py
│   └── manual_login_auto_tracking.py
├── infrastructure/
│   └── cloudformation/
│       ├── ecs-standard-3stage-pipeline-fixed.yml  # 現在使用中のパイプライン
│       ├── sales-tools-ecs.yml                     # ECSクラスター定義
│       └── keepa-api-stack.yml                     # 基本スタック
├── Dockerfile                 # ECS用Dockerファイル
├── buildspec.yml             # CodeBuild設定
├── requirements-ecs.txt      # ECS用Python依存関係
└── README.md                 # プロジェクト説明
```

### 設定ファイル
- `.env` - 環境変数（ローカル開発用）
- `.env.example` - 環境変数テンプレート
- `requirements.txt` - Python依存関係（汎用）

## 🔧 技術スタック

### インフラ
- **AWS ECS Fargate**: コンテナ実行環境
- **AWS CodePipeline**: CI/CDパイプライン
- **AWS CodeBuild**: ビルド・デプロイ
- **Amazon ECR**: Dockerイメージレジストリ
- **GitHub Webhook**: 自動トリガー

### アプリケーション
- **Python 3.9**: ランタイム
- **Flask**: Webフレームワーク
- **Docker**: コンテナ化
- **Sales Tools API**: 商品価格データ取得

## 🚀 デプロイフロー

### 自動デプロイ手順
1. **開発**: ローカルでコード変更
2. **PR作成**: GitHub上でPull Request作成
3. **PR承認・マージ**: mainブランチにマージ
4. **自動実行**: GitHub Webhook → CodePipeline トリガー
5. **ビルド**: CodeBuild でDockerイメージビルド・ECRプッシュ
6. **デプロイ**: 既存ECSタスク停止 → 新タスク起動
7. **確認**: 新バージョンでの動作確認

### 手動確認コマンド
```bash
# パイプライン実行状況
aws codepipeline list-pipeline-executions --pipeline-name ecs-standard-3stage-pipeline-fixed --max-items 1 --profile lober-system --region ap-northeast-1

# ECSタスク状況
aws ecs list-tasks --cluster sales-tools-cluster --desired-status RUNNING --profile lober-system --region ap-northeast-1

# アプリケーション動作確認
curl -s http://18.183.208.157:8080/status
```

## 🔍 API エンドポイント

### 利用可能なエンドポイント
- `GET /health` - ヘルスチェック
- `GET /status` - システム状況
- `POST /analyze` - 商品価格分析
- `GET /product/<asin>` - 商品情報取得

### 使用例
```bash
# ヘルスチェック
curl http://18.183.208.157:8080/health

# システム状況
curl http://18.183.208.157:8080/status

# 商品分析（POST）
curl -X POST http://18.183.208.157:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0B5SDFLTB", "domain": "JP"}'
```

## ⚠️ 重要な注意事項

### セキュリティ
- **セキュリティグループ**: ポート8080が開放済み（`sg-83a74ee6`）
- **パブリックアクセス**: インターネットからアクセス可能
- **API認証**: 現在は認証なし（開発段階）

### コスト管理
- **ECS Fargate**: 継続実行中（月額約$10-20）
- **CodePipeline**: 実行時のみ課金
- **ECR**: イメージストレージ費用

### Docker Hub Rate Limit対策
- **ベースイメージ**: `public.ecr.aws/docker/library/python:3.9-slim` 使用
- **理由**: Docker Hub Rate Limit回避

## 🎯 次回作業候補

### 優先度1: 運用改善
- [ ] ECSサービス化（単発タスク → サービス）
- [ ] Application Load Balancer設定
- [ ] CloudWatch監視・アラート設定
- [ ] API認証機能追加

### 優先度2: 機能拡張
- [ ] Sales Tools API機能の本格実装
- [ ] データベース連携
- [ ] バッチ処理機能
- [ ] 管理画面開発

### 優先度3: 開発効率化
- [ ] ローカル開発環境の Docker Compose化
- [ ] テスト自動化
- [ ] ログ集約・分析
- [ ] パフォーマンス監視

## 📞 トラブルシューティング

### よくある問題
1. **ECSタスクが起動しない**
   - セキュリティグループ設定確認
   - タスク定義の設定確認
   - CloudWatch Logsでエラー確認

2. **CodePipelineが失敗する**
   - GitHub Webhook設定確認
   - CodeBuild権限確認
   - ECR認証確認

3. **アプリケーションにアクセスできない**
   - パブリックIP変更確認
   - セキュリティグループ設定確認
   - ECSタスク状態確認

### 緊急時の対応
```bash
# ECSタスクの強制再起動
aws ecs stop-task --cluster sales-tools-cluster --task [TASK_ARN] --profile lober-system --region ap-northeast-1

# パイプラインの手動実行
aws codepipeline start-pipeline-execution --name ecs-standard-3stage-pipeline-fixed --profile lober-system --region ap-northeast-1
```

---

**最終更新**: 2025-08-02 14:49:00 JST  
**ステータス**: ✅ 本番稼働中  
**担当者**: システム管理者
