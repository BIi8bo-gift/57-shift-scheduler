import requests
import re, sys, time

USERNAME = "BIi8bo-gift"
PASSWORD = "ABCD489abc"
CLIENT_ID = "Iv1.0ff4669b18f4ca00"

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"

# Step 1: Get login page
print("[1] Login page...")
r = session.get("https://github.com/login")
at = re.search(r'authenticity_token".*?value="([^"]+)"', r.text)
if not at:
    at = re.search(r'authenticity_token[^>]*value="([^"]+)"', r.text)
if at:
    token = at.group(1)
    print(f"  Token: {token[:20]}...")
else:
    print("  No token found!")
    sys.exit(1)

# Step 2: Login
print("[2] Login with credentials...")
r = session.post("https://github.com/session", data={
    "login": USERNAME,
    "password": PASSWORD,
    "authenticity_token": token,
    "commit": "Sign in",
}, allow_redirects=False)
print(f"  Status: {r.status_code}, Location: {r.headers.get('Location','')[:80]}")

# Follow redirect
loc = r.headers.get("Location", "")
if loc:
    if loc.startswith("/"):
        loc = "https://github.com" + loc
    print(f"  Following to: {loc[:80]}")
    r = session.get(loc, allow_redirects=True)
    print(f"  After redirect: {r.status_code}, URL: {r.url[:60]}")

# Check login
r2 = session.get("https://github.com")
if USERNAME.lower() in r2.text.lower():
    print("  LOGIN SUCCESSFUL!")
else:
    print("  Login may have issues, continuing...")

# Step 3: Go to device auth page
print(f"[3] Getting device auth page...")
r = session.get("https://github.com/login/device")
print(f"  Status: {r.status_code}")
print(f"  Has device form: {'user_code' in r.text}")

# Step 4: Submit device code
at2 = re.search(r'authenticity_token".*?value="([^"]+)"', r.text)
if at2:
    token2 = at2.group(1)
    print(f"  Device auth token: {token2[:20]}...")
    r = session.post("https://github.com/login/device", data={
        "user_code": "7EE5-26CF",
        "authenticity_token": token2,
    }, allow_redirects=False)
    print(f"  Device submit status: {r.status_code}, Location: {r.headers.get('Location','')[:60]}")
    
    loc2 = r.headers.get("Location", "")
    if loc2:
        if loc2.startswith("/"):
            loc2 = "https://github.com" + loc2
        r = session.get(loc2, allow_redirects=True)
        print(f"  After device submit: {r.status_code}, URL: {r.url[:60]}")
    
    # Step 5: Authorize if needed
    if "authorize" in r.text.lower() or "Authorize" in r.text:
        at3 = re.search(r'authenticity_token".*?value="([^"]+)"', r.text)
        if at3:
            token3 = at3.group(1)
            # Find form action
            fa = re.search(r'<form[^>]*action="([^"]*authorize[^"]*)"', r.text)
            action = fa.group(1) if fa else "/login/oauth/authorize"
            if not action.startswith("http"):
                action = "https://github.com" + action
            print(f"  Authorizing at: {action[:60]}")
            r = session.post(action, data={
                "authenticity_token": token3,
                "authorize": "1",
            }, allow_redirects=False)
            print(f"  Auth result: {r.status_code}, Location: {r.headers.get('Location','')[:60]}")
    
    # Step 6: Check if we can get the gh token now via the callback
    # After authorization, gh should get the token via its server callback
    print("\n[6] Checking gh auth status...")
    import subprocess
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
    print(f"  STDOUT: {result.stdout[:200]}")
    print(f"  STDERR: {result.stderr[:200]}")
    if "Logged in" in result.stdout or "Logged in" in result.stderr:
        print("  GH AUTH SUCCESSFUL!")
    else:
        print("  gh not yet authenticated, waiting 10s for callback...")
        time.sleep(10)
        result2 = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
        print(f"  After wait: {result2.stdout[:200]}{result2.stderr[:200]}")
else:
    print("  No device auth token found")
    # Save response
    with open("debug_device.html", "w", encoding="utf-8") as f:
        f.write(r.text[:5000])

