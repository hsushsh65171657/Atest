# save_session.py
from playwright.sync_api import sync_playwright

USERNAME = "username_here"
PASSWORD = "password_here"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="ig_session",
        headless=False
    )
    page = context.new_page()
    page.goto("https://www.instagram.com/accounts/login/")

    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')

    input("✅ بعد ما تدخل، اضغط Enter ...")
    print("✅ جلسة محفوظة")
    context.close()
