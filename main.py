import requests, uuid, string, random, re, base64, urllib.parse
from http import cookies as http_cookies

my_uuid = uuid.uuid4()
my_uuid_str = str(my_uuid)
modified_uuid_str = my_uuid_str[:8] + "should_trigger_override_login_success_action" + my_uuid_str[8:]
rd = ''.join(random.choices(string.ascii_lowercase+string.digits, k=16))

def _parse_set_cookie_headers(resp):
    """
    يرجع dict من اسم_الكوكي -> قيمة، يحاول يقرأ كل هيدر Set-Cookie إن وُجدت (متعددة أو مجمعة)
    """
    cookie_map = {}
    # اجمع كل قيم Set-Cookie (قد تكون عدة رؤوس)
    set_cookie_values = []
    for k, v in resp.headers.items():
        if k.lower() == 'set-cookie':
            set_cookie_values.append(v)
    # لو ما كانت هناك رؤوس متعددة، خذ القيمة المفردة (قد تكون مجمعة)
    if not set_cookie_values:
        single = resp.headers.get('Set-Cookie')
        if single:
            set_cookie_values = [single]

    for val in set_cookie_values:
        try:
            sc = http_cookies.SimpleCookie()
            sc.load(val)
            for key in sc:
                cookie_map[key] = sc[key].value
        except Exception:
            # كـ fallback، حاول ريجيكس بسيط
            for m in re.finditer(r'([^=;\s]+)=([^;,\s]+)', val):
                cookie_map[m.group(1)] = m.group(2)
    return cookie_map

def login(user,password):
    data = {"params": "{\"client_input_params\":{\"contact_point\":\"" + user + "\",\"password\":\"#PWD_INSTAGRAM:0:0:" +  password + "\",\"fb_ig_device_id\":[],\"event_flow\":\"login_manual\",\"openid_tokens\":{},\"machine_id\":\"ZG93WAABAAEkJZWHLdW_Dm4nIE9C\",\"family_device_id\":\"\",\"accounts_list\":[],\"try_num\":1,\"login_attempt_count\":1,\"device_id\":\"android-" + rd + "\",\"auth_secure_device_id\":\"\",\"device_emails\":[],\"secure_family_device_id\":\"\",\"event_step\":\"home_page\"},\"server_params\":{\"is_platform_login\":0,\"qe_device_id\":\"\",\"family_device_id\":\"\",\"credential_type\":\"password\",\"waterfall_id\":\"" + modified_uuid_str + "\",\"username_text_input_id\":\"9cze54:46\",\"password_text_input_id\":\"9cze54:47\",\"offline_experiment_group\":\"caa_launch_ig4a_combined_60_percent\",\"INTERNAL__latency_qpl_instance_id\":56600226400306,\"INTERNAL_INFRA_THEME\":\"default\",\"device_id\":\"android-" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=16)) + "\",\"server_login_source\":\"login\",\"login_source\":\"Login\",\"should_trigger_override_login_success_action\":0,\"ar_event_source\":\"login_home_page\",\"INTERNAL__latency_qpl_marker_id\":36707139}}"}
    data["params"] = data["params"].replace("\"family_device_id\":\"\"", "\"family_device_id\":\"" +my_uuid_str + "\"")
    data["params"] = data["params"].replace("\"qe_device_id\":\"\"", "\"qe_device_id\":\"" + my_uuid_str + "\"")
    headers = {"Host": "i.instagram.com","X-Ig-App-Locale": "ar_SA","X-Ig-Device-Locale": "ar_SA","X-Ig-Mapped-Locale": "ar_AR","X-Pigeon-Session-Id": f"UFS-{uuid.uuid4()}-0","X-Pigeon-Rawclienttime": "1685026670.130","X-Ig-Bandwidth-Speed-Kbps": "-1.000","X-Ig-Bandwidth-Totalbytes-B": "0","X-Ig-Bandwidth-Totaltime-Ms": "0","X-Bloks-Version-Id": "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb","X-Ig-Www-Claim": "0","X-Bloks-Is-Layout-Rtl": "true","X-Ig-Device-Id": f"{uuid.uuid4()}","X-Ig-Family-Device-Id": f"{uuid.uuid4()}","X-Ig-Android-Id": f"android-{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}","X-Ig-Timezone-Offset": "10800","X-Fb-Connection-Type": "WIFI","X-Ig-Connection-Type": "WIFI","X-Ig-Capabilities": "3brTv10=","X-Ig-App-Id": "567067343352427","Priority": "u=3","User-Agent": f"Instagram 303.0.0.0.59 Android (28/9; 320dpi; 900x1600; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)","Accept-Language": "ar-SA, en-US","Ig-Intended-User-Id": "0","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","Content-Length": "1957","Accept-Encoding": "gzip, deflate","X-Fb-Http-Engine": "Liger","X-Fb-Client-Ip": "True","X-Fb-Server-Cluster": "True"}
    response = requests.post('https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/',headers=headers ,data=data)
    body = response.text

    if "Bearer" in body:
        # decode payload for sessionid (إذا موجود داخل الـ payload)
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

        # اقرأ الكوكيز من هيدرز Set-Cookie بقوة أكثر
        parsed_from_headers = _parse_set_cookie_headers(response)

        # وكمّل باقي القيم من response.cookies كـ fallback
        cookies_obj = response.cookies
        cookie_map = {}
        # fill from headers first (preferred)
        cookie_map.update(parsed_from_headers)
        # then fallback to response.cookies if أي مفتاح ناقص
        for k in ['csrftoken','rur','mid','ds_user_id','sessionid']:
            if k not in cookie_map and cookies_obj.get(k):
                cookie_map[k] = cookies_obj.get(k)

        # إذا لقينا sessionid في الـ payload فخليه أولوية
        if sessionid_from_full:
            cookie_map['sessionid'] = sessionid_from_full

        # ابني سترينغ بالترتيب اللي طلبت
        ordered_keys = ['csrftoken','rur','mid','ds_user_id','sessionid']
        cookie_items = []
        for k in ordered_keys:
            if k in cookie_map and cookie_map[k] is not None:
                cookie_items.append(f"{k}={cookie_map[k]}")
        cookie_string = "; ".join(cookie_items) + ("; " if cookie_items else "")

        print(f"[ + ] Logged in with @{user}")
        print("[ + ] Session is : ")
        print(cookie_map.get('sessionid', '(not found)'))
        print("\n[ + ] Cookies string:")
        print(cookie_string)
        input()
        exit()

    elif "The password you entered is incorrect" in body or "Please check your username and try again." in body or "inactive user" in body or "should_dismiss_loading\", \"has_identification_error\"" in body:
        print("[ - ] Bad Passowrd")
        input()
        exit()
    elif "challenge_required" in body or "two_step_verification" in body:
        print("[ ! ] Challenge requierd acccept and click enter ")
        input()
        login(user,password)
    else:
        print("[ ! ] Something wrong ")
        # لو تبا تشوف كل هيدرز للتحقيق: print(response.headers)
        input()
        exit()

if __name__ == "__main__":
    USER = str(input("[ + ] Username : "))
    PASSW = str(input("[ + ] Password : "))
    login(USER,PASSW)
