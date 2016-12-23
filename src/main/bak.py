#_*_coding:utf-8_*_
'''
Created on 2016年12月1日

@author: weelin
'''

import requests,os,sys,time
from toomain.requesttoolport *
from bs4 import BeautifulSoup
from multiprocessing import Pool
from pymongo import MongoClient

BaseUrl='http://quanben.hongxiu.com/'
page_url_1 = 'free1.html'
page_url_2 = 'free.asp?page=20&dosort=0'
BaseDownPath = r'D:\hongxiu'

downtool=download()

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def downurl(url,encode):
    #print u'down %s.....'%url
     
    try:
        html = requests.get(url).content.decode(encode)
        #print type(html)
    except Exception as e:
        print 'down fail:',e
    return html


url = BaseUrl+page_url_2

def get_novels_info(url):
    '''
    787 诛心乱，凤掩芳华 暮野天埃 http://novel.hongxiu.com/a/989627/ 84
788 警察哥哥请爱我 耳鱼儿 http://novel.hongxiu.com/a/1173027/ 152
789 倾城军恋，白熊 风烙 http://novel.hongxiu.com/a/1250524/ 80
'''
    pagehtml = downtool.get(url,5).content.decode('gbk')
    #pagehtml = downurl(url,'gbk')
    soup = BeautifulSoup(pagehtml,'lxml')
    ul_list = soup.find('div',id='ltbox').find_all('li')
    print len(ul_list)
    tmp_l=[]
    for url in ul_list:
        li_l = url.find_all('li')
        index,name,author,url,chapters = li_l[0].get_text(),li_l[1].get_text(),li_l[2].get_text(),li_l[1].a['href'],li_l[5].get_text()
        tmp_l.append([index,name,author,url,chapters])#[u'1', u'\u7231\u60c5\u591c\u8272', u'\u5c55\u989c\u542c\u96e8', 'http://novel.hongxiu.com/a/1391475/', u'22']
        print index,name,author,url,chapters
    return tmp_l

get_novels_info(url)
#787 诛心乱，凤掩芳华 暮野天埃 http://novel.hongxiu.com/a/989627/ 84
#[u'787',u'诛心乱，凤掩芳华','暮野天埃',u'http://novel.hongxiu.com/a/989627/',u'84']
def down_one_novel(novel_info):
    novel_index = novel_info[0]
    novel_title = novel_info[1]
    novel_author = novel_info[2]
    novel_url = novel_info[3]+'list.html'
    novel_path = os.path.join(BaseDownPath,novel_index+'-'+novel_title)
    print u'正在下载%s....'%novel_title
    html = downurl(novel_url,'utf-8')
    soup = BeautifulSoup(html,'lxml')
    chapter_list = soup.find('div',class_='insert_list').find_all('li')
    for index,i in enumerate(chapter_list,1):
        chapter_url = 'http://novel.hongxiu.com' + i.a['href']
        chapter_name = str(index)+'-'+i.a.get_text()
        #print chapter_name,chapter_url
        html = downurl(chapter_url,'utf-8')
        soup = BeautifulSoup(html,'lxml')
        chapter_content = u'-------------%s--------------作者:%s\n\n'%(chapter_name,novel_author)+soup.find('div',id='htmlContent').contents[1].get_text()
        with open(novel_path,'ab+') as f:
            f.write(chapter_content.encode('utf-8')+'\n')
 
def main():
     
     
    #先搞一页:
    novels_info = get_novels_info(url)
     
    for novelinfo in novels_info:
        down_one_novel(novelinfo)
         
         
if __name__=='__main__':
    main()