import urllib.request
r = urllib.request.urlopen('http://127.0.0.1:8082/', timeout=5)
h = r.read().decode('utf-8')
checks = [
    ('date input id=d', 'id="d"' in h),
    ('date input id=d2', 'id="d2"' in h),
    ('btnAdd onclick', 'onclick="addRow()"' in h),
    ('monthSel select', 'id="monthSel"' in h),
    ('personFilter select', 'id="personFilter"' in h),
    ('msg div', 'id="msg"' in h),
    ('tb tbody', 'id="tb"' in h),
    ('st span', 'id="st"' in h),
    ('$ function definition', 'function $(id)' in h),
]
for name, ok in checks:
    print(f'  {"OK" if ok else "PROBLEM"} {name}')
