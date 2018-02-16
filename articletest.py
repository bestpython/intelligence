#.*-coding:utf-8-*-
import requests
from lxml import etree
from database import Database
from HTMLParser import HTMLParser
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
函数说明:根据算法自动识别正文

Author:
    Liao
Modify:
    2018-02-16
"""

class spider(object):

    #获取增益系数
    def __init__(self):
        try:
            database = Database()
            database.connect('crawl_data')
            selectsql = """select * from article_tree"""
            data = database.query(selectsql)
            self.feature1 = data[0]['feature1']
            self.feature2 = data[0]['feature2']
            self.feature3 = data[0]['feature3']
            self.feature4 = data[0]['feature4']
            self.feature5 = data[0]['feature5']
        except:
            print '未使用数据库'
            self.feature1 = 0.046
            self.feature2 = 0.081
            self.feature3 = 0.228
            self.feature4 = 0.228
            self.feature5 = 0.046


    def check(self, sourceHtml):
        articlelist = []
        proportionlist = []
        similarity = []
        selector = etree.HTML(sourceHtml)
        articlediv = selector.xpath("//div")

        for content in articlediv:
            content = HTMLParser().unescape(etree.tostring(content))
            articlelist.append(content)


        for i in range(len(articlelist)):
            item = articlelist[i].replace("\n",'').replace(u'\xa0','').replace(" ",'')
            count = 0
            f1 = (1 if re.match(r'<divclass="[\w\s-]*art[\w\s-]*">', item) else 0)*self.feature1    #判断标签类型
            f2 = (1 if re.match(r'<divclass="[\w\s-]*cont[\w\s-]*">', item) else 0)*self.feature2
            f3 = (1 if '</p>' in item else 0)*self.feature3      #判断是否包含段落标签
            f4 = 0

            if f1:
                print item
            for word in item.decode('utf-8'):
                if u'\u4e00' <= word <= u'\u9fa5':         #是否包含中文
                    f4 = self.feature4
                    count += 1
            proportion = float(count) / len(item)           #计算中文所占比例

            proportionlist.append(proportion)

            feature = f1 + f2 + f3 + f4
            similarity.append(feature)
        f5ind = proportionlist.index(max(proportionlist))
        newf5 = similarity[f5ind] + self.feature5
        proportionlist[f5ind] = newf5

        #日后此数据也将进入数据库对信息熵进行更新

        ind = similarity.index(max(similarity))  #取得分最高的字句

        articlexpath = re.search(r'<div class="(.*)">', articlelist[ind]).group(1)
        print '//div[@class="{}"]//text()'.format(articlexpath)
        return '//div[@class="{}"]//text()'.format(articlexpath)

    # 获取url对应的网页源码
    def getsource(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        sourceHtml = requests.get(url, headers=headers)
        return sourceHtml.text

    # 从html中解析我们需要的数据
    def getNeedInfo(self, sourceHtml):

        articlexpath = self.check(sourceHtml)
        selector = etree.HTML(sourceHtml)
        article = selector.xpath(articlexpath)
        content = ''
        for word in article:
            # content += word.strip().replace(u'\xa0','').encode('raw_unicode_escape')
            content += word.strip()
        print content


if __name__ == '__main__':
    spider = spider()
    url = "http://365jia.cn/news/2018-02-11/73D175A3A9F05079.html"
    # url = 'http://www.ahwang.cn/zbah/20180211/1738282.shtml'
    html = spider.getsource(url)

    spider.getNeedInfo(html)