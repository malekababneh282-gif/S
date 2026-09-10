#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أتمتة شراء بطاقات Umniah PUBG - النسخة الاحترافية النظيفة
Umniah PUBG Card Purchase Automation - Professional Clean Version
"""

import subprocess
import sys
import time
import requests
import os
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def install_requirements():
    packages = ['selenium', 'webdriver-manager', 'requests']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

install_requirements()

# ============================================================================
# البيانات
# ============================================================================
PRODUCT_URL = "https://eshop.umniah.com/ar/بطاقة-هدية-ببجي-600-يو-سي.html"
CHECKOUT_URL = "https://eshop.umniah.com/ar/checkout/index/"
SUCCESS_URL = "https://eshop.umniah.com/ar/checkout/onepage/success"

PHONE = "797230107"
EMAIL = "ggssgg@gmail.com"
FULL_NAME = "testtesttest"

TELEGRAM_TOKEN = "7327256170:AAEiQ_F_BI1V9iUHzgPPui7JRwqGnj6Jys4"
TELEGRAM_CHAT_ID = "6873334348"

WAIT_TIME = 12
PAGE_LOAD_TIME = 1.5
SUCCESS_WAIT_TIME = 10
FAST_WAIT = 0.05

# ============================================================================
# إدارة الأرقام
# ============================================================================

class WalletManager:
    def __init__(self, filename="lu.txt"):
        self.filename = filename
        self.lock = threading.Lock()
        self.wallets = []
        self.load_wallets()
    
    def load_wallets(self):
        """قراءة الأرقام من lu.txt"""
        if not os.path.exists(self.filename):
            print("❌ ملف lu.txt غير موجود!")
            return False
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.wallets = [line.strip() for line in f if line.strip()]
            print(f"✅ تم قراءة {len(self.wallets)} رقم محفظة\n")
            return True
        except Exception as e:
            print(f"❌ خطأ في قراءة lu.txt: {e}")
            return False
    
    def remove_wallet(self, wallet):
        """حذف رقم من lu.txt"""
        with self.lock:
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                with open(self.filename, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != wallet:
                            f.write(line)
                
                if wallet in self.wallets:
                    self.wallets.remove(wallet)
                
                return True
            except:
                return False

# ============================================================================
# إعداد المتصفح
# ============================================================================

def setup_driver():
    """إعداد المتصفح للسرعة القصوى"""
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--disable-default-apps")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(WAIT_TIME)
    driver.set_script_timeout(WAIT_TIME)
    
    return driver

# ============================================================================
# الدوال المساعدة
# ============================================================================

def wait_element(driver, by, value, timeout=WAIT_TIME):
    """انتظر العنصر"""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None

def click_fast(driver, xpath):
    """انقر سريع"""
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        return False

def fill_fast(driver, xpath, text):
    """ملء سريع"""
    try:
        element = wait_element(driver, By.XPATH, xpath, WAIT_TIME)
        if element:
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, element, text)
            return True
    except:
        pass
    return False

def send_telegram_async(wallet_number, message):
    """إرسال للتليجرام بشكل غير متزامن"""
    def send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            text = f"✅ نجح!\n━━━━━━━━━━\n📱 المحفظة: {wallet_number}\n💬 {message}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        except:
            pass
    
    thread = threading.Thread(target=send, daemon=True)
    thread.start()

# ============================================================================
# خطوات العملية
# ============================================================================

def run_purchase(driver, wallet_number):
    """تشغيل عملية الشراء كاملة"""
    try:
        # الخطوة 1: إضافة للسلة
        print("  ➤ إضافة للسلة...", end=" ", flush=True)
        driver.get(PRODUCT_URL)
        time.sleep(PAGE_LOAD_TIME)
        
        if not fill_fast(driver, "//input[@name='qty']", "2"):
            print("❌")
            return False
        
        if not click_fast(driver, "//button[@id='product-addtocart-button']"):
            print("❌")
            return False
        
        time.sleep(1)
        print("✅")
        
        # الخطوة 2: الانتقال للدفع
        print("  ➤ الانتقال للدفع...", end=" ", flush=True)
        driver.get(CHECKOUT_URL)
        time.sleep(PAGE_LOAD_TIME)
        print("✅")
        
        # الخطوة 3: ملء البيانات
        print("  ➤ ملء البيانات...", end=" ", flush=True)
        fill_fast(driver, "//input[@id='customer-email']", EMAIL)
        
        phone_element = wait_element(driver, By.ID, "phoneNumber", 5)
        if phone_element:
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, phone_element, PHONE)
        
        name_element = wait_element(driver, By.XPATH, "//input[@class='input-text form-input']", 5)
        if name_element:
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, name_element, FULL_NAME)
        
        print("✅")
        
        # الخطوة 4: اختيار الدفع
        print("  ➤ اختيار UWallet...", end=" ", flush=True)
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(FAST_WAIT)
        
        radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
        for radio in radios:
            try:
                radio_id = radio.get_attribute("id") or ""
                label_text = ""
                try:
                    if radio_id:
                        label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                        label_text = label.text
                except:
                    pass
                
                if 'uwallet' in label_text.lower():
                    driver.execute_script("arguments[0].click();", radio)
                    time.sleep(FAST_WAIT)
                    print("✅")
                    break
            except:
                pass
        else:
            print("✅")
        
        # الخطوة 5: الشروط
        print("  ➤ قبول الشروط...", end=" ", flush=True)
        checkbox = wait_element(driver, By.XPATH, "//input[@type='checkbox' and @class='checkbox required-entry']", 5)
        if checkbox and not checkbox.is_selected():
            driver.execute_script("""
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, checkbox)
        print("✅")
        
        # الخطوة 6: إجراء الطلب
        print("  ➤ إجراء الطلب...", end=" ", flush=True)
        order_xpaths = [
            "//button[contains(@class, 'place-order')]",
            "//button[contains(text(), 'إجراء الطلب')]",
            "//div[@class='actions-toolbar']//button[contains(@class, 'btn-primary')]"
        ]
        
        clicked = False
        for xp in order_xpaths:
            if click_fast(driver, xp):
                clicked = True
                break
        
        if not clicked:
            print("❌")
            return False
        
        time.sleep(2)
        print("✅")
        
        # الخطوة 7: إدخال المحفظة
        print("  ➤ إدخال المحفظة...", end=" ", flush=True)
        wallet_input = wait_element(driver, By.ID, "phone_number", WAIT_TIME)
        
        if not wallet_input:
            print("❌")
            return False
        
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        """, wallet_input, wallet_number)
        
        time.sleep(0.3)
        print("✅")
        
        # الخطوة 8: الضغط على الإرسال
        print("  ➤ إرسال رمز التحقق...", end=" ", flush=True)
        send_button_xpaths = [
            "//button[contains(@class, 'btn-primary') and contains(., 'إرسال')]",
            "//button[contains(text(), 'إرسال رمز التحقق')]",
            "//button[contains(@class, 'btn') and contains(@class, 'primary')]"
        ]
        
        send_button = None
        for xpath in send_button_xpaths:
            try:
                buttons = driver.find_elements(By.XPATH, xpath)
                if buttons:
                    send_button = buttons[0]
                    break
            except:
                pass
        
        if not send_button:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in all_buttons:
                try:
                    if 'إرسال' in btn.text:
                        send_button = btn
                        break
                except:
                    pass
        
        if not send_button:
            print("❌")
            return False
        
        driver.execute_script("""
            arguments[0].disabled = false;
            arguments[0].removeAttribute('disabled');
            arguments[0].click();
        """, send_button)
        
        print("✅")
        
        # الخطوة 9: انتظر النتيجة
        print("  ➤ انتظار النتيجة...", end=" ", flush=True)
        
        for i in range(SUCCESS_WAIT_TIME):
            time.sleep(1)
            
            try:
                current_url = driver.current_url
                if SUCCESS_URL in current_url:
                    page_text = driver.execute_script("return document.body.innerText;")
                    if "تم ارسال رمز التحقق بنجاح" in page_text:
                        print("✅")
                        return True
            except:
                pass
        
        print("❌")
        return False
        
    except Exception:
        return False

# ============================================================================
# البرنامج الرئيسي
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("🚀 أتمتة شراء Umniah PUBG")
    print("=" * 70 + "\n")
    
    manager = WalletManager()
    
    if not manager.wallets:
        return
    
    total = len(manager.wallets)
    successful = 0
    driver = None
    retry_list = []
    
    try:
        # معالجة جميع الأرقام
        for idx, wallet in enumerate(manager.wallets[:]):
            print(f"[{idx + 1}/{total}] 📱 {wallet}")
            
            try:
                driver = setup_driver()
                success = run_purchase(driver, wallet)
                
                if success:
                    print(f"       🎉 نجح!\n")
                    manager.remove_wallet(wallet)
                    send_telegram_async(wallet, "تم ارسال رمز التحقق بنجاح!")
                    successful += 1
                else:
                    print(f"       ⚠️ إعادة محاولة لاحقاً\n")
                    retry_list.append(wallet)
                
            except Exception:
                print(f"       ⚠️ إعادة محاولة لاحقاً\n")
                retry_list.append(wallet)
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            
            time.sleep(0.5)
        
        # إعادة محاولة الأرقام الفاشلة
        if retry_list:
            print(f"\n🔄 إعادة محاولة {len(retry_list)} رقم\n")
            
            for wallet in retry_list:
                print(f"   🔄 {wallet}", end=" ")
                
                try:
                    driver = setup_driver()
                    success = run_purchase(driver, wallet)
                    
                    if success:
                        print(f"✅\n")
                        manager.remove_wallet(wallet)
                        send_telegram_async(wallet, "تم ارسال رمز التحقق بنجاح! (إعادة محاولة)")
                        successful += 1
                    else:
                        print(f"❌\n")
                
                except Exception:
                    print(f"❌\n")
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                time.sleep(0.5)
        
        print("\n" + "=" * 70)
        print(f"✅ انتهت العملية!")
        print(f"   ✅ نجح: {successful}")
        print(f"   ❌ فشل: {len(retry_list) - (len(retry_list) - sum(1 for w in retry_list if w not in manager.wallets))}")
        print(f"   📊 المتبقي: {len(manager.wallets)}")
        print("=" * 70 + "\n")
        
    except Exception:
        pass
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
