#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أتمتة شراء بطاقات Umniah PUBG - النسخة النهائية المصححة الكاملة
Umniah PUBG Card Purchase Automation - Final Complete Version
تحديث: قراءة الأرقام من lu.txt والتجربة المتتالية
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
from selenium.common.exceptions import TimeoutException
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
# WALLET_NUMBER سيتم قراءته من lu.txt

TELEGRAM_TOKEN = "7327256170:AAEiQ_F_BI1V9iUHzgPPui7JRwqGnj6Jys4"
TELEGRAM_CHAT_ID = "6873334348"

WAIT_TIME = 20
PAGE_LOAD_TIME = 4
SUCCESS_WAIT_TIME = 10  # 10 ثواني الانتظار على صفحة النجاح

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
    """إعداد المتصفح"""
    print("🔧 إعداد المتصفح...")
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✅ تم إعداد المتصفح\n")
    return driver

# ============================================================================
# الدوال المساعدة
# ============================================================================

def click_element(driver, xpath):
    """انقر على عنصر"""
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.3)
        element.click()
        return True
    except:
        return False

def fill_input(driver, xpath, text):
    """ملء حقل نصي"""
    try:
        element = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element.click()
        element.clear()
        element.send_keys(text)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
            element
        )
        time.sleep(0.3)
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
# الخطوات
# ============================================================================

def step1_add_to_cart(driver):
    """الخطوة 1: إضافة للسلة"""
    print("📍 الخطوة 1: إضافة للسلة")
    driver.get(PRODUCT_URL)
    time.sleep(PAGE_LOAD_TIME)
    
    if not fill_input(driver, "//input[@name='qty']", "2"):
        print("❌ فشل إدخال الكمية")
        return False
    time.sleep(1)
    
    if not click_element(driver, "//button[@id='product-addtocart-button']"):
        print("❌ فشل النقر على إضافة للسلة")
        return False
    
    time.sleep(3)
    print("✅ تمت الخطوة 1\n")
    return True

def step2_checkout(driver):
    """الخطوة 2: الانتقال للدفع"""
    print("📍 الخطوة 2: الانتقال لصفحة الدفع")
    driver.get(CHECKOUT_URL)
    time.sleep(PAGE_LOAD_TIME)
    print("✅ تمت الخطوة 2\n")
    return True

def step3_fill_info(driver):
    """الخطوة 3: ملء البيانات - مصححة تماماً"""
    print("📍 الخطوة 3: ملء بيانات العميل")
    
    # ========== البريد ==========
    print("📧 ملء البريد الإلكتروني...")
    try:
        fill_input(driver, "//input[@id='customer-email']", EMAIL)
        print(f"✅ تم إدخال البريد: {EMAIL}")
    except Exception as e:
        print(f"⚠️ خطأ في البريد: {e}")
    time.sleep(0.5)
    
    # ========== رقم الهاتف ==========
    print("📞 ملء رقم الهاتف...")
    try:
        phone_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "phoneNumber"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", phone_element)
        time.sleep(0.5)
        
        phone_element.click()
        time.sleep(0.2)
        phone_element.clear()
        time.sleep(0.2)
        
        phone_element.send_keys(PHONE)
        time.sleep(0.3)
        
        driver.execute_script("""
            var el = arguments[0];
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            el.dispatchEvent(new Event('blur', {bubbles: true}));
        """, phone_element)
        
        time.sleep(0.5)
        
        final_value = phone_element.get_attribute("value") or ""
        if PHONE in final_value:
            print(f"✅ تم إدخال رقم الهاتف: {PHONE}")
        else:
            print(f"⚠️ قيمة الهاتف: {final_value}")
            
    except Exception as e:
        print(f"❌ خطأ في رقم الهاتف: {e}")
    
    time.sleep(0.5)
    
    # ========== الاسم الكامل ==========
    print("👤 ملء الاسم الكامل...")
    try:
        name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@class='input-text form-input']"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", name_element)
        time.sleep(0.5)
        
        name_element.click()
        time.sleep(0.2)
        name_element.clear()
        time.sleep(0.2)
        
        name_element.send_keys(FULL_NAME)
        time.sleep(0.3)
        
        driver.execute_script("""
            var el = arguments[0];
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            el.dispatchEvent(new Event('blur', {bubbles: true}));
        """, name_element)
        
        time.sleep(0.5)
        
        final_value = name_element.get_attribute("value") or ""
        if FULL_NAME in final_value:
            print(f"✅ تم إدخال الاسم الكامل: {FULL_NAME}")
        else:
            print(f"⚠️ قيمة الاسم: {final_value}")
    
    except Exception as e:
        print(f"❌ خطأ في الاسم الكامل: {e}")
    
    print("✅ تمت الخطوة 3\n")
    return True

