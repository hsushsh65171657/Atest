#!/usr/bin/env python3
import requests, uuid, random, string, re

def generate_user_agent():
    return f"Instagram 303.0.0.0.59 Android (28/9; 320dpi; 900x1600; {''.join(random.choices(string.ascii_lowercase+string.digits, k=8))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=8))}; en_GB;)"

def extract_cookies_from_set_cookie(headers):
    cookies = {}
    for k, v in headers.items():
        if k.lower() == "set-cookie":
            parts = v.split(";")
            for p in parts:
                if "=" in p:
                    name, val = p.strip().split("=", 1)
                    cookies[name] = val
    return cookies

def login(user, password):
    session = requests.Session()
    my_uuid = str(uuid.uuid4())
    rd = ''.join(random.choices(string.ascii_lowercase+string.digits, k=16))
    
    # Data payload للـ bloks login
    modified_uuid_str = my_uuid[:8] + "should_trigger_override_login_success_action" + my_uuid[8:]
    data = {"params": "{\"client_input_params\":{\"contact_point\":\"" + user + "\",\"password\":\"#PWD_INSTAGRAM:0:0:" +  password + "\"},\"server_params\":{\"waterfall_id\":\"" + modified_uuid_str + "\"}}"}
    
    headers = {
        "User-Agent": generate_user_agent(),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
    }

    resp = session.post(
        "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/",
        headers=headers,
        data=data
    )

    # 1) نحاول نستخرج sessionid من payload
    sessionid = None
    try:
        session_b64 = re.search(r'Bearer IGT:2:(.*?),', resp.text).group(1).strip()[:-8]
        import base64, json
        decoded = base64.b64decode(session_b64).decode()
        m = re.search(r'"sessionid":"(.*?)"', decoded)
        if m:
            sessionid = m.group(1)
    except:
        pass

    if not sessionid:
        print("[ ! ] Login failed")
        return

    # 2) نضيف sessionid لكوكيز السشن
    session.cookies.set("sessionid", sessionid, domain=".instagram.com", path="/")

    # 3) نعمل GET لصفحة ويب حتى يطلع بقية الكوكيز
    try:
        resp_web = session.get("https://www.instagram.com/", headers={"User-Agent": headers["User-Agent"]})
    except:
        pass

    # 4) نقرأ كل الكوكيز الموجودة بعد GET
    cookies = session.cookies.get_dict()

    # 5) نرتب الكوكيز بالترتيب المطلوب
    ordered = ["csrftoken", "rur", "mid", "ds_user_id", "sessionid"]
    cookie_string = "; ".join([f"{k}={cookies[k]}" for k in ordered if k in cookies]) + ";"

    print("[ + ] Logged in with @"+user)
    print("[ + ] Final Cookies string:")
    print(cookie_string)
    print("[ + ] User-Agent:")
    print(headers["User-Agent"])

if __name__ == "__main__":
    USER = input("[ + ] Username : ")
    PASSW = input("[ + ] Password : ")
    login(USER, PASSW)
