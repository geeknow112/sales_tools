#!/bin/bash

# Sales Tools API CodePipeline 軽量版デプロイスクリプト

set -e

# 設定
STACK_NAME="sales-tools-codepipeline-minimal"
TEMPLATE_FILE="infrastructure/cloudformation/codepipeline-minimal-stack.yml"
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
cleanup_failed_stack() {
    log_info "失敗したスタックをクリーンアップしています..."
    
    if aws cloudformation describe-stacks --stack-name sales-tools-codepipeline --profile $AWS_PROFILE --region $REGION > /dev/null 2>&1; then
        STACK_STATUS=$(aws cloudformation describe-stacks --stack-name sales-tools-codepipeline --profile $AWS_PROFILE --region $REGION --query 'Stacks[0].StackStatus' --output text)
        
        if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ] || [ "$STACK_STATUS" = "CREATE_FAILED" ]; then
            log_info "失敗したスタックを削除します: sales-tools-codepipeline"
            aws cloudformation delete-stack --stack-name sales-tools-codepipeline --profile $AWS_PROFILE --region $REGION
            aws cloudformation wait stack-delete-complete --stack-name sales-tools-codepipeline --profile $AWS_PROFILE --region $REGION
            log_success "失敗したスタックの削除完了"
        fi
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
    log_info "軽量版CloudFormationスタックをデプロイしています..."
    
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
    echo "=== 軽量版デプロイ完了 ==="
    echo "$OUTPUTS"
    echo ""
    
    # 重要な情報を抽出
    PIPELINE_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineUrl`].OutputValue' \
        --output text)
    
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --profile $AWS_PROFILE \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    log_success "CodePipeline URL: $PIPELINE_URL"
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
        
        aws lambda invoke \
            --function-name $LAMBDA_NAME \
            --payload '{"action": "status", "test": true}' \
            --region $REGION \
            --profile $AWS_PROFILE \
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
    
    # CodePipelineの初回実行
    PIPELINE_NAME="sales-tools-pipeline"
    log_info "CodePipelineの初回実行をトリガーします..."
    
    aws codepipeline start-pipeline-execution \
        --name $PIPELINE_NAME \
        --region $REGION \
        --profile $AWS_PROFILE > /dev/null 2>&1
    
    log_success "CodePipeline初回実行をトリガーしました"
}

# メイン実行
main() {
    echo "=== Sales Tools API CodePipeline 軽量版デプロイ ==="
    echo "Profile: $AWS_PROFILE"
    echo "Region: $REGION"
    echo ""
    
    cleanup_failed_stack
    check_parameters
    check_aws_auth
    deploy_stack
    show_outputs
    run_tests
    
    echo ""
    log_success "🎉 軽量版CodePipelineのセットアップが完了しました！"
    echo ""
    echo "作成されたリソース:"
    echo "- CodePipeline: sales-tools-pipeline"
    echo "- Lambda Function: sales-tools-api-function"
    echo "- S3 Bucket: アーティファクト保存用"
    echo ""
    echo "次回からは、mainブランチにプッシュするだけで自動デプロイされます。"
}

# スクリプト実行
main "$@"