def step4_payment_method(driver):
    """الخطوة 4: اختيار طريقة الدفع UWallet"""
    print("📍 الخطوة 4: اختيار طريقة الدفع UWallet")
    
    try:
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(0.5)
        
        print("🔍 البحث عن خيارات الدفع...")
        radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
        print(f"📊 وجدت {len(radios)} خيار دفع")
        
        uwallet_found = False
        
        for i, radio in enumerate(radios):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio)
                time.sleep(0.3)
                
                radio_id = radio.get_attribute("id") or ""
                radio_value = radio.get_attribute("value") or ""
                
                label_text = ""
                try:
                    if radio_id:
                        label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                        label_text = label.text
                except:
                    pass
                
                print(f"   [{i}] Value: '{radio_value}' | Text: '{label_text[:50] if label_text else 'N/A'}'")
                
                if 'uwallet' in label_text.lower() or 'uwallet' in radio_value.lower():
                    print(f"✅ وجدت UWallet في الخيار {i}!")
                    
                    try:
                        radio.click()
                    except:
                        driver.execute_script("arguments[0].click();", radio)
                    
                    time.sleep(0.5)
                    
                    if radio.is_selected():
                        print("✅ تم تحديد UWallet بنجاح!")
                        uwallet_found = True
                        break
                    else:
                        driver.execute_script("""
                            arguments[0].checked = true;
                            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                        """, radio)
                        time.sleep(0.5)
                        
                        if radio.is_selected():
                            print("✅ تم تحديد UWallet بنجاح (via JavaScript)!")
                            uwallet_found = True
                            break
            
            except Exception as e:
                print(f"   ⚠️ خطأ في الخيار {i}: {e}")
                pass
        
        if uwallet_found:
            time.sleep(1)
            print("✅ تمت الخطوة 4\n")
            return True
        else:
            print("⚠️ لم يتم العثور على UWallet")
            print("✅ تمت الخطوة 4\n")
            return True
        
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")
        print("✅ تمت الخطوة 4\n")
        return True

def step5_agree_terms(driver):
    """الخطوة 5: الموافقة على الشروط والأحكام"""
    print("📍 الخطوة 5: الموافقة على الشروط والأحكام")
    
    try:
        print("🔍 البحث عن checkbox الشروط...")
        
        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and @class='checkbox required-entry']"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)
        time.sleep(0.5)
        
        is_checked = checkbox.is_selected()
        print(f"   الحالة الحالية: {'محدد ✓' if is_checked else 'غير محدد'}")
        
        if not is_checked:
            try:
                checkbox.click()
                time.sleep(0.5)
            except:
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.5)
            
            if not checkbox.is_selected():
                driver.execute_script("""
                    arguments[0].checked = true;
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('click', {bubbles: true}));
                """, checkbox)
                time.sleep(0.5)
        
        if checkbox.is_selected():
            print("✅ تم تحديد الشروط بنجاح!")
        else:
            print("⚠️ لم يتم تحديد الشروط رغم المحاولات - لكن سنستمر")
        
        time.sleep(1)
        print("✅ تمت الخطوة 5\n")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الشروط: {e}")
        print("✅ تمت الخطوة 5\n")
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
        if click_element(driver, xp):
            print("✅ تم الضغط على إجراء الطلب")
            time.sleep(5)
            print("✅ تمت الخطوة 6\n")
            return True
    
    print("❌ فشل إجراء الطلب")
    return False

