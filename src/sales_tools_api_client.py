# -*- coding: utf-8 -*-
"""
Sales Tools API Client
商品価格情報の取得・分析を行うAPIクライアント
"""
import keepa
import os
import time
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SalesToolsAPIClient:
    def __init__(self):
        """Sales Tools APIクライアント初期化"""
        self.api_key = os.getenv('SALES_TOOLS_API_KEY')
        if not self.api_key:
            raise ValueError("SALES_TOOLS_API_KEY環境変数が設定されていません")
        
        self.api = keepa.Keepa(self.api_key)
        logger.info("Sales Tools APIクライアント初期化完了")
    
    def get_product_info(self, asin: str, domain: str = 'JP') -> Optional[Dict]:
        """
        商品情報を取得
        
        Args:
            asin: 商品ASIN
            domain: Amazonドメイン
        
        Returns:
            商品情報辞書
        """
        try:
            logger.info(f"商品情報取得開始: {asin}")
            
            # API呼び出し
            products = self.api.query(asin, domain=domain, history=True)
            
            if not products or len(products) == 0:
                logger.warning(f"商品が見つかりません: {asin}")
                return None
            
            product = products[0]
            
            # 商品情報を整理
            product_info = {
                'asin': product.get('asin'),
                'title': product.get('title'),
                'domain': domain,
                'categories': product.get('categories', []),
                'manufacturer': product.get('manufacturer'),
                'brand': product.get('brand'),
                'model': product.get('model'),
                'package_dimensions': product.get('packageDimensions'),
                'features': product.get('features', [])
            }
            
            # 価格情報
            if 'csv' in product and len(product['csv']) > 0:
                amazon_prices = product['csv'][0]  # Amazon価格
                if len(amazon_prices) >= 2:
                    current_price = amazon_prices[-1]
                    if current_price != -1:
                        product_info['current_price'] = current_price / 100.0
                        product_info['currency'] = 'JPY' if domain == 'JP' else 'USD'
            
            # 価格統計
            if 'stats' in product:
                stats = product['stats']
                product_info['price_stats'] = {
                    'min': stats.get('min', 0) / 100.0 if stats.get('min') else None,
                    'max': stats.get('max', 0) / 100.0 if stats.get('max') else None,
                    'avg': stats.get('avg', 0) / 100.0 if stats.get('avg') else None,
                    'current': stats.get('current', 0) / 100.0 if stats.get('current') else None
                }
            
            # 最終更新時間
            if 'lastUpdate' in product:
                product_info['last_update'] = product['lastUpdate']
            
            logger.info(f"商品情報取得完了: {product_info.get('title', 'N/A')[:50]}")
            return product_info
            
        except Exception as e:
            logger.error(f"商品情報取得エラー: {str(e)}")
            return None
    
    def analyze_price_trend(self, asin: str, domain: str = 'JP') -> Optional[Dict]:
        """
        価格トレンドを分析
        
        Args:
            asin: 商品ASIN
            domain: Amazonドメイン
        
        Returns:
            価格分析結果
        """
        try:
            logger.info(f"価格トレンド分析開始: {asin}")
            
            # 商品情報取得
            product_info = self.get_product_info(asin, domain)
            if not product_info:
                return None
            
            # 価格履歴分析
            analysis = {
                'asin': asin,
                'title': product_info.get('title'),
                'current_price': product_info.get('current_price'),
                'currency': product_info.get('currency', 'JPY'),
                'price_stats': product_info.get('price_stats', {}),
                'analysis_timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 価格トレンド判定
            stats = product_info.get('price_stats', {})
            current = product_info.get('current_price', 0)
            
            if stats.get('min') and stats.get('max') and current:
                price_range = stats['max'] - stats['min']
                if price_range > 0:
                    price_position = (current - stats['min']) / price_range
                    
                    if price_position < 0.3:
                        analysis['trend'] = 'low_price'
                        analysis['recommendation'] = '買い時'
                        analysis['confidence'] = 'high'
                    elif price_position > 0.7:
                        analysis['trend'] = 'high_price'
                        analysis['recommendation'] = '高値圏'
                        analysis['confidence'] = 'high'
                    else:
                        analysis['trend'] = 'normal'
                        analysis['recommendation'] = '通常価格'
                        analysis['confidence'] = 'medium'
                    
                    analysis['price_position'] = round(price_position * 100, 1)
            
            logger.info(f"価格トレンド分析完了: {analysis.get('trend', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"価格トレンド分析エラー: {str(e)}")
            return None
    
    def search_deals(self, category: str = None, max_price: float = None, min_discount: float = 20.0) -> List[Dict]:
        """
        お得商品を検索
        
        Args:
            category: 商品カテゴリ
            max_price: 最大価格
            min_discount: 最小割引率(%)
        
        Returns:
            お得商品リスト
        """
        try:
            logger.info(f"お得商品検索開始: カテゴリ={category}, 最大価格={max_price}, 最小割引率={min_discount}%")
            
            # 注意: この機能は実際のAPIの制限により簡易実装
            # 実際の運用では、事前に取得した商品リストから分析
            
            deals = []
            
            # サンプル商品での検索デモ
            sample_asins = [
                'B08CDYX378',  # コカ・コーラ カナダドライ
                'B08N5WRWNW',  # SOLIMO 天然水
                'B07GXQZMM5'   # キッコーマン しょうゆ
            ]
            
            for asin in sample_asins:
                analysis = self.analyze_price_trend(asin)
                if analysis and analysis.get('trend') == 'low_price':
                    deals.append(analysis)
                
                # API制限を考慮した待機
                time.sleep(1)
            
            logger.info(f"お得商品検索完了: {len(deals)}件")
            return deals
            
        except Exception as e:
            logger.error(f"お得商品検索エラー: {str(e)}")
            return []
    
    def get_api_status(self) -> Dict:
        """API利用状況を取得"""
        try:
            status = {
                'api_key': self.api_key[:10] + '...' if self.api_key else 'Not Set',
                'tokens_left': getattr(self.api, 'tokens_left', 'Unknown'),
                'status': 'active',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"API状況: 残りトークン {status['tokens_left']}")
            return status
            
        except Exception as e:
            logger.error(f"API状況取得エラー: {str(e)}")
            return {'error': str(e)}

def main():
    """メイン実行（テスト用）"""
    try:
        client = SalesToolsAPIClient()
        
        # API状況確認
        print("=== Sales Tools API状況 ===")
        status = client.get_api_status()
        print(f"残りトークン: {status.get('tokens_left', 'Unknown')}")
        print()
        
        # 商品情報取得テスト
        test_asin = "B08CDYX378"
        print(f"=== 商品情報取得テスト: {test_asin} ===")
        product_info = client.get_product_info(test_asin)
        
        if product_info:
            print(f"商品名: {product_info.get('title', 'N/A')}")
            print(f"現在価格: {product_info.get('current_price', 'N/A')} {product_info.get('currency', '')}")
            print(f"ブランド: {product_info.get('brand', 'N/A')}")
        print()
        
        # 価格トレンド分析テスト
        print(f"=== 価格トレンド分析テスト: {test_asin} ===")
        analysis = client.analyze_price_trend(test_asin)
        
        if analysis:
            print(f"トレンド: {analysis.get('trend', 'N/A')}")
            print(f"推奨: {analysis.get('recommendation', 'N/A')}")
            print(f"価格位置: {analysis.get('price_position', 'N/A')}%")
        print()
        
        # お得商品検索テスト
        print("=== お得商品検索テスト ===")
        deals = client.search_deals()
        
        if deals:
            for deal in deals:
                print(f"- {deal.get('title', 'N/A')[:50]}: {deal.get('recommendation', 'N/A')}")
        else:
            print("お得商品が見つかりませんでした")
        
    except Exception as e:
        logger.error(f"テスト実行エラー: {str(e)}")

if __name__ == "__main__":
    main()
