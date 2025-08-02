#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keepaトラッキング商品管理
複数商品のトラッキング状況を管理・監視
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackingManager:
    """トラッキング商品管理クラス"""
    
    def __init__(self):
        self.tracked_products = {
            "B08CDYX378": {
                "name": "コカ・コーラ カナダドライ",
                "category": "食品・飲料",
                "status": "active",
                "threshold": 95,
                "added_date": "2025-08-01",
                "last_check": None
            },
            "B0B5SDFLTB": {
                "name": "Sample Product",
                "category": "Electronics", 
                "status": "pending",
                "threshold": 95,
                "added_date": "2025-08-02",
                "last_check": None
            },
            "B08N5WRWNW": {
                "name": "Echo Dot (第4世代)",
                "category": "家電・AV機器",
                "status": "pending", 
                "threshold": 95,
                "added_date": "2025-08-02",
                "last_check": None
            }
        }
    
    def get_all_tracked_products(self) -> Dict:
        """全トラッキング商品の取得"""
        return self.tracked_products
    
    def get_product_status(self, asin: str) -> Optional[Dict]:
        """特定商品のトラッキング状況取得"""
        return self.tracked_products.get(asin)
    
    def update_product_status(self, asin: str, status: str, last_check: str = None):
        """商品のトラッキング状況更新"""
        if asin in self.tracked_products:
            self.tracked_products[asin]["status"] = status
            if last_check:
                self.tracked_products[asin]["last_check"] = last_check
            logger.info(f"Updated {asin} status to {status}")
    
    def add_product(self, asin: str, name: str, category: str, threshold: int = 95):
        """新しい商品をトラッキングリストに追加"""
        self.tracked_products[asin] = {
            "name": name,
            "category": category,
            "status": "pending",
            "threshold": threshold,
            "added_date": datetime.now().strftime("%Y-%m-%d"),
            "last_check": None
        }
        logger.info(f"Added new product to tracking: {asin} - {name}")
    
    def get_tracking_summary(self) -> Dict:
        """トラッキング状況のサマリー"""
        total = len(self.tracked_products)
        active = sum(1 for p in self.tracked_products.values() if p["status"] == "active")
        pending = sum(1 for p in self.tracked_products.values() if p["status"] == "pending")
        
        return {
            "total_products": total,
            "active_tracking": active,
            "pending_setup": pending,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def simulate_price_data(self, asin: str) -> Dict:
        """価格データのシミュレーション（テスト用）"""
        import random
        
        base_prices = {
            "B08CDYX378": 150,  # コカ・コーラ
            "B0B5SDFLTB": 1980,  # Sample Product
            "B08N5WRWNW": 5980   # Echo Dot
        }
        
        base_price = base_prices.get(asin, 1000)
        current_price = base_price + random.randint(-200, 200)
        
        return {
            "asin": asin,
            "current_price": current_price,
            "base_price": base_price,
            "price_change": current_price - base_price,
            "price_change_percent": round(((current_price - base_price) / base_price) * 100, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tracking_status": self.get_product_status(asin)
        }

# グローバルインスタンス
tracking_manager = TrackingManager()
