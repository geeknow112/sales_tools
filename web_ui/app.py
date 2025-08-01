# -*- coding: utf-8 -*-
import os
import sys
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from keepa_api_client import KeepaAPIClient
    from lambda_function import lambda_handler
except ImportError as e:
    print(f"Import error: {e}")
    KeepaAPIClient = None
    lambda_handler = None

app = Flask(__name__)

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/product', methods=['POST'])
def get_product_info():
    """商品情報取得API"""
    try:
        data = request.get_json()
        asin = data.get('asin', '').strip()
        domain = int(data.get('domain', 5))
        action = data.get('action', 'analyze')
        
        if not asin:
            return jsonify({'error': 'ASINが入力されていません'}), 400
        
        # Lambda関数を直接呼び出し
        event = {
            'asin': asin,
            'domain': domain,
            'action': action
        }
        
        if lambda_handler:
            result = lambda_handler(event, None)
            if result['statusCode'] == 200:
                return jsonify(json.loads(result['body']))
            else:
                return jsonify(json.loads(result['body'])), result['statusCode']
        else:
            return jsonify({'error': 'Keepa APIクライアントが利用できません'}), 500
            
    except Exception as e:
        return jsonify({'error': f'サーバーエラー: {str(e)}'}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """API接続テスト"""
    try:
        if KeepaAPIClient:
            # 環境変数チェック
            api_key = os.getenv('KEEPA_API_KEY')
            if api_key:
                return jsonify({
                    'status': 'OK',
                    'message': 'Keepa API接続準備完了',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'WARNING',
                    'message': 'KEEPA_API_KEY環境変数が設定されていません',
                    'timestamp': datetime.now().isoformat()
                }), 400
        else:
            return jsonify({
                'status': 'ERROR',
                'message': 'Keepa APIクライアントが利用できません',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f'テストエラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # 環境変数読み込み
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=== Keepa API Web UI ===")
    print(f"KEEPA_API_KEY設定: {'✓' if os.getenv('KEEPA_API_KEY') else '✗'}")
    print("http://localhost:5000 でアクセス可能")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
