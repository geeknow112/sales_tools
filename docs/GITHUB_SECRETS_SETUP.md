# GitHub Secrets 設定ガイド

Sales Tools API の CI/CD パイプラインを動作させるために、以下のSecretsをGitHubリポジトリに設定する必要があります。

## 🔑 必要なSecrets

### 1. AWS認証情報

#### `AWS_ACCESS_KEY_ID`
- **説明**: AWSアクセスキーID
- **取得方法**: AWS IAM > ユーザー > セキュリティ認証情報
- **権限**: CodePipeline実行権限

#### `AWS_SECRET_ACCESS_KEY`
- **説明**: AWSシークレットアクセスキー
- **取得方法**: AWS IAM > ユーザー > セキュリティ認証情報
- **注意**: 絶対に外部に漏らさないこと

### 2. Sales Tools API

#### `SALES_TOOLS_API_KEY_TEST`
- **説明**: テスト用Sales Tools APIキー
- **用途**: GitHub Actionsでのテスト実行
- **注意**: 本番用とは別のキーを推奨

## 📝 設定手順

### Step 1: GitHubリポジトリにアクセス
1. https://github.com/geeknow112/sales_tools にアクセス
2. `Settings` タブをクリック

### Step 2: Secretsページに移動
1. 左サイドバーの `Secrets and variables` をクリック
2. `Actions` を選択

### Step 3: Secretsを追加
1. `New repository secret` ボタンをクリック
2. 以下の情報を入力：
   - **Name**: シークレット名（上記リスト参照）
   - **Secret**: 対応する値
3. `Add secret` をクリック

### Step 4: 設定確認
以下のSecretsが設定されていることを確認：
- ✅ `AWS_ACCESS_KEY_ID`
- ✅ `AWS_SECRET_ACCESS_KEY`
- ✅ `SALES_TOOLS_API_KEY_TEST`

## 🔒 セキュリティのベストプラクティス

### AWS IAM権限の最小化
CodePipeline用のIAMユーザーには、必要最小限の権限のみを付与：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codepipeline:StartPipelineExecution",
                "codepipeline:GetPipelineExecution",
                "codepipeline:ListPipelineExecutions"
            ],
            "Resource": "arn:aws:codepipeline:ap-northeast-1:*:sales-tools-pipeline"
        }
    ]
}
```

### APIキーの管理
- テスト用と本番用のAPIキーを分離
- 定期的なキーローテーション
- 使用量の監視

## 🧪 テスト方法

### Secretsが正しく設定されているかテスト

1. **GitHub Actionsでテスト**
   ```bash
   # テスト用PRを作成
   git checkout -b test/secrets-check
   git push origin test/secrets-check
   
   # PRを作成してActionsが実行されることを確認
   ```

2. **ローカルでテスト**
   ```bash
   # 環境変数を設定
   export SALES_TOOLS_API_KEY_TEST=your_test_api_key
   
   # テスト実行
   cd src
   python -c "
   import os
   from lambda_function import lambda_handler
   
   if os.getenv('SALES_TOOLS_API_KEY_TEST'):
       print('✅ API Key is set')
       event = {'action': 'status'}
       result = lambda_handler(event, None)
       print('Lambda test result:', result['statusCode'])
   else:
       print('❌ API Key not set')
   "
   ```

## 🚨 トラブルシューティング

### よくある問題

#### 1. AWS認証エラー
```
Error: The security token included in the request is invalid
```
**解決方法**: AWS_ACCESS_KEY_IDとAWS_SECRET_ACCESS_KEYを再確認

#### 2. API Key エラー
```
Error: SALES_TOOLS_API_KEY_TEST not configured
```
**解決方法**: GitHub SecretsにSALES_TOOLS_API_KEY_TESTを追加

#### 3. 権限エラー
```
Error: User is not authorized to perform: codepipeline:StartPipelineExecution
```
**解決方法**: IAMユーザーにCodePipeline権限を追加

## 📞 サポート

設定で問題が発生した場合：
1. GitHub Actionsのログを確認
2. AWS CloudWatch Logsを確認
3. IAM権限を確認

## 🔄 更新履歴

- 2025-08-02: 初版作成
- 権限設定の詳細化
- トラブルシューティング追加
