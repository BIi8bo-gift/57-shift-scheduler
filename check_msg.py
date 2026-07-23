c = open('E:/openclaw-data/workspace/shift-scheduler/index.html', encoding='utf8').read()
print('has msg div:', 'id="msg"' in c)
print('has mx div:', 'id="mx"' in c)
# Find the msg div in the source
import re
for m in re.finditer(r'<div[^>]*id="msg"[^>]*>', c):
    print('Found msg div:', m.group())
