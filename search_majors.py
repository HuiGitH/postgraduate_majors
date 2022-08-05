# 作者：程序员石磊
# 链接：https://zhuanlan.zhihu.com/p/388709541
# 来源：知乎
# 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

import json
import re
import collections

import requests
from bs4 import BeautifulSoup


# pip install beautifulsoup4
# pip install  requests


def getProfession(url):
    profession_html = requests.post(' https://yz.chsi.com.cn' + url)
    profession_html.encoding = 'utf-8'
    profession_soup = BeautifulSoup(profession_html.text, 'html.parser')
    trs = profession_soup.select(".more-content tr")
    colIndex = [0]
    profession_result = ''
    for trItem in trs:
        for index, tdItem in enumerate(trItem.select("td")):
            if index in colIndex:
                continue
            if index == 5:
                if len(tdItem.select("span")) > 0:
                    profession_result += ' | ' + tdItem.select("span")[0].string if tdItem.select("span")[
                        0].string else ' | ' + '无'
                else:
                    profession_result += ' | ' + '无'
            if index == 6:
                item = re.findall(r"document.write\(cutString\('(.*)',6\)\)", tdItem.select('script')[0].string.strip())
                profession_result += item[0] if len(item[0]) > 2 else '无'
                continue
            if index == 7:
                profession_result += '| ' + '[详情](https://yz.chsi.com.cn' + tdItem.select('a')[0].attrs['href'] + ')'
                continue
            if index == 8:
                item = re.findall(r"document.write\(cutString\('(.*)',6\)\)", tdItem.select('script')[0].string.strip())
                profession_result += '| ' + item[0] if len(item[0]) > 2 else '| ' + '无'
                profession_result += ' |\n'
                continue
            value = tdItem.string if tdItem.string is not None else ' '
            profession_result += ' | ' + value
    return profession_result


def getSchool(ssdm, province_name, result_dict):
    subject_kinds = requests.post('https://yz.chsi.com.cn/zsml/pages/getZy.jsp')
    kinds = json.loads(subject_kinds.text)
    fei_quan = 2  # 1 代表全日制 2 代表非全日制

    for kind in kinds:
        # 工学学科分类
        if re.match(r'085\d+', kind['dm']):
            # ssdm 省市代码 yjxkdm 学科代码  zymc 专业名称 xxfs 学习方式
            param = {'ssdm': ssdm, 'yjxkdm': kind['dm'], 'xxfs': fei_quan}
            r = requests.post('https://yz.chsi.com.cn/zsml/queryAction.do', params=param)
            r.encoding = 'utf-8'
            print(province_name, kind['mc'], '全日制' if fei_quan == 1 else '非全日制', param, r.url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.select(".ch-table a"):
                print(province_name, item.string)
                result_dict[province_name][item.string] = result_dict[province_name].get(
                    item.string, '') + getProfession(item.attrs['href'])
                fo = open("majors.md", "w")
                result_dict = dict(sorted(result_dict.items()))

                for pr_name, schs in result_dict.items():
                    fo.writelines('# ' + pr_name + '\n')
                    schs = dict(sorted(schs.items()))
                    for shchool_name, cu_item in schs.items():
                        head = '## ' + shchool_name + '\n'
                        head += '| 院系所   |  专业  |  研究方向  |  学习方式  |  指导老师  |  拟招生人数  |  考试范围、详情  |  备注  |  \n'
                        head += '| - | - | - | - |  - | - | - |  - |   \n'
                        fo.writelines(head)
                        fo.writelines(cu_item)
                fo.close()
    return result_dict


def main():
    cities = requests.post('https://yz.chsi.com.cn/zsml/pages/getSs.jsp').text
    # cities = '[{"mc": "重庆市","dm": "50"},{"mc": "四川省","dm": "51"}]'
    result_dict = collections.defaultdict(dict)
    for city in json.loads(cities):
        print(city['dm'], city.get('mc'))
        result_dict.update(getSchool(city['dm'], city.get('mc'), result_dict))


if __name__ == "__main__":
    main()
