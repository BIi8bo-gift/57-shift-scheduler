"""Rebuild font subset with comprehensive Chinese character coverage."""
import os, sys
from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Build comprehensive character set
chars = set()

# 1. Full GB2312 level 1 common characters (3755 most common Chinese chars)
# Rather than listing them all, use Unicode ranges
# CJK Unified Ideographs block: U+4E00 - U+9FFF (20992 chars)
# But that's too many. Let's cover the most common ones.

# 2. Standard common characters used in Chinese text
# Let me use a practical approach: cover all characters from the common GB2312 set
# that appear in typical Chinese names + labels

# Labels used in the app
labels = "车间排班表日期周期早班人员小夜大休合计导出PDF批次号生产记录姓名工号备注说明操作确认复核审核批准品名规格数量单位温度湿度浓度状态结果开始结束用时序列号版本页码共第页注射用水纯化蒸汽压缩空气氮气氧气不锈钢反应罐层析柱超滤膜包储液袋取样口检查中午值班延迟吃饭强制状态删除添加月份出勤统计清除筛选关闭"
chars.update(labels)

# Numbers and punctuation
chars.update("0123456789.-/:～~，,、。.;；：""''（）()!！?？·…—abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Common characters in dates and counting
chars.update("个十百千万亿年月日时分秒星期零一二三四五六七八九十甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥上下左右前后里外东南西北中大小长短高矮多少新旧好坏快慢轻重")

# Comprehensive surnames (百家姓 extended)
surnames = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴郁胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍郤璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子车颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁晋楚闫法汝鄢涂钦段干百里东郭南门呼延归海羊舌微生岳帅缑亢况后有琴梁丘左丘东门西门商牟佘佴伯赏南宫墨哈谯笪年爱阳佟"
chars.update(surnames)

# Common given name characters (extensive list)
given = "明华军建国庆文平志强刚峰辉磊涛斌杰伟勇秀英玉芳兰桂凤爱妹梅红玲春霞海龙利民东飞超洪雪金鑫国民新华振兴德胜光辉卫大军小云中阿娜香荣莲远天文宇航嘉骏瑞超翰林思远浩宇明哲立学佳琪欣怡思雨慧敏静雯梓豪子涵浩然雨泽宇轩铭洋一鸣俊杰鹏飞世杰庆丰诗涵语嫣可欣梦瑶欣怡浩宇轩泽睿洋家辉俊贤嘉懿睿渊海涛洋波君红生燕琴艳玲霞永军国华建华卫东国强志强秀兰玉芳桂兰凤英爱华美玲建国国庆文平志强永刚永强国平秀珍香玉翠兰桂荣凤莲梅芳"
chars.update(given)

# Add specific characters from the actual data
data_chars = "毛志琛张峰崔国干林新燕王征征常远王晓龙李振孙文斌学灵朱庆强"
chars.update(data_chars)

# Convert to sorted string
text = "".join(sorted(chars))
print(f"Total unique characters: {len(chars)}")

# Check which characters are missing from the current subset
existing_cmap = None
existing_path = os.path.join(fonts_dir, "NotoSansSC-Regular-subset.ttf")
if os.path.exists(existing_path):
    existing_font = TTFont(existing_path)
    existing_cmap = existing_font.getBestCmap()
    existing_font.close()

if existing_cmap:
    missing = [c for c in chars if ord(c) not in existing_cmap]
    if missing:
        print(f"New characters to add: {len(missing)} (e.g. {''.join(missing[:20])})")
    else:
        print("All characters already covered in existing subset!")

# Rebuild the subset fonts
for input_name, output_name in [
    ("NotoSansSC-Regular.ttf", "NotoSansSC-Regular.ttf"),
    ("NotoSansSC-Bold.ttf", "NotoSansSC-Bold.ttf"),
]:
    input_path = os.path.join(fonts_dir, input_name)
    output_path = os.path.join(fonts_dir, output_name.replace(".ttf", "-subset.ttf"))
    
    if not os.path.exists(input_path):
        print(f"SKIP {input_name}: not found (need to download)")
        continue
    
    print(f"\nProcessing {input_name}...")
    orig_size = os.path.getsize(input_path)
    
    opts = Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    
    subsetter = Subsetter(options=opts)
    subsetter.populate(text=text)
    
    font = TTFont(input_path)
    subsetter.subset(font)
    font.save(output_path)
    new_size = os.path.getsize(output_path)
    font.close()
    
    print(f"  {orig_size} -> {new_size} bytes ({new_size*100//orig_size}%)")
    
    # Validate
    font2 = TTFont(output_path)
    cmap = font2.getBestCmap()
    missing = [c for c in chars if ord(c) not in cmap]
    font2.close()
    
    if missing:
        print(f"  WARNING: {len(missing)} missing chars!")
    else:
        print(f"  All {len(chars)} chars present ✓")

print("\nDone!")
