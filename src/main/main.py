#_*_coding:utf-8_*_
'''
Created on 2016年12月1日

@author: weelin
'''

from lxml import etree
from bs4 import BeautifulSoup
from requesttool import download
import itertools
from multiprocessing import Pool
from pymongo import MongoClient
import os,time,requests
import sys

#reload(sys)

BaseUrl='http://quanben.hongxiu.com/'
BaseDownPath = r'D:\hongxiu'
ConnMongoDb = MongoClient()#与数据库建立连接
db = ConnMongoDb['hongxiu']#搞一个名为qsbk的库----db=qsbk
hongxiu = db['hongxiu_set']#搞一个名为qsbk_set的集合--table=qsbk_set

downtool=download()

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def downurl(url,encode):
    #print u'down %s.....'%url
     
    try:
        html = requests.get(url).content.decode(encode,'ignore')
        #print type(html)
    except Exception as e:
        print 'down fail:',e
    return html


def get_novels_info(url):
    '''
    <li class="t1">序号</li>
                <li class="t2">小说名</li>
                <li class="t3">作者</li>
                <li class="t4">属性</li>
                <li class="t5">结局</li>
                <li class="t6">章节</li>
                <li class="t7">阅读数</li>
                <li class="t8">完结时间</li>
    '''
    '''
    787 诛心乱，凤掩芳华 暮野天埃 http://novel.hongxiu.com/a/989627/ 84
    788 警察哥哥请爱我 耳鱼儿 http://novel.hongxiu.com/a/1173027/ 152
    789 倾城军恋，白熊 风烙 http://novel.hongxiu.com/a/1250524/ 80
    '''
    pagehtml = downtool.get(url,5).content.decode('gbk','ignore')
    #pagehtml = downurl(url,'gbk')
    #pagehtml = downurl(url,'gbk')
    selector = etree.HTML(pagehtml)
    li_index_list = selector.xpath('//div[@id="ltbox"]/ul/li[1]/text()')#索引
    li_title_list = selector.xpath('//div[@id="ltbox"]/ul/li[2]/a/text()')#小说名
    li_author_list = selector.xpath('//div[@id="ltbox"]/ul/li[3]/a/text()')#作者
    li_url_list = selector.xpath('//div[@id="ltbox"]/ul/li[2]/a/@href')#小说链接
    li_chapters_list = selector.xpath('//div[@id="ltbox"]/ul/li[6]/text()')#章节数
    
#     li_type_list = selector.xpath('//div[@id="ltbox"]/ul/li[4]/text()')#属性   
#     li_endtype_list = selector.xpath('//div[@id="ltbox"]/ul/li[5]/text()')#结局
#     li_readnum_list = selector.xpath('//div[@id="ltbox"]/ul/li[7]/text()')#阅读数 
#     li_finishtime_list = selector.xpath('//div[@id="ltbox"]/ul/li[8]/text()')#作品完成时间
    
    tmp_l = zip(li_index_list,li_title_list,li_author_list,li_url_list,li_chapters_list)
    return tmp_l


#787 诛心乱，凤掩芳华 暮野天埃 http://novel.hongxiu.com/a/989627/ 84
#[u'787',u'诛心乱，凤掩芳华','暮野天埃',u'http://novel.hongxiu.com/a/989627/',u'84']
def down_one_novel(novel_info):
    novel_title = novel_info[1]
    #判断是否已经下载过
    if hongxiu.find({'title':novel_title}).count():
        print u'%s下载过'%novel_title;return
    novel_index = novel_info[0]
    novel_author = novel_info[2]
    novel_url = novel_info[3]+'list.html'
    novel_chapters = novel_info[4]
    novel_path = os.path.join(BaseDownPath,novel_title)
    #清空文件
    with open(novel_path+'.txt','wb') as f:
            f.write('')
    print u'正在下载%s....'%novel_title
    try:
        html = downtool.get(novel_url,5).content.decode('utf-8')
    except Exception as e:
        print u'获取%s的章节urls error occur:'%novel_title,e
    soup = BeautifulSoup(html,'lxml')
    chapter_list = soup.find('div',class_='insert_list').find_all('li')
    if not chapter_list:
        try:
            os.remove(novel_path+'.txt')
            print u'找不到章节信息'
        except:
            pass
        finally:
            return
        
    for index,i in enumerate(chapter_list,1):
        chapter_url = 'http://novel.hongxiu.com' + i.a['href']
        chapter_name = i.a.get_text()
        try:
            html = downtool.get(chapter_url,5).content.decode('utf-8')
            soup = BeautifulSoup(html,'lxml')
        except Exception as e:
            print u"下载%s的章节内容 error occur:"%novel_title,e
        chapter_content = u'-------------%s--------------作者:%s\n\n'%(chapter_name,novel_author)+soup.find('div',id='htmlContent').contents[1].get_text()
        
        if not chapter_content:
            try:
                print u'章节内容为空'
                os.remove(novel_path+'.txt')
            except:
                pass
            finally:
                return
            
        with open(novel_path+'.txt','ab+') as f:
            f.write(chapter_content.encode('utf-8')+'\n')
    #写入mongo
    mongodb_data = {'title':novel_title,'author':novel_author,'chapters':novel_chapters,'url':novel_url}
    hongxiu.save(mongodb_data)
 
def main():
    for i in itertools.count():
        print u'正在搞第%d页.......'%i
        if i<11:page_url = BaseUrl+ 'free%d.html'%i
        else:page_url = BaseUrl+'free.asp?page=%s&dosort=0'%i
        print page_url
        novels_info = get_novels_info(page_url)
        pool = Pool(4)
        for novelinfo in novels_info:
            time.sleep(0.5)
            pool.apply_async(down_one_novel,(novelinfo,))
        pool.close()
        pool.join()

if __name__=='__main__':
    main()