# PRマージ検知自動デプロイテスト

## 🎯 テスト目的

PRマージ完了後にWebhookが自動でCodePipelineをトリガーし、Lambda関数が正常に更新されることを確認する。

## 📋 設定確認

### Webhook設定
- ✅ **Webhook名**: `sales-tools-pr-merge-pipeline-pr-merge-webhook`
- ✅ **ターゲット**: `sales-tools-pipeline`
- ✅ **認証**: GITHUB_HMAC

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
  },
  {
    "jsonPath": "$.head_commit.message",
    "matchEquals": "*"
  }
]
```

## 🔄 テストフロー

### 1. PRマージ前の状態
- CodePipeline: 待機中
- Lambda関数: 現在のバージョン
- Webhook: 監視中

### 2. PRマージ実行
- このブランチをmainにマージ
- GitHub Webhookがmainブランチへのプッシュを検知
- フィルター条件をすべて満たす場合にトリガー

### 3. 期待される動作
1. **Webhook検知**: mainブランチへのプッシュ
2. **CodePipeline起動**: 自動トリガー
3. **ソース取得**: GitHubから最新コード取得
4. **ビルド実行**: 依存関係インストール・テスト・パッケージ作成
5. **Lambda更新**: 新しいコードでデプロイ
6. **動作確認**: API呼び出しで正常動作確認

## 🧪 検証ポイント

- ✅ PRマージ後にWebhookが自動トリガー
- ✅ CodePipelineが `Webhook` トリガーで実行開始
- ✅ CodeBuildで依存関係が正常にインストール
- ✅ Lambda関数パッケージが正常に作成
- ✅ Lambda関数が新しいコードで更新
- ✅ API呼び出しで新機能が動作

## 📊 監視コマンド

### パイプライン実行確認
```bash
aws codepipeline list-pipeline-executions \
  --pipeline-name sales-tools-pipeline \
  --profile lober-system \
  --region ap-northeast-1 \
  --max-items 3 \
  --query 'pipelineExecutionSummaries[*].[pipelineExecutionId,status,trigger.triggerType,startTime]'
```

### Lambda関数テスト
```bash
aws lambda invoke \
  --function-name sales-tools-api-function \
  --payload '{"action": "status", "test": "pr_merge_detection"}' \
  --profile lober-system \
  --region ap-northeast-1 \
  response.json && cat response.json
```

## 📝 テスト実行ログ

### 実行前チェック
- **日時**: 2025-08-02 09:xx:xx
- **現在のパイプライン状態**: [確認中]
- **Lambda関数バージョン**: [確認中]

### PRマージ実行
- **マージ日時**: [実行後に記録]
- **コミットハッシュ**: [実行後に記録]
- **Webhookトリガー**: [実行後に記録]

### パイプライン実行結果
- **実行ID**: [実行後に記録]
- **トリガータイプ**: [実行後に記録]
- **実行状態**: [実行後に記録]
- **完了時間**: [実行後に記録]

### Lambda関数更新結果
- **更新成功**: [実行後に記録]
- **新機能動作**: [実行後に記録]
- **API応答**: [実行後に記録]

---

**このファイルをコミット・プッシュ・PRマージして、PRマージ検知自動デプロイをテストします。**

## 🎉 期待される最終結果

PRマージ → Webhook自動検知 → CodePipeline実行 → Lambda更新 → 新機能利用可能
