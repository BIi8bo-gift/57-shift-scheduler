import requests, re, json, sys, os

USERNAME = "BIi8bo-gift"
PASSWORD = "ABCD489abc"

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"

# Login
print("[1] Login...")
r = s.get("https://github.com/login")
at = re.search(r'authenticity_token[^>]*value="([^"]+)"', r.text)
if not at:
    at = re.search(r'authenticity_token[^>]*value="([^"]+)"', r.text)
t = at.group(1)
r = s.post("https://github.com/session", data={
    "login": USERNAME, "password": PASSWORD, "authenticity_token": t, "commit": "Sign in"
}, allow_redirects=True)
print(f"  Status: {r.status_code}, URL: {r.url[:60]}")

# Check login
r2 = s.get("https://github.com")
logged_in = USERNAME.lower() in r2.text.lower() or "sign out" in r2.text.lower()
print(f"  Logged in: {logged_in}")

# Try API
r_api = s.get("https://api.github.com/user", headers={"Accept": "application/vnd.github.v3+json"})
print(f"  API /user: {r_api.status_code}")
if r_api.status_code == 200:
    print(f"  User: {r_api.json().get('login')}")

# If API works, create repo via API
if r_api.status_code == 200:
    print("\n[2] Creating repo via API...")
    payload = {
        "name": "57-shift-scheduler",
        "description": "Workshop 57 shift scheduler",
        "private": False,
        "auto_init": False
    }
    r_create = s.post("https://api.github.com/user/repos",
                      json=payload,
                      headers={"Accept": "application/vnd.github.v3+json"})
    print(f"  Create result: {r_create.status_code}")
    if r_create.status_code == 201:
        data = r_create.json()
        print(f"  Repo created: {data.get('clone_url')}")
        print(f"  SSH URL: {data.get('ssh_url')}")
    else:
        print(f"  Error: {r_create.text[:200]}")
else:
    print("\n[2] Trying web form approach...")
    r_new = s.get("https://github.com/new")
    print(f"  New repo page: {r_new.status_code}")
    at2 = re.search(r'authenticity_token[^>]*value="([^"]+)"', r_new.text)
    if at2:
        t2 = at2.group(1)
        r_create = s.post("https://github.com/repositories", data={
            "authenticity_token": t2,
            "repository[name]": "57-shift-scheduler",
            "repository[description]": "Workshop 57 shift scheduler",
            "repository[visibility]": "public",
            "repository[auto_init]": "1",
        }, allow_redirects=False)
        print(f"  Create result: {r_create.status_code}")
        if r_create.status_code == 302:
            loc = r_create.headers.get("Location", "")
            print(f"  Redirect to: {loc[:80]}")
            if "57-shift-scheduler" in loc:
                print("  REPO CREATED VIA WEB FORM!")
