#!/usr/bin/env python3
import requests, uuid, string, random, re, base64, urllib.parse
from http import cookies as http_cookies
import sys

my_uuid = uuid.uuid4()
my_uuid_str = str(my_uuid)
modified_uuid_str = my_uuid_str[:8] + "should_trigger_override_login_success_action" + my_uuid_str[8:]
rd = ''.join(random.choices(string.ascii_lowercase+string.digits, k=16))

def parse_set_cookie_from_headers(headers, out):
    """
    قرّاء لكل رؤوس الهيدر (dict-like) ويستخرج أي Set-Cookie key=value
    يضيفها إلى dict out
    """
    for k, v in headers.items():
        if k.lower() == 'set-cookie':
            # v ممكن يحتوي على عدة كوكيز مفصولة بفواصل أو تكون واحدة
            # نجيب كل key=value قبل أول ";" لكل قطعة
            parts = re.split(r',(?! )', v)  # محاولة لتقسيم متحفظ لو كانت رشا، fallback
            for p in parts:
                first = p.split(';', 1)[0].strip()
                if '=' in first:
                    name, val = first.split('=', 1)
                    out[name] = val

def collect_all_set_cookie_lines(responses):
    """
    responses: قائمة response-like objects
    يرجع list من كل key=value اللي لقيناها في كل هيدر Set-Cookie
    """
    lines = []
    for r in responses:
        for k, v in r.headers.items():
            if k.lower() == 'set-cookie':
                # قد يكون header فيه أكثر من كوكي مفصول بفاصلة
                # نأخذ كل key=value قبل أول ; لكل جزء
                # لكن أيضاً نحاول استخراج كل occurrences عبر regex
                matches = re.findall(r'([^=;\s]+=[^;,\s]+)', v)
                for m in matches:
                    lines.append(m)
    return lines

