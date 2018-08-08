import urllib.request
from bs4 import BeautifulSoup
import time

#
# 爬取 统计局全国信息
# authon:wangjiaming
#

def getSoup(url):
    time.sleep(1)
    # 请求
    request = urllib.request.Request(url)
    request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36' )
    # 爬取结果
    response = urllib.request.urlopen(request)
    data = response.read()

    # 设置解码方式
    data = data.decode('gbk')
    # print(data)
    soup = BeautifulSoup(data, 'html.parser')
    return soup


def main():
    soup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html");
    file=openFile()
    getProvince(soup,file)
    file.close();


# 省
def getProvince(soup,file):
    _index = 0
    loopIndex = 0
    _topHtml = soup.find_all(attrs={'class': 'provincetr'})
    while loopIndex < len(_topHtml) - 1:
        for tag in _topHtml[loopIndex].select('a'):
            printInsertSql(_index, str(tag['href']).split('.')[0] + "0000000000", "", 1, tag.get_text(), "", "", "","",file)
            _index = getCity(_index, str(tag['href']).split('.')[0] + "0000000000", tag.get_text(), tag['href'],file);
        loopIndex = loopIndex + 1


# 市
def getCity(index, provinceCode, provinceName, href,file):
    _index = index
    _citySoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href);
    _cityHtml = _citySoup.find_all(attrs={'class': 'citytr'})
    loopIndex = 0
    while loopIndex < len(_cityHtml):
        _index = _index + 1;
        printInsertSql(_index, _cityHtml[loopIndex].select('a')[0].get_text(), provinceCode, 2, provinceName,_cityHtml[loopIndex].select('a')[1].get_text(), "", "", "",file)
        _index = getDistrict(_index, provinceCode, provinceName, _cityHtml[loopIndex].select('a')[0].get_text(),_cityHtml[loopIndex].select('a')[1].get_text(),_cityHtml[loopIndex].select('a')[1]['href'],file)
        loopIndex = loopIndex + 1
    return _index


# 区
def getDistrict(index, provinceCode, provinceName, cityCode, cityName, href,file):
    _index = index
    _districtSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href);
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
        printInsertSql(_index, _districtCode, cityCode, 3, provinceName, cityName, _districtName, "", "",file)
        if (_href != ""):
            _index = getTown(_index, provinceCode, provinceName, cityCode, cityName, _districtCode, _districtName,
                             _href,file)
        loopIndex = loopIndex + 1
    return _index

#街道
def getTown(index, provinceCode, provinceName, cityCode, cityName, districtCode, districtName, href,file):
    _index = index
    _townSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href);
    _townHtml = _townSoup.find_all(attrs={'class': 'towntr'})
    loopIndex = 0
    while loopIndex < len(_townHtml):
        _index = _index + 1
        _townCode = _townHtml[loopIndex].select('a')[0].get_text()
        _townName = _townHtml[loopIndex].select('a')[1].get_text()
        printInsertSql(_index, _townCode, districtCode, 4, provinceName,cityName,districtName,_townName, "",file)
        _href = str(href.split("/")[0] + "/" + href.split("/")[1] + "/" + _townHtml[loopIndex].select('a')[0]['href'])
        _index = getVillage(_index,provinceCode, provinceName, cityCode, cityName, districtCode, districtName,_townCode,_townName,_href,file)
        loopIndex = loopIndex + 1
    return _index

#居委会
def getVillage(index, provinceCode, provinceName, cityCode, cityName, districtCode, districtName, townCode, townName,href,file):
    _index = index
    _villageSoup = getSoup("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/" + href);
    _villageHtml = _villageSoup.find_all(attrs={'class': 'villagetr'})
    loopIndex = 0
    while loopIndex < len(_villageHtml):
        _index = _index + 1
        _villageCode = _villageHtml[loopIndex].select('td')[0].get_text()
        _villageName = _villageHtml[loopIndex].select('td')[2].get_text()
        printInsertSql(_index,_villageCode,townCode,5,provinceName,cityName,districtName,townName,_villageName,file)
        loopIndex = loopIndex + 1
    return _index



def printInsertSql(id, code, parent_code, level_grade, province, city, district, street, neighborhood_committee,file):
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
    file.writelines("insert into RHIN_SYS.TB_DI_CHINA(\"id\",\"code\",\"parent_code\",\"level_grade\",\"short_name\",\"name\") values(\"" + _id + "\",\"" + _code + "\",\"" + _parent_code + "\",\"" + _level_grade + "\",\"" + _short_name + "\",\"" + _all_address + "\");"+'\n')
    print(str(_province+"|"+_city+"|"+_district+"|"+_street+"|"+_neighborhood_committee))
def openFile():
    file = open("/Users/wangjiaming/insert_into[python].sql", "a")
    return file

main()
