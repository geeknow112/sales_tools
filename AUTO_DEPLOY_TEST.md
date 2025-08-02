# ECS Auto Deploy Test

このファイルは自動デプロイパイプラインのテスト用です。

## テスト実行時刻
- 作成日時: 2025-08-02 12:45:00 JST
- テスト目的: GitHub → CodePipeline → ECS 自動デプロイ確認

## 期待される動作
1. このファイルをmainブランチにプッシュ
2. GitHub Webhookが CodePipeline をトリガー
3. CodeBuild が Docker イメージをビルド・ECR プッシュ
4. 既存 ECS タスクを停止
5. 新しい ECS タスクを自動起動

## 確認方法
- AWS Console → CodePipeline → ecs-auto-deploy-pipeline
- AWS Console → ECS → Clusters → sales-tools-cluster → Tasks

テスト実行中...
