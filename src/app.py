#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sales Tools API - ECS Fargate Application v1.2.0
Amazon商品価格分析のためのECSアプリケーション（トラッキング機能強化版）
"""

import json
import logging
import os
import time
from flask import Flask, request, jsonify
from tracking_manager import tracking_manager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 環境変数の取得
SALES_TOOLS_API_KEY = os.environ.get('SALES_TOOLS_API_KEY', 'test_api_key_placeholder')

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'service': 'sales-tools-api'
    })

@app.route('/status', methods=['GET'])
def get_status():
    """ステータス情報の取得"""
    return jsonify({
        'message': 'Sales Tools API - ECS Fargate Version',
        'version': '1.2.0',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'deployment_method': 'ECS Fargate',
        'status': 'active',
        'environment': {
            'platform': 'ECS Fargate',
            'runtime': 'python3.9',
            'has_api_key': bool(SALES_TOOLS_API_KEY and SALES_TOOLS_API_KEY != 'test_api_key_placeholder')
        }
    })

@app.route('/tracking', methods=['GET'])
def get_tracking_status():
    """トラッキング状況の取得"""
    try:
        summary = tracking_manager.get_tracking_summary()
        products = tracking_manager.get_all_tracked_products()
        
        return jsonify({
            'summary': summary,
            'products': products,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_tracking_status: {str(e)}")
        return jsonify({
            'error': 'Failed to get tracking status',
            'message': str(e),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/tracking/<asin>', methods=['GET'])
def get_product_tracking(asin):
    """特定商品のトラッキング状況取得"""
    try:
        product_status = tracking_manager.get_product_status(asin)
        if not product_status:
            return jsonify({
                'error': 'Product not found',
                'asin': asin,
                'message': 'This product is not in the tracking list',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }), 404
        
        # 価格データのシミュレーション
        price_data = tracking_manager.simulate_price_data(asin)
        
        return jsonify({
            'asin': asin,
            'tracking_info': product_status,
            'price_data': price_data,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_product_tracking: {str(e)}")
        return jsonify({
            'error': 'Failed to get product tracking',
            'message': str(e),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_product():
    """商品価格分析エンドポイント"""
    try:
        data = request.get_json()
        if not data or 'asin' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'ASIN is required',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }), 400
        
        asin = data['asin']
        domain = data.get('domain', 'JP')
        
        logger.info(f"Analysis request: ASIN={asin}, Domain={domain}")
        
        # トラッキング状況確認
        tracking_status = tracking_manager.get_product_status(asin)
        
        # 分析結果（シミュレーション）
        response_data = {
            'asin': asin,
            'domain': domain,
            'analysis': {
                'current_price': 1980,
                'avg_price_30d': 2100,
                'price_trend': 'decreasing',
                'recommendation': 'good_time_to_buy'
            },
            'tracking_status': tracking_status,
            'metadata': {
                'api_version': '1.2.0',
                'processing_time_ms': 150,
                'data_source': 'sales_tools_api'
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_product: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/product/<asin>', methods=['GET'])
def get_product_info(asin):
    """商品情報取得エンドポイント"""
    try:
        domain = request.args.get('domain', 'JP')
        
        logger.info(f"Product info request: ASIN={asin}, Domain={domain}")
        
        # トラッキング状況確認
        tracking_status = tracking_manager.get_product_status(asin)
        
        # 商品情報（シミュレーション）
        response_data = {
            'asin': asin,
            'domain': domain,
            'product_info': {
                'title': 'Sample Product Title',
                'brand': 'Sample Brand',
                'category': 'Electronics',
                'current_price': 1980,
                'currency': 'JPY',
                'availability': 'In Stock',
                'rating': 4.2,
                'review_count': 1250
            },
            'price_history': {
                'period_days': 30,
                'data_points': 30,
                'min_price': 1850,
                'max_price': 2300,
                'avg_price': 2100
            },
            'tracking_status': tracking_status,
            'metadata': {
                'retrieved_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'api_version': '1.2.0'
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in get_product_info: {str(e)}")
        return jsonify({
            'error': 'Failed to get product info',
            'message': str(e),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            'GET /health',
            'GET /status', 
            'GET /tracking',
            'GET /tracking/<asin>',
            'POST /analyze',
            'GET /product/<asin>'
        ],
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }), 404

if __name__ == '__main__':
    logger.info("Starting Sales Tools API - ECS Fargate Version 1.2.0")
    app.run(host='0.0.0.0', port=8080, debug=False)
