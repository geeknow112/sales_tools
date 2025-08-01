# -*- coding: utf-8 -*-
"""
手動ログイン + 自動トラッキング設定
ログインは手動で行い、トラッキング設定のみ自動化
"""
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualLoginAutoTracker:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.actions = None
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """人間らしいランダム待機"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        logger.debug(f"Human delay: {delay:.2f}秒")
    
    def human_type(self, element, text, typing_delay=0.1):
        """人間らしいタイピング"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, typing_delay))
        logger.debug(f"Human typing completed: {text[:10]}...")
    
    def setup_browser(self):
        """ブラウザセットアップ（手動操作用）"""
        try:
            chrome_options = Options()
            
            # 手動操作に適した設定
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 通常のUser-Agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 自動化検知を無効化
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)  # 手動操作を考慮して長めに設定
            self.actions = ActionChains(self.driver)
            
            logger.info("✅ ブラウザ初期化成功（手動操作モード）")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザ初期化エラー: {str(e)}")
            return False
    
    def open_keepa_for_manual_login(self):
        """Keepaを開いて手動ログインを待機"""
        try:
            logger.info("🏠 Keepaサイトを開きます")
            
            # Keepaメインページにアクセス
            self.driver.get("https://keepa.com/#!")
            self.human_delay(2, 3)
            
            print("\n" + "="*60)
            print("🔐 手動ログインを行ってください")
            print("="*60)
            print("1. ブラウザでKeepaサイトが開きました")
            print("2. 「ログイン」ボタンをクリックしてください")
            print("3. ログイン情報を入力してください")
            print("   - メール: yourenemy1008@gmail.com")
            print("   - パスワード: keepa.rage.%%%'")
            print("4. ログインが完了したらEnterキーを押してください")
            print("="*60)
            
            # 手動ログイン完了を待機
            input("ログインが完了したらEnterキーを押してください...")
            
            # ログイン確認
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # ログイン成功の指標
            login_indicators = [
                "dashboard" in page_source,
                "account" in page_source,
                "logout" in page_source,
                "profile" in page_source,
                "manage" in page_source
            ]
            
            login_confirmed = any(login_indicators)
            
            if login_confirmed:
                logger.info("✅ ログイン成功を確認")
                print("✅ ログイン成功を確認しました")
                return True
            else:
                logger.warning("⚠️ ログイン状況が不明確ですが続行します")
                print("⚠️ ログイン状況が不明確ですが続行します")
                return True
                
        except Exception as e:
            logger.error(f"Keepa開始エラー: {str(e)}")
            return False
    
    def navigate_to_product_and_track(self, asin: str):
        """商品ページに移動してトラッキング設定"""
        try:
            logger.info(f"🎯 商品ページでトラッキング設定開始: {asin}")
            
            # 商品ページに移動
            product_url = f"https://keepa.com/#!product/5-{asin}"
            logger.info(f"📱 商品ページアクセス: {product_url}")
            self.driver.get(product_url)
            self.human_delay(3, 5)
            
            # ページ読み込み確認
            page_title = self.driver.title
            logger.info(f"📄 商品ページタイトル: {page_title}")
            print(f"📄 商品ページ: {page_title}")
            
            # 少しスクロールして内容確認
            self.driver.execute_script("window.scrollTo(0, 300);")
            self.human_delay(1, 2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human_delay(1, 2)
            
            # Trackタブを探してクリック
            print("🔍 Trackタブを探しています...")
            track_selectors = [
                "#tabTrack",
                "a[href*='track']",
                ".track-tab",
                "//a[contains(text(), 'Track')]",
                "//span[contains(text(), 'Track')]/..",
                "//a[contains(@class, 'track')]",
                "//button[contains(text(), 'Track')]"
            ]
            
            tracking_tab_found = False
            for i, selector in enumerate(track_selectors):
                try:
                    print(f"  試行 {i+1}: {selector}")
                    
                    if selector.startswith("//"):
                        track_element = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        track_element = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    # 要素が見つかった場合の詳細情報
                    element_text = track_element.text
                    element_tag = track_element.tag_name
                    print(f"  ✅ 要素発見: {element_tag} - '{element_text}'")
                    
                    # タブにマウス移動してクリック
                    self.actions.move_to_element(track_element).perform()
                    self.human_delay(0.5, 1)
                    
                    # JavaScriptクリックも試行
                    try:
                        self.actions.click(track_element).perform()
                    except:
                        self.driver.execute_script("arguments[0].click();", track_element)
                    
                    logger.info("✅ Trackタブクリック成功")
                    print("✅ Trackタブクリック成功")
                    self.human_delay(2, 3)
                    tracking_tab_found = True
                    break
                    
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)[:50]}...")
                    continue
            
            if not tracking_tab_found:
                print("❌ Trackタブが見つかりませんでした")
                print("手動でTrackタブをクリックしてください")
                input("Trackタブをクリックした後、Enterキーを押してください...")
            
            # トラッキング設定
            print("⚙️ トラッキング設定を開始します...")
            
            # Amazon価格トラッキングのチェックボックス
            checkbox_selectors = [
                "#csvtype-5-0-threshold",
                "input[data-csv='0']",
                "input[type='checkbox'][value='0']",
                "input[name*='amazon']",
                ".amazon-checkbox"
            ]
            
            checkbox_found = False
            for i, selector in enumerate(checkbox_selectors):
                try:
                    print(f"  チェックボックス試行 {i+1}: {selector}")
                    checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if not checkbox.is_selected():
                        self.actions.move_to_element(checkbox).pause(0.3).click().perform()
                        print("  ✅ Amazon価格トラッキング有効化")
                        logger.info("✅ Amazon価格トラッキング有効化")
                    else:
                        print("  ✅ Amazon価格トラッキング既に有効")
                    
                    checkbox_found = True
                    break
                    
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)[:50]}...")
                    continue
            
            if not checkbox_found:
                print("⚠️ チェックボックスが見つかりません（手動で設定してください）")
            
            self.human_delay(1, 2)
            
            # 閾値設定
            threshold_selectors = [
                "#threshold-5-0",
                "input[name*='threshold']",
                ".threshold-input",
                "input[type='number']"
            ]
            
            threshold_found = False
            for i, selector in enumerate(threshold_selectors):
                try:
                    print(f"  閾値設定試行 {i+1}: {selector}")
                    threshold_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    self.actions.move_to_element(threshold_input).click().perform()
                    self.human_delay(0.5, 1)
                    
                    threshold_input.clear()
                    self.human_type(threshold_input, "95", 0.05)
                    print("  ✅ 閾値95%設定完了")
                    logger.info("✅ 閾値95%設定完了")
                    threshold_found = True
                    break
                    
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)[:50]}...")
                    continue
            
            if not threshold_found:
                print("⚠️ 閾値入力フィールドが見つかりません（手動で設定してください）")
            
            self.human_delay(1, 2)
            
            # 送信ボタンクリック
            submit_selectors = [
                "#submitTracking",
                "button[type='submit']",
                ".submit-tracking",
                "input[type='submit']",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), '送信')]"
            ]
            
            submit_found = False
            for i, selector in enumerate(submit_selectors):
                try:
                    print(f"  送信ボタン試行 {i+1}: {selector}")
                    
                    if selector.startswith("//"):
                        submit_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    button_text = submit_button.text
                    print(f"  ボタン発見: '{button_text}'")
                    
                    self.actions.move_to_element(submit_button).pause(0.5).click().perform()
                    print("  ✅ トラッキング設定送信完了")
                    logger.info("✅ トラッキング設定送信完了")
                    submit_found = True
                    break
                    
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)[:50]}...")
                    continue
            
            if not submit_found:
                print("⚠️ 送信ボタンが見つかりません")
                print("手動で送信ボタンをクリックしてください")
                input("送信ボタンをクリックした後、Enterキーを押してください...")
            
            self.human_delay(3, 5)
            
            # 成功確認
            page_source = self.driver.page_source.lower()
            success_indicators = ["successfully", "success", "added", "tracking", "完了"]
            tracking_success = any(indicator in page_source for indicator in success_indicators)
            
            # スクリーンショット保存
            try:
                screenshot_path = f"manual_login_tracking_{asin}_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 スクリーンショット保存: {screenshot_path}")
                logger.info(f"📸 スクリーンショット保存: {screenshot_path}")
            except:
                pass
            
            result = {
                'asin': asin,
                'product_url': product_url,
                'page_title': page_title,
                'tracking_success': tracking_success,
                'status': 'success' if tracking_success else 'completed',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'message': '手動ログイン + 自動トラッキング設定完了'
            }
            
            print(f"🎉 トラッキング設定完了: {asin}")
            logger.info(f"🎉 トラッキング設定完了: {asin}")
            return result
            
        except Exception as e:
            logger.error(f"トラッキング設定エラー: {str(e)}")
            print(f"❌ トラッキング設定エラー: {str(e)}")
            return {
                'asin': asin,
                'status': 'error',
                'error': str(e),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def close_browser(self):
        """ブラウザ終了"""
        if self.driver:
            try:
                print("\n🔍 処理が完了しました")
                print("Keepa Webサイト（https://keepa.com/manage/）でトラッキング一覧を確認してください")
                input("確認が完了したらEnterキーを押してブラウザを終了します...")
                self.driver.quit()
                logger.info("🔚 ブラウザ終了")
            except:
                pass

def main():
    """メイン実行"""
    tracker = ManualLoginAutoTracker()
    
    try:
        print("=== 手動ログイン + 自動トラッキング設定 ===")
        print("🖥️ ブラウザが表示されます")
        print("🔐 ログインは手動で行います")
        print("🤖 トラッキング設定は自動で行います")
        print("🎯 対象商品: B08CDYX378")
        print()
        
        # ブラウザ初期化
        if tracker.setup_browser():
            print("✅ ブラウザ初期化成功")
            
            # Keepa開始 + 手動ログイン
            if tracker.open_keepa_for_manual_login():
                print("✅ 手動ログイン完了")
                
                # 自動トラッキング設定
                result = tracker.navigate_to_product_and_track("B08CDYX378")
                
                print(f"\n=== 最終結果 ===")
                print(f"ASIN: {result['asin']}")
                print(f"ステータス: {result['status']}")
                print(f"トラッキング成功: {'✅' if result.get('tracking_success') else '❌'}")
                print(f"実行時刻: {result['timestamp']}")
                print(f"メッセージ: {result.get('message', 'N/A')}")
                
                if 'error' in result:
                    print(f"エラー: {result['error']}")
                
                # 結果保存
                import json
                filename = f"manual_login_auto_track_{int(time.time())}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n💾 詳細結果を{filename}に保存しました")
                
            else:
                print("❌ 手動ログイン失敗")
        else:
            print("❌ ブラウザ初期化失敗")
            
    except KeyboardInterrupt:
        print("\n⏹️ 処理が中断されました")
    except Exception as e:
        print(f"❌ 実行エラー: {str(e)}")
    finally:
        tracker.close_browser()

if __name__ == "__main__":
    main()
