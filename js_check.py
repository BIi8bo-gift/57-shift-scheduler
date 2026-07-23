c = open('E:/openclaw-data/workspace/shift-scheduler/index.html', encoding='utf8').read()
marker = "'use strict'"
i = c.find(marker)
i2 = c.find('</script>', i)
js = c[i:i2]
opens = js.count('{')
closes = js.count('}')
opens_p = js.count('(')
closes_p = js.count(')')
opens_b = js.count('[')
closes_b = js.count(']')
print(f'Braces: open={opens} close={closes} diff={opens-closes}')
print(f'Parens: open={opens_p} close={closes_p} diff={opens_p-closes_p}')
print(f'Brackets: open={opens_b} close={closes_b} diff={opens_b-closes_b}')
