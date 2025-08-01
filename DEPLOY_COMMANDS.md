# CodePipelineデプロイコマンド

## 🚀 ワンライナーデプロイ

```bash
# 1. 環境変数設定
export GITHUB_TOKEN="your_github_personal_access_token"
export SALES_TOOLS_API_KEY="your_actual_sales_tools_api_key"

# 2. デプロイ実行
./scripts/deploy-pipeline.sh
```

## 📋 手動デプロイ（AWS CLIコマンド）

```bash
# CloudFormationスタック作成
aws cloudformation create-stack \
  --stack-name sales-tools-codepipeline \
  --template-body file://infrastructure/cloudformation/codepipeline-stack.yml \
  --parameters \
    ParameterKey=GitHubOwner,ParameterValue=geeknow112 \
    ParameterKey=GitHubRepo,ParameterValue=sales_tools \
    ParameterKey=GitHubToken,ParameterValue=your_github_personal_access_token \
    ParameterKey=SalesToolsApiKey,ParameterValue=your_actual_sales_tools_api_key \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1

# デプロイ完了を待機
aws cloudformation wait stack-create-complete \
  --stack-name sales-tools-codepipeline \
  --region ap-northeast-1

# 結果確認
aws cloudformation describe-stacks \
  --stack-name sales-tools-codepipeline \
  --region ap-northeast-1 \
  --query 'Stacks[0].Outputs' \
  --output table
```

## 🔗 作成されるリソース

### CodePipeline
- **名前**: `sales-tools-pipeline`
- **ソース**: GitHub (geeknow112/sales_tools)
- **ビルド**: CodeBuild
- **デプロイ**: Lambda関数更新

### Lambda関数
- **名前**: `sales-tools-api-function`
- **ランタイム**: Python 3.9
- **ハンドラー**: `lambda_function.lambda_handler`

### API Gateway
- **名前**: `sales-tools-api`
- **エンドポイント**: `/api` (POST)
- **統合**: Lambda Proxy

### S3バケット
- **用途**: CodePipelineアーティファクト保存
- **暗号化**: AES256

## 📊 デプロイ後の確認

### 1. CodePipelineの確認
```bash
# パイプライン一覧
aws codepipeline list-pipelines

# パイプライン詳細
aws codepipeline get-pipeline --name sales-tools-pipeline
```

### 2. Lambda関数の確認
```bash
# 関数一覧
aws lambda list-functions --query 'Functions[?contains(FunctionName, `sales-tools`)]'

# 関数詳細
aws lambda get-function --function-name sales-tools-api-function
```

### 3. API Gatewayの確認
```bash
# API一覧
aws apigateway get-rest-apis --query 'items[?contains(name, `sales-tools`)]'
```

## 🧪 テスト実行

### Lambda関数テスト
```bash
# 直接テスト
aws lambda invoke \
  --function-name sales-tools-api-function \
  --payload '{"action": "status"}' \
  response.json && cat response.json
```

### API Gatewayテスト
```bash
# API URL取得
API_URL=$(aws cloudformation describe-stacks \
  --stack-name sales-tools-codepipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

# APIテスト
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}'
```

## 🔄 パイプライン実行

### 手動実行
```bash
# パイプライン手動実行
aws codepipeline start-pipeline-execution \
  --name sales-tools-pipeline

# 実行状況確認
aws codepipeline list-pipeline-executions \
  --pipeline-name sales-tools-pipeline \
  --max-items 1
```

### GitHub連携確認
```bash
# mainブランチにプッシュしてパイプライン自動実行を確認
git checkout main
git pull origin main
echo "# Test" >> test.md
git add test.md
git commit -m "test: パイプライン自動実行テスト"
git push origin main
```

## 🚨 トラブルシューティング

### よくあるエラー

#### 1. GitHub Token権限不足
```
Error: Could not access repository
```
**解決**: GitHubトークンに`repo`スコープを追加

#### 2. IAM権限不足
```
Error: User is not authorized to perform: cloudformation:CreateStack
```
**解決**: IAMユーザーにCloudFormation権限を追加

#### 3. Lambda関数更新失敗
```
Error: The role defined for the function cannot be assumed by Lambda
```
**解決**: Lambda実行ロールの信頼関係を確認

## 📞 サポート

問題が発生した場合：
1. CloudFormationスタックのイベントを確認
2. CodeBuildのログを確認
3. Lambda関数のCloudWatch Logsを確認