def step7_wallet_otp(driver, wallet_number):
    """الخطوة 7: إدخال المحفظة و OTP - معدلة"""
    print(f"📍 الخطوة 7: إدخال رقم المحفظة: {wallet_number}")
    
    try:
        # البحث عن حقل المحفظة
        wallet_input = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "phone_number"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wallet_input)
        time.sleep(0.4)
        
        # ملء المحفظة
        wallet_input.click()
        time.sleep(0.2)
        wallet_input.clear()
        time.sleep(0.2)
        wallet_input.send_keys(wallet_number)
        
        # تفعيل الأحداث
        driver.execute_script("""
            const el = arguments[0];
            el.value = arguments[1];
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            el.dispatchEvent(new Event('blur', {bubbles: true}));
        """, wallet_input, wallet_number)
        
        time.sleep(0.7)
        
        # التحقق من القيمة
        final_value = wallet_input.get_attribute("value") or ""
        if wallet_number not in final_value:
            print(f"❌ فشل إدخال المحفظة: {final_value}")
            return False
        
        print(f"✅ تم إدخال رقم المحفظة: {wallet_number}")
        time.sleep(1)
        
        # البحث عن زر الإرسال وإزالة disabled
        print("🔍 البحث عن زر إرسال رمز التحقق...")
        
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
                    print(f"✅ وجدت الزر عبر: {xpath}")
                    break
            except:
                pass
        
        if send_button is None:
            print("⚠️ لم نتمكن من العثور على الزر - سنحاول البحث البديل")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in all_buttons:
                try:
                    if 'إرسال' in btn.text:
                        send_button = btn
                        print(f"✅ وجدت الزر: {btn.text}")
                        break
                except:
                    pass
        
        if send_button is None:
            print("❌ فشل العثور على زر الإرسال")
            return False
        
        # إزالة disabled وتفعيل الزر
        print("🔧 تفعيل الزر وإزالة disabled...")
        driver.execute_script("""
            const btn = arguments[0];
            btn.disabled = false;
            btn.removeAttribute('disabled');
            btn.classList.remove('disabled');
            return true;
        """, send_button)
        
        time.sleep(0.5)
        
        # النقر على الزر
        driver.execute_script("arguments[0].click();", send_button)
        print("✅ تم الضغط على الزر عبر JavaScript")
        
        time.sleep(3)
        print("✅ تمت الخطوة 7\n")
        return True
        
    except TimeoutException:
        print("❌ لم يتم العثور على حقل المحفظ��")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

def step8_check_result(driver, wallet_number):
    """الخطوة 8: التحقق من النتيجة والانتظار على صفحة النجاح"""
    print("📍 الخطوة 8: التحقق من النتيجة والانتظار على صفحة النجاح")
    
    print(f"\n⏳ جاري الانتظار للنتيجة من UWallet...")
    print(f"⏳ سيتم الانتظار لمدة {SUCCESS_WAIT_TIME} ثواني على صفحة النجاح...\n")
    
    start_time = time.time()
    success_message_found = False
    
    for i in range(SUCCESS_WAIT_TIME):
        remaining = SUCCESS_WAIT_TIME - i
        print(f"⏳ {remaining}s...", end="\r")
        time.sleep(1)
        
        # تحقق من الـ URL
        try:
            current_url = driver.current_url
            if SUCCESS_URL in current_url:
                print(f"\n✅ وصلنا لصفحة النجاح!")
                
                # ابحث عن رسالة النجاح
                page_text = driver.execute_script("return document.body.innerText;")
                
                if "تم ارسال رمز التحقق بنجاح" in page_text:
                    print("✅ وجدنا رسالة: تم ارسال رمز التحقق بنجاح!")
                    success_message_found = True
                    
                    # أرسل للتليجرام
                    send_telegram(wallet_number, "تم ارسال رمز التحقق بنجاح!", status="success")
                    return True
        except:
            pass
    
    print("\n")
    
    if not success_message_found:
        print("❌ لم نصل لرسالة النجاح المطلوبة")
        return False
    
    print("✅ تمت الخطوة 8\n")
    return True

# ============================================================================
# البرنامج الرئيسي
# ============================================================================

def main():
    print("=" * 70)
    print("🚀 بدء أتمتة شراء Umniah PUBG - النسخة المحسنة")
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
    
    # لو كان آخر محاولة فشلت (retry)
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
                    # تحقق من النتيجة والانتظار
                    success = step8_check_result(driver, wallet)
                    
                    if success:
                        print(f"✅ نجحت عملية الرقم: {wallet}")
                    else:
                        print(f"❌ فشلت عملية الرقم: {wallet}")
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
            time.sleep(2)
        
        # محاولة إعادة الأرقام التي فشلت
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
                        # تحقق من النتيجة والانتظار
                        success = step8_check_result(driver, wallet)
                        
                        if success:
                            print(f"✅ نجحت عملية الرقم بعد الإعادة: {wallet}")
                        else:
                            print(f"❌ فشلت عملية الرقم بعد الإعادة: {wallet}")
                
                except Exception as e:
                    print(f"❌ خطأ في إعادة محاولة الرقم {wallet}: {e}")
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                time.sleep(2)
        
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
                print("🔒 تم إغلاق المتصفح")
            except:
                pass

if __name__ == "__main__":
    main()