def login(user,password):
    s = requests.Session()
    data = {"params": "{\"client_input_params\":{\"contact_point\":\"" + user + "\",\"password\":\"#PWD_INSTAGRAM:0:0:" +  password + "\",\"fb_ig_device_id\":[],\"event_flow\":\"login_manual\",\"openid_tokens\":{},\"machine_id\":\"ZG93WAABAAEkJZWHLdW_Dm4nIE9C\",\"family_device_id\":\"\",\"accounts_list\":[],\"try_num\":1,\"login_attempt_count\":1,\"device_id\":\"android-" + rd + "\",\"auth_secure_device_id\":\"\",\"device_emails\":[],\"secure_family_device_id\":\"\",\"event_step\":\"home_page\"},\"server_params\":{\"is_platform_login\":0,\"qe_device_id\":\"\",\"family_device_id\":\"\",\"credential_type\":\"password\",\"waterfall_id\":\"" + modified_uuid_str + "\",\"username_text_input_id\":\"9cze54:46\",\"password_text_input_id\":\"9cze54:47\",\"offline_experiment_group\":\"caa_launch_ig4a_combined_60_percent\",\"INTERNAL__latency_qpl_instance_id\":56600226400306,\"INTERNAL_INFRA_THEME\":\"default\",\"device_id\":\"android-" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=16)) + "\",\"server_login_source\":\"login\",\"login_source\":\"Login\",\"should_trigger_override_login_success_action\":0,\"ar_event_source\":\"login_home_page\",\"INTERNAL__latency_qpl_marker_id\":36707139}}"}
    data["params"] = data["params"].replace("\"family_device_id\":\"\"", "\"family_device_id\":\"" +my_uuid_str + "\"")
    data["params"] = data["params"].replace("\"qe_device_id\":\"\"", "\"qe_device_id\":\"" + my_uuid_str + "\"")
    headers = {
        "Host": "i.instagram.com",
        "X-Ig-App-Locale": "ar_SA",
        "X-Ig-Device-Locale": "ar_SA",
        "X-Ig-Mapped-Locale": "ar_AR",
        "X-Pigeon-Session-Id": f"UFS-{uuid.uuid4()}-0",
        "X-Pigeon-Rawclienttime": "1685026670.130",
        "X-Ig-Bandwidth-Speed-Kbps": "-1.000",
        "X-Ig-Bandwidth-Totalbytes-B": "0",
        "X-Ig-Bandwidth-Totaltime-Ms": "0",
        "X-Bloks-Version-Id": "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb",
        "X-Ig-Www-Claim": "0",
        "X-Bloks-Is-Layout-Rtl": "true",
        "X-Ig-Device-Id": f"{uuid.uuid4()}",
        "X-Ig-Family-Device-Id": f"{uuid.uuid4()}",
        "X-Ig-Android-Id": f"android-{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}",
        "X-Ig-Timezone-Offset": "10800",
        "X-Fb-Connection-Type": "WIFI",
        "X-Ig-Connection-Type": "WIFI",
        "X-Ig-Capabilities": "3brTv10=",
        "X-Ig-App-Id": "567067343352427",
        "Priority": "u=3",
        "User-Agent": f"Instagram 303.0.0.0.59 Android (28/9; 320dpi; 900x1600; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)",
        "Accept-Language": "ar-SA, en-US",
        "Ig-Intended-User-Id": "0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
    }

    # 1) POST login
    response = s.post(
        'https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/',
        headers=headers, data=data, allow_redirects=True, timeout=20
    )
    body = response.text

    if "Bearer" not in body:
        print("[ ! ] Login failed or challenge")
        print("response.status_code:", response.status_code)
        print("response.text (first 400 chars):", body[:400])
        # طبع هيدرز للمساعدة
        print("\n--- response.headers ---")
        print(response.headers)
        for i, h in enumerate(getattr(response, 'history', [])):
            print(f"\n--- history #{i} headers ---")
            print(h.headers)
        return {}

    # 2) decode sessionid from payload if موجود
    sessionid_from_full = None
    try:
        session_b64 = re.search(r'Bearer IGT:2:(.*?),', response.text).group(1).strip()
        session_b64 = session_b64[:-8]
        full = base64.b64decode(session_b64).decode('utf-8')
        m = re.search(r'"sessionid":"(.*?)"', full)
        if m:
            sessionid_from_full = m.group(1).strip()
    except Exception:
        sessionid_from_full = None

    # 3) اجمع كل Set-Cookie lines من response و history
    responses_to_check = [response] + list(getattr(response, 'history', []))
    set_cookie_lines = collect_all_set_cookie_lines(responses_to_check)

    # 4) جرب نعمل GET لصفحات عامة علشان يجبر السيرفر يرسل بقية الكوكيز
    try:
        r_i = s.get('https://i.instagram.com/', headers=headers, timeout=10, allow_redirects=True)
        responses_to_check.append(r_i)
        for hist in getattr(r_i, 'history', []):
            responses_to_check.append(hist)
    except Exception:
        pass

    try:
        r_www = s.get('https://www.instagram.com/', headers={'User-Agent': headers['User-Agent']}, timeout=10, allow_redirects=True)
        responses_to_check.append(r_www)
        for hist in getattr(r_www, 'history', []):
            responses_to_check.append(hist)
    except Exception:
        pass

    # اجمع كل Set-Cookie بعد الطلبات الاضافية
    set_cookie_lines = collect_all_set_cookie_lines(responses_to_check)

    # 5) اختصر القيم الى dict name->value
    cookie_map = {}
    for line in set_cookie_lines:
        if '=' in line:
            name, val = line.split('=', 1)
            cookie_map[name] = val

    # كمان اخذ من session.cookies كـ fallback
    for k, v in s.cookies.items():
        cookie_map.setdefault(k, v)

    # أعطِ أولوية لـ sessionid المشتق من payload (لو موجود)
    if sessionid_from_full:
        cookie_map['sessionid'] = sessionid_from_full

    # 6) رتب واطبع بالترتيب المطلوب
    ordered_keys = ['csrftoken', 'rur', 'mid', 'ds_user_id', 'sessionid']
    cookie_items = []
    for k in ordered_keys:
        if k in cookie_map and cookie_map[k]:
            cookie_items.append(f"{k}={cookie_map[k]}")
    cookie_string = "; ".join(cookie_items) + (";" if cookie_items else "")

    # طباعة تفصيلية للتصحيح
    print(f"[ + ] Logged in with @{user}")
    print("[ + ] Session is :")
    print(cookie_map.get('sessionid', '(not found)'))
    print("\n--- ALL SET-COOKIE LINES ---")
    for ln in set_cookie_lines:
        print(ln)
    print("\n--- session.cookies (jar) ---")
    print(s.cookies.get_dict())
    print("\n--- FINAL COOKIE STRING ---")
    print(cookie_string)

    return cookie_map

if __name__ == "__main__":
    USER = str(input("[ + ] Username : "))
    PASSW = str(input("[ + ] Password : "))
    login(USER,PASSW)
