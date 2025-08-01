#!/bin/bash

# Sales Tools API CodePipeline デプロイスクリプト

set -e

# 設定
STACK_NAME="sales-tools-codepipeline"
TEMPLATE_FILE="infrastructure/cloudformation/codepipeline-stack.yml"
REGION="ap-northeast-1"

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
    log_info "AWS認証を確認しています..."
    
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        log_error "AWS認証が設定されていません"
        echo "aws configure を実行してください"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_success "AWS認証確認完了 (Account: $ACCOUNT_ID)"
}

# CloudFormationスタックのデプロイ
deploy_stack() {
    log_info "CloudFormationスタックをデプロイしています..."
    
    # スタックが存在するかチェック
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION > /dev/null 2>&1; then
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
        --region $REGION
    
    log_info "CloudFormationスタックの処理を待機しています..."
    
    # スタック処理完了を待機
    if [ "$OPERATION" = "create-stack" ]; then
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    else
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
    fi
    
    log_success "CloudFormationスタックのデプロイ完了"
}

# 出力情報の表示
show_outputs() {
    log_info "デプロイ結果を取得しています..."
    
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
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
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineUrl`].OutputValue' \
        --output text)
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    log_success "CodePipeline URL: $PIPELINE_URL"
    log_success "API Gateway URL: $API_URL"
}

# GitHub Webhookの設定案内
setup_webhook_guide() {
    log_info "GitHub Webhook設定案内"
    echo ""
    echo "=== 次のステップ ==="
    echo "1. GitHubリポジトリの Settings > Webhooks に移動"
    echo "2. 'Add webhook' をクリック"
    echo "3. Payload URL に以下を設定:"
    echo "   https://codepipeline.${REGION}.amazonaws.com/"
    echo "4. Content type: application/json"
    echo "5. Events: 'Just the push event' を選択"
    echo "6. Active にチェックを入れて保存"
    echo ""
    log_warning "または、GitHub Actions経由でCodePipelineをトリガーする設定が既に含まれています"
}

# メイン実行
main() {
    echo "=== Sales Tools API CodePipeline デプロイ ==="
    echo ""
    
    check_parameters
    check_aws_auth
    deploy_stack
    show_outputs
    setup_webhook_guide
    
    echo ""
    log_success "🎉 CodePipelineのセットアップが完了しました！"
    echo ""
    echo "次回からは、mainブランチにプッシュするだけで自動デプロイされます。"
}

# スクリプト実行
main "$@"
