#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أتمتة شراء بطاقات Umniah PUBG - النسخة المتوازية (4 متصفحات بنفس الوقت)
"""

import subprocess
import sys
import time
import requests
import os
import threading
from datetime import datetime
from multiprocessing import Process
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
# البيانات والإعدادات
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
PAGE_LOAD_TIME = 2.5
SUCCESS_WAIT_TIME = 10
FAST_WAIT = 0.05
SLEEP_BEFORE_ORDER = 1

# ⭐ ملفات الأرقام (اضبطها حسب اللي عندك)
WALLET_FILES = [
    "lu1.txt",
    "lu2.txt",
    "lu3.txt",
    "lu4.txt"
]

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
        """قراءة الأرقام من الملف"""
        if not os.path.exists(self.filename):
            return False
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.wallets = [line.strip() for line in f if line.strip()]
            return True
        except Exception as e:
            return False
    
    def remove_wallet(self, wallet):
        """حذف رقم من الملف"""
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
    
    def get_remaining(self):
        """الأرقام المتبقية"""
        return len(self.wallets)

# ============================================================================
# إعداد المتصفح
# ============================================================================

def setup_driver():
    """إعداد المتصفح"""
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

def send_telegram_async(wallet_number, instance_num):
    """إرسال للتليجرام بدون انتظار"""
    def send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            text = f"✅ نجح!\n━━━━━━━━━━\n📱 المحفظة: {wallet_number}\n🔹 العملية #{instance_num}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        except:
            pass
    
    thread = threading.Thread(target=send, daemon=True)
    thread.start()

# ============================================================================
# خطوات العملية
# ============================================================================

def run_purchase(driver, wallet_number):
    """
    تشغيل عملية الشراء
    Returns:
        "success" = حذف + إرسال بوت
        "reached_wallet" = حذف، بدون بوت
        "network_error" = لا تحذف
    """
    try:
        # الخطوة 1: إضافة للسلة
        driver.get(PRODUCT_URL)
        time.sleep(PAGE_LOAD_TIME)
        
        if not fill_fast(driver, "//input[@name='qty']", "2"):
            return "network_error"
        
        if not click_fast(driver, "//button[@id='product-addtocart-button']"):
            return "network_error"
        
        time.sleep(1)
        
        # الخطوة 2: الانتقال للدفع
        driver.get(CHECKOUT_URL)
        time.sleep(PAGE_LOAD_TIME)
        
        # الخطوة 3: ملء البيانات
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
        
        # الخطوة 4: اختيار الدفع
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
                    break
            except:
                pass
        
        # الخطوة 5: الشروط
        checkbox = wait_element(driver, By.XPATH, "//input[@type='checkbox' and @class='checkbox required-entry']", 5)
        if checkbox and not checkbox.is_selected():
            driver.execute_script("""
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """, checkbox)
        
        # الخطوة 6: الانتظار قبل الضغط على إجراء الطلب
        time.sleep(SLEEP_BEFORE_ORDER)
        
        # الخطوة 7: إجراء الطلب
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
            return "network_error"
        
        time.sleep(2)
        
        # الخطوة 8: إدخال المحفظة
        wallet_input = wait_element(driver, By.ID, "phone_number", WAIT_TIME)
        
        if not wallet_input:
            return "network_error"
        
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        """, wallet_input, wallet_number)
        
        time.sleep(0.3)
        
        reached_wallet_page = True
        
        # الخطوة 9: إرسال رمز التحقق
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
            return "reached_wallet" if reached_wallet_page else "network_error"
        
        driver.execute_script("""
            arguments[0].disabled = false;
            arguments[0].removeAttribute('disabled');
            arguments[0].click();
        """, send_button)
        
        # الخطوة 10: انتظر النتيجة
        for i in range(SUCCESS_WAIT_TIME):
            time.sleep(1)
            
            try:
                current_url = driver.current_url
                if SUCCESS_URL in current_url:
                    page_text = driver.execute_script("return document.body.innerText;")
                    if "تم ارسال رمز التحقق بنجاح" in page_text:
                        return "success"
            except:
                pass
        
        return "reached_wallet" if reached_wallet_page else "network_error"
        
    except Exception as e:
        return "network_error"

# ============================================================================
# معالج كل عملية (لكل ملف أرقام)
# ============================================================================

def process_wallet_file(wallet_file, instance_num):
    """معالج لكل ملف أرقام في عملية منفصلة"""
    manager = WalletManager(wallet_file)
    
    if not manager.wallets:
        print(f"[#️⃣ {instance_num}] ❌ ملف فارغ: {wallet_file}")
        return
    
    print(f"[#️⃣ {instance_num}] ✅ بدء المعالجة: {wallet_file} ({len(manager.wallets)} رقم)")
    
    total = len(manager.wallets)
    successful = 0
    reached_wallet = 0
    driver = None
    retry_wallets = []
    
    try:
        # المعالجة الأولية
        for idx, wallet in enumerate(manager.wallets[:]):
            print(f"[#️⃣ {instance_num}] [{idx + 1}/{total}] {wallet}", end=" → ")
            
            try:
                driver = setup_driver()
                result = run_purchase(driver, wallet)
                
                if result == "success":
                    print("✅")
                    manager.remove_wallet(wallet)
                    send_telegram_async(wallet, instance_num)
                    successful += 1
                elif result == "reached_wallet":
                    print("⊘")
                    manager.remove_wallet(wallet)
                    reached_wallet += 1
                else:  # network_error
                    print("⚠️")
                    retry_wallets.append(wallet)
                
            except Exception:
                print("⚠️")
                retry_wallets.append(wallet)
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            
            time.sleep(0.3)
        
        # إعادة محاولة
        if retry_wallets:
            print(f"\n[#️⃣ {instance_num}] 🔄 إعادة محاولة {len(retry_wallets)}\n")
            
            for wallet in retry_wallets:
                print(f"[#️⃣ {instance_num}]    {wallet}", end=" → ")
                
                try:
                    driver = setup_driver()
                    result = run_purchase(driver, wallet)
                    
                    if result == "success":
                        print("✅")
                        manager.remove_wallet(wallet)
                        send_telegram_async(wallet, instance_num)
                        successful += 1
                    elif result == "reached_wallet":
                        print("⊘")
                        manager.remove_wallet(wallet)
                        reached_wallet += 1
                    else:
                        print("⚠️")
                
                except Exception:
                    print("⚠️")
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                time.sleep(0.3)
        
        print(f"\n[#️⃣ {instance_num}] ✅ النتيجة: ✅{successful} | ⊘{reached_wallet} | 📊{manager.get_remaining()}")
        
    except Exception:
        pass
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# ============================================================================
# البرنامج الرئيسي
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("🚀 أتمتة شراء Umniah PUBG - النسخة المتوازية (4 متصفحات)")
    print("=" * 70 + "\n")
    
    # التحقق من وجود ملفات الأرقام
    for i, wallet_file in enumerate(WALLET_FILES, 1):
        if not os.path.exists(wallet_file):
            print(f"⚠️  تحذير: ملف {wallet_file} غير موجود (العملية #{i})")
    
    print()
    
    # إنشاء 4 عمليات منفصلة
    processes = []
    
    for i, wallet_file in enumerate(WALLET_FILES, 1):
        p = Process(target=process_wallet_file, args=(wallet_file, i))
        processes.append(p)
        p.start()
    
    # انتظر انتهاء جميع العمليات
    for p in processes:
        p.join()
    
    print("\n" + "=" * 70)
    print("✅ انتهت جميع العمليات!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
