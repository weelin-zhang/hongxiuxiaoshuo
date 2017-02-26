# hongxiuxiaoshuo
crawl  "http://quanben.hongxiu.com/" novels


爬取红袖小说网所有全本完结小说并保存，并把小说信息存储之mongodb数据库

使用模块:

from lxml import etree

from bs4 import BeautifulSoup

from requesttool import download

import itertools

from multiprocessing import Pool

from pymongo import MongoClient

import os,time,requests

import sys
