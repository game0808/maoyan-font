import re
import io
import json
import requests
import numpy as np
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent

# 结果保存路径
fileName = 'D:/code/Pro/maoyan-font/maoyan.json'

# 预先处理旧字体文件
base_font_d = {
    'uniE90B': '0',
    'uniF8B1': '1',
    'uniE72D': '2',
    'uniE79F': '3',
    'uniF301': '4',
    'uniF015': '5',
    'uniEB31': '6',
    'uniEEA5': '7',
    'uniF27E': '8',
    'uniF75B': '9',
}


def getAxis(font):
    # 获取字体坐标
    uni_list = font.getGlyphOrder()[2:]
    font_axis = []
    for uni in uni_list:
        axis = []
        for i in font['glyf'][uni].coordinates:
            axis.append(i)
        font_axis.append(axis)
    return font_axis


def EucliDist(axis1, axis2):
    # 欧式距离计算
    if len(axis1) < len(axis2):
        axis1.extend([0, 0] for _ in range(len(axis2) - len(axis1)))
    elif len(axis2) < len(axis1):
        axis2.extend([0, 0] for _ in range(len(axis1) - len(axis2)))
    axis1 = np.array(axis1)
    axis2 = np.array(axis2)
    return np.sqrt(np.sum(np.square(axis1-axis2)))


# 获取旧字体文件
base_font = TTFont('D:/code/Pro/maoyan-font/maoyan.woff')
# base_font.saveXML('maoyan.xml')
uni_base_list = base_font.getGlyphOrder()[2:]
base_axis = getAxis(base_font)


def get_new_font():
    # 获取新字体文件
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }
    url = 'http://piaofang.maoyan.com/dashboard-ajax'
    response = requests.get(url=url, headers=headers).json()
    with open(fileName, 'w', encoding='utf-8') as fp:
        json.dump(response, fp=fp, ensure_ascii=False)
    font_style = response['fontStyle']
    font_url = 'http:' + re.search(r',url\("(.*\.woff)', font_style).group(1)
    font_response = requests.get(url=font_url, headers=headers).content
    new_font = TTFont(io.BytesIO(font_response))
    return new_font


def parse_new_font():
    # 解析对比新旧字体文件
    new_font = get_new_font()
    uni_list = new_font.getGlyphOrder()[2:]
    cur_axis = getAxis(new_font)
    new_font_dict = {}
    for i in range(len(uni_list)):
        min_avg = 99999
        uni = None
        for j in range(len(uni_base_list)):
            avg = EucliDist(cur_axis[i], base_axis[j])
            if avg < min_avg:
                min_avg = avg
                uni = uni_base_list[j]
        new_font_dict['&#x' + uni_list[i][3:].lower() + ';'] = base_font_d[uni]
    return new_font_dict


def replace_num():
    # 替换数字文本
    new_font_dict = parse_new_font()
    fp = open(fileName, 'r', encoding='utf-8')
    data = json.load(fp)
    data = json.dumps(data)
    for uni, number in new_font_dict.items():
        try:
            data = re.sub(uni, number, data)
        except:
            print('ERROR!')
    fp = open(fileName, 'w', encoding='utf-8')
    data = json.loads(data)
    json.dump(data, fp=fp, ensure_ascii=False)


if __name__ == "__main__":
    replace_num()
    print('OK!')
