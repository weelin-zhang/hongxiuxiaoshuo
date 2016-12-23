#_*_coding:utf-8_*_

import requests,re,random
import time,os
import conf

class download(object):
    
    def __init__(self):
        #拿到代理iplist
#         iprespon = requests.get('http://haoip.cc/tiqu.htm')
#         pattern = re.compile(r'r/>(.*?)<b',re.S)
#         ipresult = re.findall(pattern, iprespon.text)
#         self.iplist = list(i.strip() for i in ipresult)
        self.iplist = conf.proxy_ip_list
        self.UserAgent = conf.user_agent_list   
    def get(self,url,timeout,proxy=False,num_retries=3):
        '''url timeout,proxy,num_retries
                返回response对象
        '''
        #伪造UserAgent
        UA = self.UserAgent[random.randint(0,len(self.UserAgent)-1)]
        
        headers = {'User-Agent':UA}
        if proxy == False:
            try:
                return requests.get(url,timeout=timeout,headers=headers)
                print '2'
            except Exception as e:
                print '3',e
                #判断retries
                if num_retries>0:
                    print u'爬取网页错误,10s后继续尝试.....'
                    time.sleep(1)
                    return self.get(url, timeout, False, num_retries-1)
                else:#重试次数用尽,使用代理
                    time.sleep(1)
                    IP = str(random.choice(self.iplist))
                    proxy = {'http',IP}
                    return self.get(url, timeout, True,8)
                
        else:#使用代理
            
            try:
                print '开始使用代理'
                IP = str(random.choice(self.iplist))
                proxy = {'http':IP}
                print proxy['http']
                return requests.get(url,headers=headers, timeout=timeout, proxies=proxy)
            except:
                if num_retries>0:
                    print u'代理爬取网页错误,10s后继续尝试.....'
                    time.sleep(1)
                    return self.get(url, timeout,True, num_retries-1)
                else:#代理也不行
                    time.sleep(30)
                    print u'代理也没用...'
                    return self.get(url, 3)
 
 
def mkdir(path): 
    if os.path.exists(path) and os.path.isdir(path):
        #print u'%s 存在'%path
        pass
    else:
        os.makedirs(path)
 
def test():
    t=download()
    #tt = t.get('http://www.baidu.com',10,)
    #print tt.text

if __name__=='__main__':
    test()