#!/bin/bash

# Sales Tools API CodePipeline デプロイスクリプト (AWS Profile対応版)

set -e

# 設定
STACK_NAME="sales-tools-codepipeline"
TEMPLATE_FILE="infrastructure/cloudformation/codepipeline-stack.yml"
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
        echo "aws configure --profile $AWS_PROFILE を実行してください"
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
    log_info "CloudFormationスタックをデプロイしています..."
    
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
    echo "=== デプロイ完了 ==="
    echo "$OUTPUTS"
    echo ""
    
    # 重要な情報を抽出
    PIPELINE_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineUrl`].OutputValue' \
        --output text)
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    log_success "CodePipeline URL: $PIPELINE_URL"
    log_success "API Gateway URL: $API_URL"
    log_success "Lambda Function: $LAMBDA_NAME"
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
        
        TEST_RESULT=$(aws lambda invoke \
            --function-name $LAMBDA_NAME \
            --payload '{"action": "status"}' \
            --region $REGION \
            --profile $AWS_PROFILE \
            response.json 2>/dev/null && cat response.json)
        
        if echo "$TEST_RESULT" | grep -q '"statusCode": 200'; then
            log_success "Lambda関数テスト: 成功"
        else
            log_warning "Lambda関数テスト: 要確認"
            echo "Response: $TEST_RESULT"
        fi
        
        rm -f response.json
    fi
    
    # CodePipelineの初回実行
    PIPELINE_NAME="sales-tools-pipeline"
    log_info "CodePipelineの初回実行をトリガーします..."
    
    aws codepipeline start-pipeline-execution \
        --name $PIPELINE_NAME \
        --region $REGION \
        --profile $AWS_PROFILE > /dev/null 2>&1
    
    log_success "CodePipeline初回実行をトリガーしました"
}

# GitHub Webhook設定案内
setup_webhook_guide() {
    log_info "GitHub連携設定案内"
    echo ""
    echo "=== 次のステップ ==="
    echo "1. GitHub Actions設定:"
    echo "   - Personal Access Tokenに 'workflow' スコープを追加"
    echo "   - .github/workflows/ci-cd.yml を手動で追加"
    echo ""
    echo "2. GitHub Secrets設定:"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - SALES_TOOLS_API_KEY_TEST"
    echo ""
    echo "3. テスト実行:"
    echo "   - テスト用PRを作成"
    echo "   - mainブランチにマージ"
    echo "   - 自動デプロイを確認"
    echo ""
    log_warning "GitHub Actions経由でCodePipelineをトリガーする設定が推奨です"
}

# メイン実行
main() {
    echo "=== Sales Tools API CodePipeline デプロイ (Profile: $AWS_PROFILE) ==="
    echo ""
    
    check_parameters
    check_aws_auth
    deploy_stack
    show_outputs
    run_tests
    setup_webhook_guide
    
    echo ""
    log_success "🎉 CodePipelineのセットアップが完了しました！"
    echo ""
    echo "AWS Profile: $AWS_PROFILE"
    echo "Region: $REGION"
    echo "Stack: $STACK_NAME"
    echo ""
    echo "次回からは、mainブランチにプッシュするだけで自動デプロイされます。"
}

# スクリプト実行
main "$@"
