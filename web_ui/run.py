#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keepa API Web UI 起動スクリプト
"""
import os
import sys
from dotenv import load_dotenv

def main():
    # 環境変数読み込み
    load_dotenv()
    
    # 環境チェック
    print("=== Keepa API Web UI 起動チェック ===")
    
    # APIキーチェック
    api_key = os.getenv('KEEPA_API_KEY')
    if api_key:
        print("✅ KEEPA_API_KEY: 設定済み")
    else:
        print("⚠️  KEEPA_API_KEY: 未設定")
        print("   .envファイルにKEEPA_API_KEY=your_api_keyを設定してください")
    
    # 依存関係チェック
    try:
        import flask
        print("✅ Flask: インストール済み")
    except ImportError:
        print("❌ Flask: 未インストール")
        print("   pip install flask でインストールしてください")
        return
    
    try:
        import keepa
        print("✅ Keepa: インストール済み")
    except ImportError:
        print("❌ Keepa: 未インストール")
        print("   pip install keepa でインストールしてください")
        return
    
    print("\n🚀 Web UIを起動します...")
    print("📱 ブラウザで http://localhost:5000 にアクセスしてください")
    print("🛑 終了するには Ctrl+C を押してください")
    print("-" * 50)
    
    # アプリケーション起動
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
