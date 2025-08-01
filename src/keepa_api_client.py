# -*- coding: utf-8 -*-
import keepa
import time
import logging
import os
from typing import List, Dict, Optional

class KeepaAPIClient:
    def __init__(self):
        self.api_key = os.getenv('KEEPA_API_KEY')
        if not self.api_key:
            raise ValueError("KEEPA_API_KEY環境変数が設定されていません")
        
        self.api = keepa.Keepa(self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # ドメイン設定（Keepa API v2対応）
        self.AMAZON_DOMAIN = {
            'US': 'US',
            'UK': 'GB', 
            'DE': 'DE',
            'FR': 'FR',
            'JP': 'JP',  # 日本
            'CA': 'CA',
            'IT': 'IT',
            'ES': 'ES',
            'IN': 'IN',
            'MX': 'MX'
        }
        
    def get_product_info(self, asin: str, domain: str = 'JP') -> Optional[Dict]:
        """
        商品情報を取得
        
        Args:
            asin: Amazon商品のASIN
            domain: Amazonドメイン（デフォルト: 'JP'=日本）
        
        Returns:
            商品情報辞書またはNone
        """
        try:
            # Keepa APIでは数値ドメインコードを使用
            domain_code = self._get_domain_code(domain)
            products = self.api.query(asin, domain=domain_code)
            
            if products and len(products) > 0:
                return products[0]
            else:
                self.logger.warning(f"商品が見つかりません: {asin}")
                return None
                
        except Exception as e:
            self.logger.error(f"API呼び出しエラー: {str(e)}")
            return None
    
    def _get_domain_code(self, domain: str) -> int:
        """ドメイン文字列を数値コードに変換"""
        domain_mapping = {
            'US': 1,
            'GB': 2,
            'DE': 3,
            'FR': 4,
            'JP': 5,
            'CA': 6,
            'IT': 8,
            'ES': 9,
            'IN': 10,
            'MX': 11
        }
        return domain_mapping.get(domain, 5)  # デフォルトは日本
    
    def get_current_price(self, product: Dict) -> Optional[float]:
        """現在価格を取得"""
        try:
            if 'csv' in product and len(product['csv']) > 0:
                amazon_price_data = product['csv'][0]
                if len(amazon_price_data) >= 2:
                    latest_price = amazon_price_data[-1]
                    if latest_price != -1:
                        return latest_price / 100.0
            
            return None
            
        except Exception as e:
            self.logger.error(f"価格取得エラー: {str(e)}")
            return None
    
    def get_price_history(self, asin: str, domain: str = 'JP', days: int = 30) -> Optional[List]:
        """価格履歴を取得"""
        try:
            domain_code = self._get_domain_code(domain)
            products = self.api.query(asin, domain=domain_code, history=True, days=days)
            
            if products and len(products) > 0:
                return products[0].get('csv', [])
            
            return None
            
        except Exception as e:
            self.logger.error(f"価格履歴取得エラー: {str(e)}")
            return None
    
    def analyze_price_trend(self, asin: str, domain: str = 'JP') -> Dict:
        """価格トレンド分析"""
        try:
            product = self.get_product_info(asin, domain)
            if not product:
                return {"error": "商品情報取得失敗"}
            
            current_price = self.get_current_price(product)
            price_history = self.get_price_history(asin, domain, 30)
            
            result = {
                "asin": asin,
                "title": product.get('title', 'N/A'),
                "current_price": current_price,
                "currency": "JPY" if domain == 'JP' else "USD",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if price_history and len(price_history) > 0:
                # 簡単な価格分析
                prices = [p for p in price_history[0] if p != -1]
                if prices:
                    result["min_price"] = min(prices) / 100.0
                    result["max_price"] = max(prices) / 100.0
                    result["avg_price"] = sum(prices) / len(prices) / 100.0
            
            return result
            
        except Exception as e:
            self.logger.error(f"価格分析エラー: {str(e)}")
    def search_discounted_products(self, category: str = 'food', discount_threshold: float = 20.0, 
                                 domain: str = 'JP', limit: int = 10) -> List[Dict]:
        """
        値下がり商品を検索
        
        Args:
            category: 商品カテゴリ（food=食品）
            discount_threshold: 値下がり閾値（%）
            domain: Amazonドメイン
            limit: 取得件数
        
        Returns:
            値下がり商品のリスト
        """
        try:
            # Keepa APIでカテゴリ検索（食品カテゴリ）
            # 注意: 実際のKeepa APIの仕様に応じて調整が必要
            
            # 食品カテゴリのASINリストを取得（サンプル）
            food_asins = [
                'B08N5WRWNW',  # 食品サンプル1
                'B07GXQZMM5',  # 食品サンプル2
                'B0B5SDFLTB',  # テスト用ASIN
                'B08HLQV8K3',  # 食品サンプル3
                'B09JQVZM2P'   # 食品サンプル4
            ]
            
            discounted_products = []
            
            for asin in food_asins[:limit]:
                try:
                    product = self.get_product_info(asin, domain)
                    if not product:
                        continue
                    
                    # 価格履歴から値下がり率を計算
                    price_history = self.get_price_history(asin, domain, 30)
                    if not price_history or len(price_history) == 0:
                        continue
                    
                    current_price = self.get_current_price(product)
                    if not current_price:
                        continue
                    
                    # 過去30日の最高価格を取得
                    amazon_prices = price_history[0] if len(price_history) > 0 else []
                    valid_prices = [p for p in amazon_prices if p != -1]
                    
                    if len(valid_prices) < 2:
                        continue
                    
                    max_price = max(valid_prices) / 100.0
                    discount_rate = ((max_price - current_price) / max_price) * 100
                    
                    if discount_rate >= discount_threshold:
                        product_info = {
                            'asin': asin,
                            'title': product.get('title', 'N/A'),
                            'current_price': current_price,
                            'max_price': max_price,
                            'discount_rate': round(discount_rate, 2),
                            'currency': 'JPY' if domain == 'JP' else 'USD',
                            'category': 'food'
                        }
                        discounted_products.append(product_info)
                        
                except Exception as e:
                    self.logger.error(f"商品処理エラー {asin}: {str(e)}")
                    continue
            
            return discounted_products
            
        except Exception as e:
            self.logger.error(f"値下がり商品検索エラー: {str(e)}")
            return []
    
    def get_trending_deals(self, domain: str = 'JP') -> List[Dict]:
        """
        トレンド商品・お得情報を取得
        """
        try:
            # 人気の食品ASINリスト（実際の運用では動的に取得）
            trending_asins = [
                'B08N5WRWNW',  # 人気食品1
                'B07GXQZMM5',  # 人気食品2
                'B08HLQV8K3',  # 人気食品3
                'B09JQVZM2P',  # 人気食品4
                'B0B5SDFLTB'   # テスト用
            ]
            
            deals = []
            for asin in trending_asins:
                try:
                    product = self.get_product_info(asin, domain)
                    if product:
                        current_price = self.get_current_price(product)
                        if current_price:
                            deal_info = {
                                'asin': asin,
                                'title': product.get('title', 'N/A'),
                                'current_price': current_price,
                                'currency': 'JPY' if domain == 'JP' else 'USD'
                            }
                            deals.append(deal_info)
                except Exception as e:
                    continue
            
            return deals
            
        except Exception as e:
            self.logger.error(f"トレンド取得エラー: {str(e)}")
            return []
