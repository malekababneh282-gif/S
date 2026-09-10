#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أتمتة شراء بطاقات Umniah PUBG - النسخة السريعة المحسنة
Umniah PUBG Card Purchase Automation - Fast Optimized Version
"""

import subprocess
import sys
import time
import requests
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def install_requirements():
    packages = ['selenium', 'webdriver-manager', 'requests']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 تثبيت {package}...")
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

WAIT_TIME = 15  # تقليل من 20
PAGE_LOAD_TIME = 2  # تقليل من 4
SUCCESS_WAIT_TIME = 10
FAST_WAIT = 0.1  # بدل 0.3 أو 0.5

# ============================================================================
# ملف تتبع التقدم
# ============================================================================

PROGRESS_FILE = "progress.json"

def load_progress():
    """تحميل آخر موضع توقفت عنده"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"current_index": 0, "wallet_numbers": []}

def save_progress(data):
    """حفظ موضع التوقف"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_wallet_numbers():
    """قراءة أرقام المحافظ من lu.txt"""
    if not os.path.exists("lu.txt"):
        print("❌ ملف lu.txt غير موجود!")
        return []
    
    try:
        with open("lu.txt", 'r', encoding='utf-8') as f:
            wallets = [line.strip() for line in f if line.strip()]
        print(f"✅ تم قراءة {len(wallets)} رقم محفظة من lu.txt\n")
        return wallets
    except Exception as e:
        print(f"❌ خطأ في قراءة lu.txt: {e}")
        return []

# ============================================================================
# إعداد المتصفح
# ============================================================================

def setup_driver():
    """إعداد المتصفح - محسن للسرعة"""
    print("🔧 إعداد المتصفح...")
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")  # تعطيل الصور لتسريع التحميل
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-plugins-power-saver")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    
    # تعيين timeouts
    driver.set_page_load_timeout(WAIT_TIME)
    driver.set_script_timeout(WAIT_TIME)
    
    print("✅ تم إعداد المتصفح\n")
    return driver

# ============================================================================
# الدوال المساعدة - محسنة
# ============================================================================

def wait_for_element(driver, by, value, timeout=WAIT_TIME):
    """انتظر لحين ظهور العنصر"""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None

def click_element_fast(driver, xpath):
    """انقر على عنصر - محسن"""
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", element)
        time.sleep(FAST_WAIT)
        driver.execute_script("arguments[0].click();", element)  # JavaScript click أسرع
        return True
    except:
        return False

def fill_input_fast(driver, xpath, text):
    """ملء حقل نصي - محسن"""
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", element)
        time.sleep(FAST_WAIT)
        
        # استخدم JavaScript للملء - أسرع
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        """, element, text)
        
        return True
    except:
        return False

