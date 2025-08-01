# -*- coding: utf-8 -*-
import unittest
import json
import os
import sys
from unittest.mock import Mock, patch

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    
    @patch('lambda_function.KeepaAPIClient')
    def test_lambda_handler_analyze_success(self, mock_client_class):
        """Lambda関数の価格分析成功テスト"""
        # モッククライアント設定
        mock_client = Mock()
        mock_client.analyze_price_trend.return_value = {
            'asin': 'B0B5SDFLTB',
            'title': 'テスト商品',
            'current_price': 15.00,
            'currency': 'JPY'
        }
        mock_client_class.return_value = mock_client
        
        # テストイベント
        event = {
            'asin': 'B0B5SDFLTB',
            'domain': 5,
            'action': 'analyze'
        }
        
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 200)
        body = json.loads(result['body'])
        self.assertEqual(body['asin'], 'B0B5SDFLTB')
        self.assertEqual(body['current_price'], 15.00)
    
    @patch('lambda_function.KeepaAPIClient')
    def test_lambda_handler_info_success(self, mock_client_class):
        """Lambda関数の商品情報取得成功テスト"""
        mock_client = Mock()
        mock_client.get_product_info.return_value = {
            'asin': 'B0B5SDFLTB',
            'title': 'テスト商品'
        }
        mock_client.get_current_price.return_value = 15.00
        mock_client_class.return_value = mock_client
        
        event = {
            'asin': 'B0B5SDFLTB',
            'action': 'info'
        }
        
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 200)
        body = json.loads(result['body'])
        self.assertEqual(body['asin'], 'B0B5SDFLTB')
    
    def test_lambda_handler_missing_asin(self):
        """ASINパラメータ不足テスト"""
        event = {
            'action': 'analyze'
        }
        
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 400)
        body = json.loads(result['body'])
        self.assertIn('error', body)
    
    @patch('lambda_function.KeepaAPIClient')
    def test_lambda_handler_api_error(self, mock_client_class):
        """API呼び出しエラーテスト"""
        mock_client_class.side_effect = Exception("API接続エラー")
        
        event = {
            'asin': 'B0B5SDFLTB',
            'action': 'analyze'
        }
        
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 500)
        body = json.loads(result['body'])
        self.assertIn('error', body)
    
    @patch('lambda_function.KeepaAPIClient')
    def test_lambda_handler_with_body(self, mock_client_class):
        """API Gateway形式のbodyパラメータテスト"""
        mock_client = Mock()
        mock_client.analyze_price_trend.return_value = {'asin': 'B0B5SDFLTB'}
        mock_client_class.return_value = mock_client
        
        event = {
            'body': json.dumps({
                'asin': 'B0B5SDFLTB',
                'action': 'analyze'
            })
        }
        
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()
