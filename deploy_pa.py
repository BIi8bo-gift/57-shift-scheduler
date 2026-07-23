"""Create a PythonAnywhere account and deploy the Flask app"""
import requests, re, json, os, sys
from urllib.parse import parse_qs

USERNAME = "bi8bo"
EMAIL = "1356484338@qq.com"
PASSWORD = "***"

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"

# Step 1: Get signup page
print("[1] Getting signup page...")
r = s.get("https://www.pythonanywhere.com/registration/register/beginner/")
at = re.search(r'authenticity_token[^>]*value="([^"]+)"', r.text)
if at:
    token = at.group(1)
    print(f"  Got token: {token[:20]}...")
else:
    print("  No token found")
    sys.exit(1)

# Step 2: Sign up
print("[2] Signing up...")
r = s.post("https://www.pythonanywhere.com/registration/register/beginner/", data={
    "authenticity_token": token,
    "user[username]": USERNAME,
    "user[password]": PASSWORD,
    "user[password_confirmation]": PASSWORD,
    "user[email]": EMAIL,
    "commit": "Create account"
}, allow_redirects=True)
print(f"  Status: {r.status_code}")
print(f"  URL: {r.url}")
if "tier" in r.url or "welcome" in r.url or "dashboard" in r.url:
    print("  SIGNUP SUCCESSFUL!")
else:
    if "error" in r.text.lower() or "already" in r.text.lower():
        print("  Account might already exist")
    print(f"  Page: {r.url[:60]}")
    with open("pa_signup_debug.html", "w", encoding="utf-8") as f:
        f.write(r.text[:10000])
    print("  Saved debug page")
