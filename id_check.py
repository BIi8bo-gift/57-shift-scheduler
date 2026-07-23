c = open('E:/openclaw-data/workspace/shift-scheduler/index.html', encoding='utf8').read()
# Collect all getElementById references in JS
import re
js_ids = set(re.findall(r"getElementById\(['\"](\w+)['\"]", c))
html_ids = set(re.findall(r'id="(\w+)"', c))
print('JS references:', sorted(js_ids))
print('HTML defines:', sorted(html_ids))
print('Missing in HTML:', sorted(js_ids - html_ids))
print('Extra in HTML:', sorted(html_ids - js_ids))
