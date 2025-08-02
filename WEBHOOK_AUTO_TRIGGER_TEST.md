# PRマージ後Webhook自動トリガーテスト

## 🎯 テスト目的

PRマージ後にGitHub WebhookがCodePipelineを自動トリガーし、Lambdaデプロイフローが正常に動作することを確認する。

## 📋 テスト内容

### 現在の設定状況
- ✅ **Webhook名**: `sales-tools-pr-merge-pipeline-pr-merge-webhook`
- ✅ **フィルター条件**: 
  - `$.ref` = `refs/heads/main`
  - `$.repository.name` = `sales_tools`
  - `$.head_commit.message` = `*`
- ✅ **前回手動実行**: 成功（f6e66687-da72-412a-8cf1-86ca4c629f83）

### 変更内容
- **Lambda関数**: `pr_test.version` を `1.2.0` に更新
- **テスト機能**: Webhook自動トリガー検証用の情報追加
- **テストID**: `webhook-auto-trigger-test-1754095832`

## 🔄 期待される動作フロー

### 1. PRマージ実行
- このブランチをmainにマージ
- GitHub側でmainブランチが更新される

### 2. Webhook自動検知
- GitHub WebhookがAWS CodePipelineにイベント送信
- フィルター条件をすべて満たすことを確認
- CodePipelineが自動トリガー

### 3. CodePipeline実行
- **Source Stage**: GitHubから最新コード取得
- **Build Stage**: CodeBuildで依存関係インストール・テスト・パッケージ作成

### 4. Lambda自動デプロイ
- **パッケージ作成**: 依存関係込みのzipファイル
- **Lambda更新**: `aws lambda update-function-code`
- **設定更新**: 環境変数・タイムアウト・メモリ設定

## 📊 Lambdaデプロイフローの可視化

### CodePipelineでのLambda更新プロセス

#### **Build Stage内での処理**
```yaml
post_build:
  commands:
    - echo "=== Deploying to Lambda ==="
    - aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://lambda-deployment.zip
    - aws lambda update-function-configuration --function-name $LAMBDA_FUNCTION_NAME --environment Variables="{...}"
    - echo "✅ Lambda function updated successfully!"
```

#### **確認可能な場所**
1. **CodeBuild Logs**: `/aws/codebuild/sales-tools-pr-merge-pipeline-build`
2. **Lambda Console**: 関数の「Last modified」時刻
3. **CloudWatch Logs**: Lambda実行ログ
4. **CodePipeline Console**: Build Stageの詳細

## 🧪 検証ポイント

### PRマージ後の確認項目
- ✅ **Webhookトリガー**: `trigger.triggerType` = `Webhook`
- ✅ **パイプライン実行**: ステータス = `Succeeded`
- ✅ **Lambda更新**: `LastModified` 時刻が更新
- ✅ **新機能動作**: API呼び出しで `version: 1.2.0` 確認

### 監視コマンド
```bash
# パイプライン実行確認
aws codepipeline list-pipeline-executions --pipeline-name sales-tools-pipeline --profile lober-system --region ap-northeast-1

# Lambda関数確認
aws lambda get-function --function-name sales-tools-api-function --profile lober-system --region ap-northeast-1

# Lambda関数テスト
aws lambda invoke --function-name sales-tools-api-function --payload '{"action": "status"}' --profile lober-system response.json
```

## 📝 テスト実行ログ

### 実行前状態
- **日時**: 2025-08-02 09:50:xx
- **最新パイプライン**: f6e66687-da72-412a-8cf1-86ca4c629f83 (手動実行・成功)
- **Lambda最終更新**: 2025-08-02T00:46:38.000+0000

### PRマージ実行
- **マージ日時**: [実行後に記録]
- **コミットハッシュ**: [実行後に記録]

### Webhook自動トリガー結果
- **トリガー検知**: [実行後に記録]
- **パイプライン実行ID**: [実行後に記録]
- **実行結果**: [実行後に記録]

### Lambda更新結果
- **更新成功**: [実行後に記録]
- **新バージョン動作**: [実行後に記録]

---

**このファイルをコミット・プッシュ・PRマージして、完全な自動デプロイフローをテストします。**

## 🎉 期待される最終結果

PRマージ → GitHub Webhook → CodePipeline自動実行 → Lambda自動更新 → 新機能利用可能
