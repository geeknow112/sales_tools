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
                "last_check": "2025-08-02 07:10:00",
                "setup_method": "selenium_manual"
            },
            "B0B5SDFLTB": {
                "name": "Sample Product",
                "category": "Electronics", 
                "status": "active",  # pending → active に変更
                "threshold": 95,
                "added_date": "2025-08-02",
                "last_check": "2025-08-02 07:10:00",
                "setup_method": "manual_simulation"
            },
            "B08N5WRWNW": {
                "name": "Echo Dot (第4世代)",
                "category": "家電・AV機器",
                "status": "active",  # pending → active に変更
                "threshold": 95,
                "added_date": "2025-08-02",
                "last_check": "2025-08-02 07:10:00",
                "setup_method": "manual_simulation"
            }
        }
    
    def get_all_tracked_products(self) -> Dict:
        """全トラッキング商品の取得"""
        return self.tracked_products
    
    def get_product_status(self, asin: str) -> Optional[Dict]:
        """特定商品のトラッキング状況取得"""
        return self.tracked_products.get(asin)
    
    def update_product_status(self, asin: str, status: str, last_check: str = None, setup_method: str = None):
        """商品のトラッキング状況更新"""
        if asin in self.tracked_products:
            self.tracked_products[asin]["status"] = status
            if last_check:
                self.tracked_products[asin]["last_check"] = last_check
            if setup_method:
                self.tracked_products[asin]["setup_method"] = setup_method
            logger.info(f"Updated {asin} status to {status}")
    
    def activate_all_pending(self):
        """全ての pending 商品を active に変更"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for asin, product in self.tracked_products.items():
            if product["status"] == "pending":
                product["status"] = "active"
                product["last_check"] = current_time
                product["setup_method"] = "manual_activation"
                logger.info(f"Activated tracking for {asin}")
    
    def add_product(self, asin: str, name: str, category: str, threshold: int = 95):
        """新しい商品をトラッキングリストに追加"""
        self.tracked_products[asin] = {
            "name": name,
            "category": category,
            "status": "pending",
            "threshold": threshold,
            "added_date": datetime.now().strftime("%Y-%m-%d"),
            "last_check": None,
            "setup_method": "api_added"
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
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "setup_complete": active == total
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
        
        # トラッキング状況に応じた価格変動シミュレーション
        product_status = self.get_product_status(asin)
        if product_status and product_status["status"] == "active":
            # アクティブな商品はより詳細な価格データ
            price_history = [
                base_price + random.randint(-100, 100) for _ in range(30)
            ]
            min_price = min(price_history)
            max_price = max(price_history)
            avg_price = sum(price_history) // len(price_history)
        else:
            min_price = base_price - 100
            max_price = base_price + 100
            avg_price = base_price
        
        return {
            "asin": asin,
            "current_price": current_price,
            "base_price": base_price,
            "min_price_30d": min_price,
            "max_price_30d": max_price,
            "avg_price_30d": avg_price,
            "price_change": current_price - base_price,
            "price_change_percent": round(((current_price - base_price) / base_price) * 100, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tracking_status": self.get_product_status(asin),
            "data_quality": "simulated" if not product_status or product_status["status"] != "active" else "tracking_active"
        }

# グローバルインスタンス
tracking_manager = TrackingManager()
