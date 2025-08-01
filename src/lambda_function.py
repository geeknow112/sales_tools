# -*- coding: utf-8 -*-
import json
import logging
import sys
import os

# シンプル版検索機能をインポート
from simple_discount_search import search_discounted_products_simple

try:
    from keepa_api_client import KeepaAPIClient
    KEEPA_AVAILABLE = True
except ImportError as e:
    print(f"Keepa import error: {e}")
    KEEPA_AVAILABLE = False

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda関数のメインハンドラー
    
    Args:
        event: Lambda実行イベント
        context: Lambda実行コンテキスト
    
    Returns:
        API Gateway形式のレスポンス
    """
    try:
        # リクエストパラメータの取得
        if 'body' in event and event['body']:
            body = json.loads(event['body'])
        else:
            body = event
        
        asin = body.get('asin', '')
        domain = body.get('domain', 'JP')  # デフォルト: 日本
        action = body.get('action', 'analyze')  # デフォルト: 価格分析
        
        # ASINが必要なアクションの場合のみチェック
        if action in ['analyze', 'info'] and not asin:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'ASINパラメータが必要です'
                }, ensure_ascii=False)
            }
        
        # Keepa APIクライアント初期化
        if KEEPA_AVAILABLE and action in ['analyze', 'info']:
            try:
                client = KeepaAPIClient()
            except Exception as e:
                logger.error(f"Keepa API初期化エラー: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Keepa API初期化失敗: {str(e)}'
                    }, ensure_ascii=False)
                }
        else:
            client = None
        
        # アクションに応じた処理
        if action == 'analyze':
            if client:
                result = client.analyze_price_trend(asin, domain)
            else:
                result = {'error': 'Keepa APIが利用できません'}
        elif action == 'info':
            if client:
                product = client.get_product_info(asin, domain)
                if product:
                    result = {
                        'asin': asin,
                        'title': product.get('title', 'N/A'),
                        'current_price': client.get_current_price(product)
                    }
                else:
                    result = {'error': '商品情報が取得できませんでした'}
            else:
                result = {'error': 'Keepa APIが利用できません'}
        elif action == 'search_discounts':
            # 値下がり商品検索（シンプル版）
            discount_threshold = body.get('discount_threshold', 20.0)
            category = body.get('category', 'food')
            limit = body.get('limit', 10)
            
            result = search_discounted_products_simple(
                discount_threshold=discount_threshold,
                category=category,
                limit=limit
            )
        elif action == 'trending':
            # トレンド商品取得（シンプル版）
            result = search_discounted_products_simple(
                discount_threshold=10.0,  # トレンドは低い閾値
                category='food',
                limit=10
            )
            result['action'] = 'trending'
        else:
            result = {'error': f'未対応のアクション: {action}'}
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        logger.error(f"Lambda実行エラー: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'サーバーエラーが発生しました',
                'details': str(e)
            }, ensure_ascii=False)
        }

# ローカルテスト用
if __name__ == "__main__":
    # テストイベント
    test_event = {
        'asin': 'B0B5SDFLTB',
        'domain': 5,
        'action': 'analyze'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
