# save_session.py
from playwright.sync_api import sync_playwright
import time

USERNAME = "username_here"  # ← غيّرها ليوزر حسابك
PASSWORD = "password_here"  # ← غيّرها لباسورد حسابك

with sync_playwright() as p:
    # نسوي session ثابتة ونحفظ الجلسة داخل ig_session
    context = p.chromium.launch_persistent_context(
        user_data_dir="ig_session",
        headless=False
    )
    page = context.pages[0]

    # روح لصفحة تسجيل الدخول
    page.goto("https://www.instagram.com/accounts/login/")
    page.wait_for_timeout(5000)

    # فلّ الحقول
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_timeout(7000)

    # أحياناً تظهر popup "Save Info" أو "Turn on Notifications"
    try:
        page.click('text="Not Now"')
        page.wait_for_timeout(2000)
    except:
        pass

    try:
        page.click('text="Not Now"')  # للمرة الثانية
        page.wait_for_timeout(2000)
    except:
        pass

    # دخلت للصفحة الرئيسية؟ خلاص
    print("✅ سجلت دخولك بنجاح، الجلسة محفوظة")
    input("⌨️ اضغط Enter بعد التأكد أنك داخل الحساب...")

    context.close()
