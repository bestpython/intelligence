#.*-coding:utf-8-*-
import requests
from lxml import etree
from database import Database
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
函数说明:根据算法自动识别标题

Author:
    Liao
Modify:
    2018-02-11
"""

class spider(object):

    #获取增益系数
    def __init__(self):
        try:
            database = Database()
            database.connect('crawl_data')
            selectsql = """select * from title_tree"""
            data = database.query(selectsql)
            self.feature1 = data[0]['feature1']
            self.feature2 = data[0]['feature2']
            self.feature3 = data[0]['feature3']
            self.feature4 = data[0]['feature4']
            self.feature5 = data[0]['feature5']
        except:
            print '未使用数据库'
            self.feature1 = 0.132
            self.feature2 = 0.132
            self.feature3 = 0.132
            self.feature4 = 0.228
            self.feature5 = 0.081


    def check(self, sourceHtml):
        titlelist = []
        similarity = []
        selector = etree.HTML(sourceHtml)
        h1title = selector.xpath('//h1/text()')
        h2title = selector.xpath('//h2/text()')
        for title in h1title:
            titlelist.append(title)
        for title in h2title:
            titlelist.append(title)

        for i in range(len(titlelist)):
            item = titlelist[i].replace("\n",'').replace(u'\xa0','')

            f1 = (1 if i<len(h1title) else 0)*self.feature1    #判断标签类型
            f2 = (1 if i>=len(h1title) else 0)*self.feature2
            f3 = (1 if len(item)>10 else 0)*self.feature3      #判断字句长度
            f4 = 0
            f5 = 0
            if item:
                for word in item.decode('utf-8'):
                    if u'\u4e00' <= word <= u'\u9fff':         #是否包含中文
                        f4 = self.feature4
                        break
                for word in item.decode('utf-8'):              #是否包含英文
                    if (word >= u'\u0041' and word <= u'\u005a') or (word >= u'\u0061' and word <= u'\u007a'):
                        f5 = self.feature5
                        break
            feature = f1 + f2 + f3 + f4 + f5
            similarity.append(feature)
        #日后此数据也将进入数据库对信息熵进行更新

        ind = similarity.index(max(similarity))  #取得分最高的字句
        if ind < len(h1title):
            return "//h1/text()[{}]".format(ind+1)
        else:
            return '//h2/text()[{}]'.format(ind-len(h1title)+1)


    # 获取url对应的网页源码
    def getsource(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        sourceHtml = requests.get(url, headers=headers)
        return sourceHtml.text

    # 从html中解析我们需要的数据
    def getNeedInfo(self, sourceHtml):

        titlexpath = self.check(sourceHtml)
        selector = etree.HTML(sourceHtml)
        title = selector.xpath(titlexpath)[0]
        print titlexpath
        print title
        print title.encode('raw_unicode_escape')


if __name__ == '__main__':
    spider = spider()
    url = "http://365jia.cn/news/2018-02-11/73D175A3A9F05079.html"
    # url = 'http://www.ahwang.cn/zbah/20180211/1738282.shtml'
    html = spider.getsource(url)

    spider.getNeedInfo(html)