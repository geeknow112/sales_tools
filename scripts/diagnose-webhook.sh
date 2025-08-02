#!/bin/bash

# GitHub Webhook診断スクリプト

set -e

AWS_PROFILE="lober-system"
REGION="ap-northeast-1"
PIPELINE_NAME="sales-tools-pipeline"

echo "=== GitHub Webhook診断 ==="
echo ""

# 1. Webhook設定確認
echo "1. Webhook設定確認"
WEBHOOK_INFO=$(aws codepipeline list-webhooks \
  --profile $AWS_PROFILE \
  --region $REGION \
  --query 'webhooks[?definition.targetPipeline==`'$PIPELINE_NAME'`]' \
  --output json)

if [ "$WEBHOOK_INFO" = "[]" ]; then
  echo "❌ Webhookが設定されていません"
  exit 1
else
  echo "✅ Webhook設定確認"
  WEBHOOK_URL=$(echo "$WEBHOOK_INFO" | grep -o 'https://[^"]*')
  echo "Webhook URL: $WEBHOOK_URL"
fi

# 2. パイプライン実行履歴確認
echo ""
echo "2. パイプライン実行履歴"
aws codepipeline list-pipeline-executions \
  --pipeline-name $PIPELINE_NAME \
  --profile $AWS_PROFILE \
  --region $REGION \
  --max-items 5 \
  --query 'pipelineExecutionSummaries[*].[pipelineExecutionId,status,trigger.triggerType,startTime]' \
  --output table

# 3. 最新のGitコミット確認
echo ""
echo "3. 最新のGitコミット"
cd /mnt/c/Users/youre/Documents/git_repo/dev_tmp/keepa_work
git log --oneline -5

# 4. GitHub API経由でWebhook確認（参考）
echo ""
echo "4. 推奨対応"
echo "GitHub側でWebhookが正しく設定されているか確認してください："
echo "1. https://github.com/geeknow112/sales_tools/settings/hooks にアクセス"
echo "2. AWS CodePipelineのWebhookが登録されているか確認"
echo "3. Recent Deliveriesでイベント送信状況を確認"

# 5. 手動テスト用コマンド
echo ""
echo "5. 手動テスト用コマンド"
echo "aws codepipeline start-pipeline-execution --name $PIPELINE_NAME --profile $AWS_PROFILE --region $REGION"

echo ""
echo "=== 診断完了 ==="
