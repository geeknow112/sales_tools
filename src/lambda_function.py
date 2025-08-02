# -*- coding: utf-8 -*-
"""
AWS Lambda Function for Sales Tools API Integration
商品価格分析のためのLambda関数
"""
import json
import logging
import sys
import os
import time

# Sales Tools APIクライアントをインポート
from sales_tools_api_client import SalesToolsAPIClient

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Lambda関数のメインハンドラー
    
    Args:
        event: Lambda実行イベント
        context: Lambda実行コンテキスト
    
    Returns:
        レスポンス辞書
    """
    try:
        logger.info(f"Lambda実行開始: {json.dumps(event, ensure_ascii=False)}")
        
        # リクエストパラメータ取得
        asin = event.get('asin')
        domain = event.get('domain', 'JP')
        action = event.get('action', 'info')
        
        if not asin:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'ASINパラメータが必要です',
                    'message': 'ASIN parameter is required'
                }, ensure_ascii=False)
            }
        
        # Sales Tools APIクライアント初期化
        try:
            client = SalesToolsAPIClient()
        except ValueError as e:
            logger.error(f"APIクライアント初期化エラー: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'API設定エラー',
                    'message': 'Sales Tools API key not configured'
                }, ensure_ascii=False)
            }
        
        # アクションに応じた処理
        if action == 'info':
            # 商品情報取得
            result = client.get_product_info(asin, domain)
            
        elif action == 'analyze':
            # 価格トレンド分析
            result = client.analyze_price_trend(asin, domain)
            
        elif action == 'deals':
            # お得商品検索
            max_price = event.get('max_price')
            min_discount = event.get('min_discount', 20.0)
            result = client.search_deals(max_price=max_price, min_discount=min_discount)
            
        elif action == 'status':
            # API状況確認
            result = client.get_api_status()
            
            # PR テスト用の追加情報
            result['pr_test'] = {
                'version': '1.1.0',
                'feature': 'CodePipeline PR Test',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'deployment_method': 'GitHub PR → CodePipeline → Lambda'
            }
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '無効なアクション',
                    'message': f'Invalid action: {action}',
                    'available_actions': ['info', 'analyze', 'deals', 'status']
                }, ensure_ascii=False)
            }
        
        # 結果確認
        if result is None:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'データが見つかりません',
                    'message': f'No data found for ASIN: {asin}'
                }, ensure_ascii=False)
            }
        
        # 成功レスポンス
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'action': action,
                'asin': asin,
                'domain': domain,
                'data': result,
                'timestamp': client.get_api_status().get('timestamp')
            }, ensure_ascii=False)
        }
        
        logger.info(f"Lambda実行完了: {action} - {asin}")
        return response
        
    except Exception as e:
        logger.error(f"Lambda実行エラー: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': '内部サーバーエラー',
                'message': str(e)
            }, ensure_ascii=False)
        }

def test_lambda_locally():
    """ローカルテスト用関数"""
    # テストイベント
    test_events = [
        {
            'asin': 'B08CDYX378',
            'domain': 'JP',
            'action': 'info'
        },
        {
            'asin': 'B08CDYX378',
            'domain': 'JP',
            'action': 'analyze'
        },
        {
            'action': 'status'
        }
    ]
    
    print("=== Lambda関数ローカルテスト ===")
    
    for i, event in enumerate(test_events, 1):
        print(f"\n--- テスト {i}: {event.get('action', 'unknown')} ---")
        
        try:
            response = lambda_handler(event, None)
            print(f"ステータス: {response['statusCode']}")
            
            body = json.loads(response['body'])
            if response['statusCode'] == 200:
                print(f"成功: {body.get('action', 'N/A')}")
                if 'data' in body:
                    data = body['data']
                    if isinstance(data, dict):
                        print(f"データ: {data.get('title', data.get('asin', 'N/A'))}")
                    elif isinstance(data, list):
                        print(f"データ件数: {len(data)}")
            else:
                print(f"エラー: {body.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"テストエラー: {str(e)}")

if __name__ == "__main__":
    test_lambda_locally()
