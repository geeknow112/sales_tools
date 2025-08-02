# PR Test: CodePipeline自動デプロイ

## 🎯 テスト目的

GitHub PRを作成してCodePipelineによる自動デプロイが正常に動作することを確認する。

## 📋 テスト内容

### 変更内容
- Lambda関数に`pr_test`情報を追加
- バージョン: 1.1.0
- 機能: CodePipeline PR Test

### 期待される動作
1. **PR作成** → GitHub Actionsでテスト実行 (設定済みの場合)
2. **PRマージ** → CodePipelineが自動トリガー
3. **CodeBuild** → テスト・ビルド・パッケージ作成
4. **Lambda更新** → 新しいコードがデプロイ
5. **動作確認** → API呼び出しで新機能確認

## 🧪 テスト手順

### 1. PR作成
```bash
git checkout -b feature/test-codepipeline-pr
# 変更を追加
git add .
git commit -m "test: CodePipeline PR自動デプロイテスト"
git push origin feature/test-codepipeline-pr
```

### 2. GitHub でPR作成
- base: main
- compare: feature/test-codepipeline-pr
- タイトル: "test: CodePipeline PR自動デプロイテスト"

### 3. PRマージ後の確認
```bash
# Lambda関数テスト
aws lambda invoke \
  --function-name sales-tools-api-function \
  --payload '{"action": "status"}' \
  --profile lober-system \
  --region ap-northeast-1 \
  response.json

# レスポンス確認
cat response.json | jq '.pr_test'
```

### 4. 期待されるレスポンス
```json
{
  "pr_test": {
    "version": "1.1.0",
    "feature": "CodePipeline PR Test",
    "timestamp": "2025-08-02 12:34:56",
    "deployment_method": "GitHub PR → CodePipeline → Lambda"
  }
}
```

## 📊 検証ポイント

- ✅ PRマージ後にCodePipelineが自動実行される
- ✅ CodeBuildでテスト・ビルドが成功する
- ✅ Lambda関数が新しいコードで更新される
- ✅ API呼び出しで新機能が動作する
- ✅ パイプライン実行履歴に記録される

## 🔗 関連リンク

- **CodePipeline**: https://console.aws.amazon.com/codesuite/codepipeline/pipelines/sales-tools-pipeline/view
- **Lambda関数**: https://console.aws.amazon.com/lambda/home?region=ap-northeast-1#/functions/sales-tools-api-function
- **GitHub Repository**: https://github.com/geeknow112/sales_tools

## 📝 テスト結果

- **実行日時**: 2025-08-02
- **実行者**: システム管理者
- **結果**: [テスト実行後に記録]