def send_telegram(wallet_number, message, status="success"):
    """إرسال رسالة للتليجرام"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        status_emoji = "✅" if status == "success" else "❌"
        text = f"{status_emoji} نتيجة الشراء:\n━━━━━━━━━━\n📱 رقم المحفظة: {wallet_number}\n💬 {message}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        if response.status_code == 200:
            print("✅ تم إرسال الرسالة للتليجرام\n")
            return True
    except Exception as e:
        print(f"⚠️ خطأ في التليجرام: {e}")
    return False

# ============================================================================
# الخطوات - محسنة للسرعة
# ============================================================================

def step1_add_to_cart(driver):
    """الخطوة 1: إضافة للسلة"""
    print("📍 الخطوة 1: إضافة للسلة")
    try:
        driver.get(PRODUCT_URL)
        time.sleep(PAGE_LOAD_TIME)
        
        if not fill_input_fast(driver, "//input[@name='qty']", "2"):
            print("❌ فشل إدخال الكمية")
            return False
        
        time.sleep(FAST_WAIT)
        
        if not click_element_fast(driver, "//button[@id='product-addtocart-button']"):
            print("❌ فشل النقر على إضافة للسلة")
            return False
        
        time.sleep(1.5)  # انتظر العملية تتم
        print("✅ تمت الخطوة 1\n")
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def step2_checkout(driver):
    """الخطوة 2: الانتقال للدفع"""
    print("📍 الخطوة 2: الانتقال لصفحة الدفع")
    try:
        driver.get(CHECKOUT_URL)
        time.sleep(PAGE_LOAD_TIME)
        print("✅ تمت الخطوة 2\n")
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def step3_fill_info(driver):
    """الخطوة 3: ملء البيانات - سريع"""
    print("📍 الخطوة 3: ملء بيانات العميل")
    
    try:
        # البريد
        print("📧 ملء البريد...")
        fill_input_fast(driver, "//input[@id='customer-email']", EMAIL)
        time.sleep(FAST_WAIT)
        
        # رقم الهاتف
        print("📞 ملء الهاتف...")
        try:
            phone_element = wait_for_element(driver, By.ID, "phoneNumber", WAIT_TIME)
            if phone_element:
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
                """, phone_element, PHONE)
                time.sleep(FAST_WAIT)
        except:
            pass
        
        # الاسم
        print("👤 ملء الاسم...")
        try:
            name_element = wait_for_element(driver, By.XPATH, "//input[@class='input-text form-input']", WAIT_TIME)
            if name_element:
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                """, name_element, FULL_NAME)
                time.sleep(FAST_WAIT)
        except:
            pass
        
        print("✅ تمت الخطوة 3\n")
        return True
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        return True  # استمر على أي حال

def step4_payment_method(driver):
    """الخطوة 4: اختيار UWallet"""
    print("📍 الخطوة 4: اختيار طريقة الدفع UWallet")
    
    try:
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(FAST_WAIT)
        
        radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
        
        for i, radio in enumerate(radios):
            try:
                radio_id = radio.get_attribute("id") or ""
                radio_value = radio.get_attribute("value") or ""
                
                label_text = ""
                try:
                    if radio_id:
                        label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                        label_text = label.text
                except:
                    pass
                
                if 'uwallet' in label_text.lower() or 'uwallet' in radio_value.lower():
                    driver.execute_script("arguments[0].click();", radio)
                    time.sleep(FAST_WAIT)
                    print("✅ تم تحديد UWallet\n")
                    return True
            except:
                pass
        
        print("⚠️ لم يتم العثور على UWallet - استمرار على أي حال\n")
        return True
        
    except Exception as e:
        print(f"⚠️ خطأ: {e}\n")
        return True

def step5_agree_terms(driver):
    """الخطوة 5: الموافقة على الشروط"""
    print("📍 الخطوة 5: الموافقة على الشروط")
    
    try:
        checkbox = wait_for_element(driver, By.XPATH, "//input[@type='checkbox' and @class='checkbox required-entry']", WAIT_TIME)
        
        if checkbox:
            driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", checkbox)
            time.sleep(FAST_WAIT)
            
            if not checkbox.is_selected():
                driver.execute_script("""
                    arguments[0].checked = true;
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('click', {bubbles: true}));
                """, checkbox)
                time.sleep(FAST_WAIT)
        
        print("✅ تمت الخطوة 5\n")
        return True
        
    except Exception as e:
        print(f"⚠️ خطأ: {e}\n")
        return True

def step6_place_order(driver):
    """الخطوة 6: إجراء الطلب"""
    print("📍 الخطوة 6: إجراء الطلب")
    
    order_xpaths = [
        "//button[contains(@class, 'place-order')]",
        "//button[contains(text(), 'إجراء الطلب')]",
        "//div[@class='actions-toolbar']//button[contains(@class, 'btn-primary')]"
    ]
    
    for xp in order_xpaths:
        if click_element_fast(driver, xp):
            print("✅ تم الضغط على إجراء الطلب")
            time.sleep(3)
            print("✅ تمت الخطوة 6\n")
            return True
    
    print("❌ فشل إجراء الطلب\n")
    return False

def step7_wallet_otp(driver, wallet_number):
    """الخطوة 7: إدخال المحفظة و OTP"""
    print(f"📍 الخطوة 7: إدخال رقم المحفظة: {wallet_number}")
    
    try:
        wallet_input = wait_for_element(driver, By.ID, "phone_number", WAIT_TIME)
        
        if not wallet_input:
            print("❌ لم يتم العثور على حقل المحفظة")
            return False
        
        driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", wallet_input)
        time.sleep(FAST_WAIT)
        
        # ملء المحفظة
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
        """, wallet_input, wallet_number)
        
        time.sleep(0.5)
        
        print(f"✅ تم إدخال رقم المحفظة: {wallet_number}")
        
        # ابحث عن زر الإرسال
        print("🔍 البحث عن زر الإرسال...")
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
            print("❌ فشل العثور على زر الإرسال")
            return False
        
        # تفعيل الزر
        driver.execute_script("""
            arguments[0].disabled = false;
            arguments[0].removeAttribute('disabled');
            arguments[0].click();
        """, send_button)
        
        print("✅ تم الضغط على الزر")
        time.sleep(1.5)
        print("✅ تمت الخطوة 7\n")
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def step8_check_result(driver, wallet_number):
    """الخطوة 8: التحقق من النتيجة - محسنة"""
    print("📍 الخطوة 8: التحقق من النتيجة والانتظار")
    
    print(f"⏳ الانتظار {SUCCESS_WAIT_TIME} ثواني على صفحة النجاح...\n")
    
    for i in range(SUCCESS_WAIT_TIME):
        remaining = SUCCESS_WAIT_TIME - i
        print(f"⏳ {remaining}s...", end="\r")
        time.sleep(1)
        
        try:
            current_url = driver.current_url
            if SUCCESS_URL in current_url:
                print(f"\n✅ وصلنا لصفحة النجاح!")
                time.sleep(0.5)
                
                # ابحث عن رسالة النجاح
                try:
                    page_text = driver.execute_script("return document.body.innerText;")
                    if "تم ارسال رمز التحقق بنجاح" in page_text:
                        print("✅ وجدنا رسالة: تم ارسال رمز التحقق بنجاح!")
                        
                        # أرسل للتليجرام
                        send_telegram(wallet_number, "تم ارسال رمز التحقق بنجاح!", status="success")
                        print("✅ تمت الخطوة 8\n")
                        return True
                except:
                    pass
        except:
            pass
    
    print("\n❌ لم نصل لرسالة النجاح المطلوبة\n")
    return False

