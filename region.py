import socket
import urllib.request
from bs4 import BeautifulSoup

'''
爬取统计局全国信息

authon:wangjiaming
'''
def getSoup(url, code):
    # 请求
    try:
        # 设置超时时间2秒，2秒内返不回直接重调用当前这个url，简单粗暴的做法
        # 正常情况不到100毫秒返回的。超过2秒的不正常
        timeout = 2
        socket.setdefaulttimeout(timeout)

        request = urllib.request.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
        # 爬取结果
        response = urllib.request.urlopen(request)

        data = response.read()
        # 设置解码方式
        data = data.decode(code)
        # print(data)
        soup = BeautifulSoup(data, 'html.parser')
    except BaseException as err:
        print(err)
        print('重试：' + url)
        soup = getSoup(url, 'gbk')
    return soup


def main():
    soup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html",'gbk');
    getProvince(soup)


# 省
def getProvince(soup):
    _index = 427699
    loopIndex = 0
    _topHtml = soup.find_all(attrs={'class': 'provincetr'})
    while loopIndex < len(_topHtml) - 1:
        for tag in _topHtml[loopIndex].select('a'):
            if (tag.get_text() != '北京市' and tag.get_text() != '天津市' and tag.get_text() != '河北省' and tag.get_text() != '山西省' and tag.get_text() != '内蒙古自治区' and tag.get_text() != '辽宁省' and tag.get_text() != '吉林省' and tag.get_text() != '黑龙江省' and tag.get_text() != '上海市' and tag.get_text() != '江苏省' and tag.get_text() != '浙江省' and tag.get_text() != '安徽省' and tag.get_text() != '福建省' and tag.get_text() != '江西省' and tag.get_text() != '山东省' and tag.get_text() != '河南省' and tag.get_text() != '湖北省' and tag.get_text() != '湖南省' and tag.get_text() != '广东省' and tag.get_text() != '广西壮族自治区' and tag.get_text() != '海南省' and tag.get_text() != '重庆市'):
                printInsertSql(_index, str(tag['href']).split('.')[0] + "0000000000", "", 1, tag.get_text(), "", "", "",
                               "")
                _index = getCity(_index, str(tag['href']).split('.')[0] + "0000000000", tag.get_text(), tag['href']);
        loopIndex = loopIndex + 1


# 市
def getCity(index, provinceCode, provinceName, href):
    _index = index
    _citySoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href,'gbk');
    _cityHtml = _citySoup.find_all(attrs={'class': 'citytr'})
    loopIndex = 0
    while loopIndex < len(_cityHtml):
        _index = _index + 1;
        printInsertSql(_index, _cityHtml[loopIndex].select('a')[0].get_text(), provinceCode, 2, provinceName,
                       _cityHtml[loopIndex].select('a')[1].get_text(), "", "", "")
        _index = getDistrict(_index, provinceCode, provinceName, _cityHtml[loopIndex].select('a')[0].get_text(),
                             _cityHtml[loopIndex].select('a')[1].get_text(),
                             _cityHtml[loopIndex].select('a')[1]['href'])
        loopIndex = loopIndex + 1
    return _index


# 区
def getDistrict(index, provinceCode, provinceName, cityCode, cityName, href):
    _index = index
    _districtSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href,'gbk');
    _districtHtml = _districtSoup.find_all(attrs={'class': 'countytr'})
    loopIndex = 0
    while loopIndex < len(_districtHtml):
        _index = _index + 1
        _districtCode = ""
        _districtName = ""
        _href = ""
        try:
            _districtCode = _districtHtml[loopIndex].select('a')[0].get_text()
            _districtName = _districtHtml[loopIndex].select('a')[1].get_text()
            _href = str(href.split('/')[0] + "/" + _districtHtml[loopIndex].select('a')[0]['href'])
        except BaseException:
            _districtCode = _districtHtml[loopIndex].select('td')[0].get_text()
            _districtName = _districtHtml[loopIndex].select('td')[1].get_text()
        printInsertSql(_index, _districtCode, cityCode, 3, provinceName, cityName, _districtName, "", "")
        if (_href != ""):
            _index = getTown(_index, provinceCode, provinceName, cityCode, cityName, _districtCode, _districtName,
                             _href)
        loopIndex = loopIndex + 1
    return _index


# 街道
def getTown(index, provinceCode, provinceName, cityCode, cityName, districtCode, districtName, href):
    _index = index
    _townSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href,'gbk');
    _townHtml = _townSoup.find_all(attrs={'class': 'towntr'})
    loopIndex = 0
    while loopIndex < len(_townHtml):
        _index = _index + 1
        _townCode = _townHtml[loopIndex].select('a')[0].get_text()
        _townName = _townHtml[loopIndex].select('a')[1].get_text()
        printInsertSql(_index, _townCode, districtCode, 4, provinceName, cityName, districtName, _townName, "")
        _href = str(href.split("/")[0] + "/" + href.split("/")[1] + "/" + _townHtml[loopIndex].select('a')[0]['href'])
        _index = getVillage(_index, provinceCode, provinceName, cityCode, cityName, districtCode, districtName,
                            _townCode, _townName, _href)
        loopIndex = loopIndex + 1
    return _index


# 居委会
def getVillage(index, provinceCode, provinceName, cityCode, cityName, districtCode, districtName, townCode, townName,
               href):
    _index = index

    if ("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href == 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/42/06/84/420684103.html' or "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href =="http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/51/06/81/510681114.html"):
        _villageSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href, 'gb18030')
    else:
        _villageSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href, 'gbk')

    # _villageSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href);
    _villageHtml = _villageSoup.find_all(attrs={'class': 'villagetr'})
    loopIndex = 0
    while loopIndex < len(_villageHtml):
        _index = _index + 1
        _villageCode = _villageHtml[loopIndex].select('td')[0].get_text()
        _villageName = _villageHtml[loopIndex].select('td')[2].get_text()
        printInsertSql(_index, _villageCode, townCode, 5, provinceName, cityName, districtName, townName, _villageName)
        loopIndex = loopIndex + 1
    return _index


def printInsertSql(id, code, parent_code, level_grade, province, city, district, street, neighborhood_committee):
    _id = str(id)
    _code = str(code)
    _parent_code = str(parent_code)
    _level_grade = str(level_grade)
    _province = str(province)
    _city = str(city)
    _district = str(district)
    _street = str(street)
    _neighborhood_committee = str(neighborhood_committee)
    _short_name = ""
    if (level_grade == 1):
        _short_name = _province
    elif (level_grade == 2):
        _short_name = _city
    elif (level_grade == 3):
        _short_name = _district
    elif (level_grade == 4):
        _short_name = _street
    elif (level_grade == 5):
        _short_name = _neighborhood_committee
    _all_address = _province + _city + _district + _street + _neighborhood_committee
    file = openFile()
    file.writelines(
        "insert into RHIN_SYS.TB_DI_CHINA(\"id\",\"code\",\"parent_code\",\"level_grade\",\"short_name\",\"name\") values(\"" + _id + "\",\"" + _code + "\",\"" + _parent_code + "\",\"" + _level_grade + "\",\"" + _short_name + "\",\"" + _all_address + "\");" + '\n')
    file.close()
    print(str(_province + "|" + _city + "|" + _district + "|" + _street + "|" + _neighborhood_committee))


def openFile():
    file = open(r"/Users/wangjiaming/region.sql", "a")
    return file


main()
