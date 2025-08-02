# GitHub Webhook自動トリガーテスト

## 🎯 テスト目的

GitHub PRマージ時にWebhookが自動でCodePipelineをトリガーすることを確認する。

## 📋 テスト内容

### Webhook設定確認
- ✅ GitHub Webhook URL: 設定済み
- ✅ フィルター条件: `refs/heads/main` & `sales_tools`
- ✅ 認証: GITHUB_HMAC
- ✅ ターゲット: `sales-tools-pipeline`

### 期待される動作
1. **このファイル追加** → PRブランチ作成
2. **PRマージ** → GitHub Webhookトリガー
3. **CodePipeline自動実行** → ソース取得・ビルド・デプロイ
4. **Lambda関数更新** → 依存関係込みでデプロイ
5. **動作確認** → 新しいコードで正常動作

## 🧪 実行ログ

### Webhook情報
- **Webhook名**: `sales-tools-codepipeline-webhook-github-webhook`
- **URL**: `https://ap-northeast-1.webhooks.aws/trigger?t=...`
- **ターゲットパイプライン**: `sales-tools-pipeline`
- **ターゲットアクション**: `SourceAction`

### フィルター条件
```json
[
  {
    "jsonPath": "$.ref",
    "matchEquals": "refs/heads/main"
  },
  {
    "jsonPath": "$.repository.name", 
    "matchEquals": "sales_tools"
  }
]
```

## 📊 検証ポイント

- ✅ PRマージ後にWebhookが自動トリガー
- ✅ CodePipelineが自動実行開始
- ✅ CodeBuildで依存関係インストール
- ✅ Lambda関数パッケージ作成・デプロイ
- ✅ Lambda関数が正常動作

## 🔗 監視コマンド

```bash
# パイプライン実行履歴確認
aws codepipeline list-pipeline-executions \
  --pipeline-name sales-tools-pipeline \
  --profile lober-system \
  --region ap-northeast-1 \
  --max-items 3

# Lambda関数テスト
aws lambda invoke \
  --function-name sales-tools-api-function \
  --payload '{"action": "status"}' \
  --profile lober-system \
  --region ap-northeast-1 \
  response.json && cat response.json
```

## 📝 テスト結果

- **実行日時**: 2025-08-02 09:xx:xx
- **PRマージ**: [実行後に記録]
- **Webhook トリガー**: [実行後に記録]
- **パイプライン実行**: [実行後に記録]
- **Lambda更新**: [実行後に記録]
- **動作確認**: [実行後に記録]

---

**このファイルをコミット・プッシュ・PRマージして、Webhook自動トリガーをテストします。**
