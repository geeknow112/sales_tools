#!/bin/bash

# Sales Tools API CodePipeline - PR Merge Detection デプロイスクリプト

set -e

# 設定
STACK_NAME="sales-tools-pr-merge-pipeline"
TEMPLATE_FILE="infrastructure/cloudformation/codepipeline-pr-merge-webhook.yml"
REGION="ap-northeast-1"
AWS_PROFILE="lober-system"

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 既存スタックのクリーンアップ
cleanup_existing_stacks() {
    log_info "既存のWebhookスタックをクリーンアップしています..."
    
    # 既存のWebhook版スタックを削除
    if aws cloudformation describe-stacks --stack-name sales-tools-codepipeline-webhook --profile $AWS_PROFILE --region $REGION > /dev/null 2>&1; then
        log_info "既存のWebhookスタックを削除します..."
        aws cloudformation delete-stack --stack-name sales-tools-codepipeline-webhook --profile $AWS_PROFILE --region $REGION
        log_info "Webhookスタック削除を開始しました（バックグラウンドで実行中）"
    fi
}

# パラメータチェック
check_parameters() {
    log_info "パラメータをチェックしています..."
    
    if [ -z "$GITHUB_TOKEN" ]; then
        log_error "GITHUB_TOKEN環境変数が設定されていません"
        echo "export GITHUB_TOKEN=your_github_token"
        exit 1
    fi
    
    if [ -z "$SALES_TOOLS_API_KEY" ]; then
        log_error "SALES_TOOLS_API_KEY環境変数が設定されていません"
        echo "export SALES_TOOLS_API_KEY=your_api_key"
        exit 1
    fi
    
    log_success "パラメータチェック完了"
}

# AWS認証確認
check_aws_auth() {
    log_info "AWS認証を確認しています (Profile: $AWS_PROFILE)..."
    
    if ! aws sts get-caller-identity --profile $AWS_PROFILE > /dev/null 2>&1; then
        log_error "AWS認証が設定されていません (Profile: $AWS_PROFILE)"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
    USER_ARN=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Arn --output text)
    log_success "AWS認証確認完了"
    log_info "Account: $ACCOUNT_ID"
    log_info "User: $USER_ARN"
}

# CloudFormationスタックのデプロイ
deploy_stack() {
    log_info "PRマージ検知対応CodePipelineをデプロイしています..."
    
    # スタックが存在するかチェック
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --profile $AWS_PROFILE > /dev/null 2>&1; then
        log_info "既存スタックを更新します: $STACK_NAME"
        OPERATION="update-stack"
    else
        log_info "新しいスタックを作成します: $STACK_NAME"
        OPERATION="create-stack"
    fi
    
    # CloudFormationデプロイ
    aws cloudformation $OPERATION \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters \
            ParameterKey=GitHubOwner,ParameterValue=geeknow112 \
            ParameterKey=GitHubRepo,ParameterValue=sales_tools \
            ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN \
            ParameterKey=SalesToolsApiKey,ParameterValue=$SALES_TOOLS_API_KEY \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --profile $AWS_PROFILE
    
    log_info "CloudFormationスタックの処理を待機しています..."
    
    # スタック処理完了を待機
    if [ "$OPERATION" = "create-stack" ]; then
        aws cloudformation wait stack-create-complete \
            --stack-name $STACK_NAME \
            --region $REGION \
            --profile $AWS_PROFILE
    else
        aws cloudformation wait stack-update-complete \
            --stack-name $STACK_NAME \
            --region $REGION \
            --profile $AWS_PROFILE
    fi
    
    log_success "CloudFormationスタックのデプロイ完了"
}

