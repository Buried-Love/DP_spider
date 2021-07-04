from bs4 import BeautifulSoup
import re
from fontTools.ttLib import TTFont
import requests


woff_string = '''
1234567890店中美家馆
小车大市公酒行国品发电金心业商司
超生装园场食有新限天面工服海华水
房饰城乐汽香部利子老艺花专东肉菜
学福饭人百餐茶务通味所山区门药银
农龙停尚安广鑫一容动南具源兴鲜记
时机烤文康信果阳理锅宝达地儿衣特
产西批坊州牛佳化五米修爱北养卖建
材三会鸡室红站德王光名丽油院堂烧
江社合星货型村自科快便日民营和活
童明器烟育宾精屋经居庄石顺林尔县
手厅销用好客火雅盛体旅之鞋辣作粉
包楼校鱼平彩上吧保永万物教吃设医
正造丰健点汤网庆技斯洗料配汇木缘
加麻联卫川泰色世方寓风幼羊烫来高
厂兰阿贝皮全女拉成云维贸道术运都
口博河瑞宏京际路祥青镇厨培力惠连
马鸿钢训影甲助窗布富牌头四多妆吉
苑沙恒隆春干饼氏里二管诚制售嘉长
轩杂副清计黄讯太鸭号街交与叉附近
层旁对巷栋环省桥湖段乡厦府铺内侧
元购前幢滨处向座下臬凤港开关景泉
塘放昌线湾政步宁解白田町溪十八古
双胜本单同九迎第台玉锦底后七斜期
武岭松角纪朝峰六振珠局岗洲横边济
井办汉代临弄团外塔杨铁浦字年岛陵
原梅进荣友虹央桂沿事津凯莲丁秀柳
集紫旗张谷的是不了很还个也这我就
在以可到错没去过感次要比觉看得说
常真们但最喜哈么别位能较境非为欢
然他挺着价那意种想出员两推做排实
分间甜度起满给热完格荐喝等其再几
只现朋候样直而买于般豆量选奶打每
评少算又因情找些份置适什蛋师气你
姐棒试总定啊足级整带虾如态且尝主
话强当更板知己无酸让入啦式笑赞片
酱差像提队走嫩才刚午接重串回晚微
周值费性桌拍跟块调糕'''

woffs = [i for i in woff_string if i != '\n' and i != ' ']


def woff_change(wofflist, TTG, woffdict):
    woff_content = ''
    for char in wofflist:
        text = str(char.encode('raw_unicode_escape').replace(b'\\u', b'uni'), 'utf-8')
        if text in TTG:
            content = woffs[woffdict[str(char.encode('raw_unicode_escape').replace(b'\\u', b'uni'), 'utf-8')]]
        else:
            content = char
        woff_content += ''.join(content)
    return woff_content


# def read_html(filepath):
#     with client.read(filepath, encoding='utf-8') as reader:
#         respon = reader.read()
#     soup = BeautifulSoup(respon, 'lxml')
#     return soup
# address

def get_adress(soup, address_TTGlyphs, address_dict):
    pattern = re.compile('>(.*?)<')
    adress = pattern.findall(str(soup.find_all('span', id='address')[0]))
    location = woff_change(adress, address_TTGlyphs, address_dict)
    return location


def get_telphonenumber(soup, number_TTGlyphs, number_dict):
    tell_number = ''
    try:
        pattern = re.compile('>(.*?)<')
        tell_number = pattern.findall(str(soup.find_all('p', class_='expand-info tel')[0]))
        tell_number = woff_change(tell_number, number_TTGlyphs, number_dict)
        return tell_number
    except:
        return tell_number


def get_svg_url(soup):
    svgtextcss = re.search(r'href="([^"]+svgtextcss[^"]+)"', str(soup), re.M)
    woff_url = 'http:' + svgtextcss.group(1)
    return woff_url


def get_address_woff(woff_url):
    global address_url
    svg_html = requests.get(woff_url).text
    lines = svg_html.split('PingFangSC-')
    partern = re.compile(r',(url.*address)')
    for line in lines:
        out = partern.findall(line)
        if len(out) > 0:
            woff = re.compile('\((.*?)\)')
            address_url = 'http:' + woff.findall(out[0])[0].replace('"', '')
            print(address_url)
    with open('font/address.woff', 'wb') as writer:
        writer.write(requests.get(address_url).content)
    return None


def get_number_woff(woff_url):
    global number_url
    svg_html = requests.get(woff_url).text
    lines = svg_html.split('PingFangSC')
    partern = re.compile(r',(url.*num)')
    for line in lines:
        out = partern.findall(line)
        if len(out) > 0:
            woff = re.compile('\((.*?)\)')
            number_url = 'http:' + woff.findall(out[0])[0].replace('"', '')
    with open('font/number.woff', 'wb') as writer:
        writer.write(requests.get(number_url).content)
    return None


with open('店铺.html', 'r', encoding='utf-8') as f:
    respon = f.read()
    soup = BeautifulSoup(respon, 'lxml')
woff_url = get_svg_url(soup)
get_address_woff(woff_url)
get_number_woff(woff_url)
addressfont = TTFont('font/address.woff')
addressfont.saveXML('font/address.xml')
numberfont = TTFont('font/number.woff')
numberfont.saveXML('font/number.xml')
address_TTGlyphs = addressfont['cmap'].tables[0].ttFont.getGlyphOrder()[2:]
number_TTGlyphs = numberfont['cmap'].tables[0].ttFont.getGlyphOrder()[2:]
address_dict = {}
for i, x in enumerate(address_TTGlyphs):
    address_dict[x] = i
address = get_adress(soup, address_TTGlyphs, address_dict)
print(address)
number_dict = {}
for i, x in enumerate(number_TTGlyphs):
    number_dict[x] = i
tell_number = get_telphonenumber(soup, number_TTGlyphs, number_dict)
if len(tell_number) != 0:
    phone_number = tell_number
else:
    phone_number = ''
print(phone_number)