# ============================================================================
# البرنامج الرئيسي
# ============================================================================

def main():
    print("=" * 70)
    print("🚀 بدء أتمتة شراء Umniah PUBG - النسخة السريعة")
    print("=" * 70)
    print()
    
    # قراءة أرقام المحافظ
    wallet_numbers = read_wallet_numbers()
    if not wallet_numbers:
        print("❌ لا توجد أرقام محافظ للمعالجة!")
        return
    
    # تحميل التقدم السابق
    progress = load_progress()
    current_index = progress.get("current_index", 0)
    
    retry_wallets = []
    driver = None
    
    try:
        # معالجة الأرقام الأساسية
        for idx in range(current_index, len(wallet_numbers)):
            wallet = wallet_numbers[idx].strip()
            if not wallet:
                continue
            
            print("\n" + "=" * 70)
            print(f"🔄 معالجة الرقم {idx + 1}/{len(wallet_numbers)}")
            print(f"📱 المحفظة: {wallet}")
            print("=" * 70 + "\n")
            
            try:
                driver = setup_driver()
                
                steps = [
                    ("إضافة للسلة", lambda d: step1_add_to_cart(d)),
                    ("الانتقال للدفع", lambda d: step2_checkout(d)),
                    ("ملء البيانات", lambda d: step3_fill_info(d)),
                    ("اختيار الدفع", lambda d: step4_payment_method(d)),
                    ("الموافقة على الشروط", lambda d: step5_agree_terms(d)),
                    ("إجراء الطلب", lambda d: step6_place_order(d)),
                    ("إدخال المحفظة والـ OTP", lambda d: step7_wallet_otp(d, wallet)),
                ]
                
                step_failed = False
                for step_name, step_func in steps:
                    if not step_func(driver):
                        print(f"❌ فشلت خطوة: {step_name}")
                        retry_wallets.append((idx, wallet))
                        step_failed = True
                        break
                
                if not step_failed:
                    success = step8_check_result(driver, wallet)
                    if not success:
                        retry_wallets.append((idx, wallet))
                
            except Exception as e:
                print(f"❌ خطأ في معالجة الرقم {wallet}: {e}")
                retry_wallets.append((idx, wallet))
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            
            # حفظ التقدم
            save_progress({"current_index": idx + 1, "wallet_numbers": wallet_numbers})
            time.sleep(1)
        
        # محاولة إعادة الأرقام الفاشلة
        if retry_wallets:
            print("\n" + "=" * 70)
            print(f"🔄 إعادة محاولة {len(retry_wallets)} رقم فشل")
            print("=" * 70 + "\n")
            
            for idx, wallet in retry_wallets:
                print("\n" + "=" * 70)
                print(f"🔄 إعادة محاولة الرقم: {wallet}")
                print("=" * 70 + "\n")
                
                try:
                    driver = setup_driver()
                    
                    steps = [
                        ("إضافة للسلة", lambda d: step1_add_to_cart(d)),
                        ("الانتقال للدفع", lambda d: step2_checkout(d)),
                        ("ملء البيانات", lambda d: step3_fill_info(d)),
                        ("اختيار الدفع", lambda d: step4_payment_method(d)),
                        ("الموافقة على الشروط", lambda d: step5_agree_terms(d)),
                        ("إجراء الطلب", lambda d: step6_place_order(d)),
                        ("إدخال المحفظة والـ OTP", lambda d: step7_wallet_otp(d, wallet)),
                    ]
                    
                    step_failed = False
                    for step_name, step_func in steps:
                        if not step_func(driver):
                            print(f"❌ فشلت خطوة: {step_name}")
                            step_failed = True
                            break
                    
                    if not step_failed:
                        step8_check_result(driver, wallet)
                
                except Exception as e:
                    print(f"❌ خطأ في إعادة محاولة الرقم {wallet}: {e}")
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                time.sleep(1)
        
        print("\n" + "=" * 70)
        print("✅ انتهت عملية معالجة جميع الأرقام!")
        print("=" * 70)
        
        # مسح ملف التقدم
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}\n")
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
