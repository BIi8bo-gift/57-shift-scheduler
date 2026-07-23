c = open('E:/openclaw-data/workspace/shift-scheduler/index.html', encoding='utf8').read()
import re
# Find all $(...) calls with string literals
dollar_calls = set(re.findall(r"\$\(['\"](\w+)['\"]\)", c))
html_ids = set(re.findall(r'id="(\w+)"', c))
print('$() calls:', sorted(dollar_calls))
print('Missing:', sorted(dollar_calls - html_ids))