# 出力情報の表示
show_outputs() {
    log_info "デプロイ結果を取得しています..."
    
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs' \
        --output table)
    
    echo ""
    echo "=== PRマージ検知対応デプロイ完了 ==="
    echo "$OUTPUTS"
    echo ""
    
    # 重要な情報を抽出
    PIPELINE_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineUrl`].OutputValue' \
        --output text)
    
    WEBHOOK_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
        --output text)
    
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    log_success "CodePipeline URL: $PIPELINE_URL"
    log_success "PR Merge Webhook URL: $WEBHOOK_URL"
    log_success "Lambda Function: $LAMBDA_NAME"
}

# Webhook設定の確認
verify_webhook() {
    log_info "PRマージ検知Webhook設定を確認しています..."
    
    # Webhook一覧を取得
    WEBHOOK_INFO=$(aws codepipeline list-webhooks \
        --profile $AWS_PROFILE \
        --region $REGION \
        --query 'webhooks[?definition.name==`sales-tools-pr-merge-pipeline-pr-merge-webhook`]' \
        --output json)
    
    if [ "$WEBHOOK_INFO" != "[]" ] && [ -n "$WEBHOOK_INFO" ]; then
        log_success "PRマージ検知Webhookが正常に設定されました"
        
        # フィルター条件を表示
        echo "Webhook フィルター条件:"
        echo "$WEBHOOK_INFO" | jq -r '.[0].definition.filters[] | "- \(.jsonPath): \(.matchEquals)"'
    else
        log_warning "Webhook設定を確認してください"
    fi
}

# テスト実行
run_tests() {
    log_info "デプロイ後のテストを実行しています..."
    
    # Lambda関数テスト
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    if [ "$LAMBDA_NAME" != "None" ] && [ -n "$LAMBDA_NAME" ]; then
        log_info "Lambda関数テスト実行: $LAMBDA_NAME"
        
        aws lambda invoke \
            --function-name $LAMBDA_NAME \
            --payload '{"action": "status", "test": "pr_merge_setup"}' \
            --profile $AWS_PROFILE \
            --region $REGION \
            response.json > /dev/null 2>&1
        
        if [ -f response.json ]; then
            TEST_RESULT=$(cat response.json)
            if echo "$TEST_RESULT" | grep -q '"statusCode": 200'; then
                log_success "Lambda関数テスト: 成功"
                echo "Response: $TEST_RESULT"
            else
                log_warning "Lambda関数テスト: 要確認"
                echo "Response: $TEST_RESULT"
            fi
            rm -f response.json
        fi
    fi
}

# 使用方法の案内
show_usage_guide() {
    echo ""
    echo "=== 🎉 PRマージ検知対応CodePipeline構築完了！ ==="
    echo ""
    echo "📋 PRマージ後自動デプロイの仕組み:"
    echo "1. GitHub でPRを作成・レビュー"
    echo "2. PRをmainブランチにマージ"
    echo "3. GitHub Webhookがmainブランチへのプッシュを検知"
    echo "4. CodePipelineが自動トリガー"
    echo "5. CodeBuildでテスト・ビルド・デプロイ実行"
    echo "6. Lambda関数が依存関係込みで自動更新"
    echo ""
    echo "🔍 Webhook検知条件:"
    echo "- ブランチ: refs/heads/main"
    echo "- リポジトリ: sales_tools"
    echo "- コミット: すべてのコミットメッセージ"
    echo ""
    echo "🧪 テスト方法:"
    echo "git checkout -b feature/pr-merge-test"
    echo "echo '# Test PR Merge' >> TEST_PR_MERGE.md"
    echo "git add . && git commit -m 'test: PR merge auto trigger'"
    echo "git push origin feature/pr-merge-test"
    echo "# GitHub でPRを作成・マージ"
    echo ""
    echo "📊 監視方法:"
    echo "aws codepipeline list-pipeline-executions \\"
    echo "  --pipeline-name sales-tools-pipeline \\"
    echo "  --profile $AWS_PROFILE --region $REGION \\"
    echo "  --query 'pipelineExecutionSummaries[*].[pipelineExecutionId,status,trigger.triggerType]'"
    echo ""
    log_success "PRマージ後の自動デプロイ準備完了！"
}

# メイン実行
main() {
    echo "=== Sales Tools API CodePipeline - PR Merge Detection ==="
    echo "Profile: $AWS_PROFILE"
    echo "Region: $REGION"
    echo ""
    
    cleanup_existing_stacks
    check_parameters
    check_aws_auth
    deploy_stack
    show_outputs
    verify_webhook
    run_tests
    show_usage_guide
}

# スクリプト実行
main "$@"
