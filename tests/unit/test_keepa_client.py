# -*- coding: utf-8 -*-
import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from keepa_api_client import KeepaAPIClient

class TestKeepaAPIClient(unittest.TestCase):
    
    @patch.dict(os.environ, {'KEEPA_API_KEY': 'test_api_key'})
    @patch('keepa_api_client.keepa.Keepa')
    def setUp(self, mock_keepa):
        self.mock_api = Mock()
        mock_keepa.return_value = self.mock_api
        self.client = KeepaAPIClient()
    
    def test_init_without_api_key(self):
        """APIキーなしでの初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                KeepaAPIClient()
    
    def test_get_product_info_success(self):
        """商品情報取得成功テスト"""
        # モックデータ
        mock_product = {
            'asin': 'B0B5SDFLTB',
            'title': 'テスト商品',
            'csv': [[1000, 2000, 1500]]
        }
        self.mock_api.query.return_value = [mock_product]
        
        result = self.client.get_product_info('B0B5SDFLTB')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['asin'], 'B0B5SDFLTB')
        self.mock_api.query.assert_called_once_with('B0B5SDFLTB', domain=5)
    
    def test_get_product_info_not_found(self):
        """商品情報取得失敗テスト"""
        self.mock_api.query.return_value = []
        
        result = self.client.get_product_info('INVALID_ASIN')
        
        self.assertIsNone(result)
    
    def test_get_current_price_success(self):
        """現在価格取得成功テスト"""
        mock_product = {
            'csv': [[1000, 2000, 1500]]  # 最新価格は1500 (15.00円)
        }
        
        result = self.client.get_current_price(mock_product)
        
        self.assertEqual(result, 15.00)
    
    def test_get_current_price_invalid_data(self):
        """無効な価格データテスト"""
        mock_product = {
            'csv': [[-1, -1, -1]]  # 無効な価格データ
        }
        
        result = self.client.get_current_price(mock_product)
        
        self.assertIsNone(result)
    
    def test_analyze_price_trend_success(self):
        """価格トレンド分析成功テスト"""
        mock_product = {
            'asin': 'B0B5SDFLTB',
            'title': 'テスト商品',
            'csv': [[1000, 2000, 1500, 1200]]
        }
        self.mock_api.query.return_value = [mock_product]
        
        result = self.client.analyze_price_trend('B0B5SDFLTB')
        
        self.assertIn('asin', result)
        self.assertIn('title', result)
        self.assertIn('current_price', result)
        self.assertEqual(result['asin'], 'B0B5SDFLTB')

if __name__ == '__main__':
    unittest.main()
