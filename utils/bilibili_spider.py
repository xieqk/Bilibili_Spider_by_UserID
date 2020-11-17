import re
import os
import os.path as osp
import json
import time
import argparse
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse as url_parse

from .tools import mkdir_if_missing, write_json


class Bilibili_Spider():

    def __init__(self, uid, save_dir_json):
        self.uid = uid
        self.user_url = 'https://space.bilibili.com/{}'.format(uid)
        self.save_dir_json = save_dir_json
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(options=options)

    def close(self):
        # 关闭浏览器驱动
        self.browser.quit()

    def time_convert(self, time_str):
        time_item = time_str.split(':')
        assert len(time_item) == 2, 'time format error: {}, x:x expected!'.format(time_str)
        seconds = int(time_item[0])*60 + int(time_item[1])
        return seconds

    def date_convert(self, date_str):
        date_item = date_str.split('-')
        assert len(date_item) == 2 or len(date_item) == 3, 'date format error: {}, x-x or x-x-x expected!'.format(date_str)
        if len(date_item) == 2:
            year = datetime.datetime.now().strftime('%Y')
            date_str = '{}-{:>02d}-{:>02d}'.format(year, int(date_item[0]), int(date_item[1]))
        else:
            date_str = '{}-{:>02d}-{:>02d}'.format(date_item[0], int(date_item[1]), int(date_item[2]))
        return date_str

    def get_page_num(self):
        page_url = self.user_url + '/video?tid=0&page={}&keyword=&order=pubdate'.format(1)
        self.browser.get(page_url)
        time.sleep(2)
        html = BeautifulSoup(self.browser.page_source)

        page_number = html.find('span', attrs={'class':'be-pager-total'}).text
        user_name = html.find('span', id = 'h-name').text

        return int(page_number.split(' ')[1]), user_name

    def get_videos_by_page(self, idx):
        # 获取第 page_idx 页的视频信息
        urls_page, titles_page, plays_page, dates_page, durations_page = [], [], [], []
        page_url = self.user_url + '/video?tid=0&page={}&keyword=&order=pubdate'.format(idx+1)
        self.browser.get(page_url)
        time.sleep(2)
        html = BeautifulSoup(self.browser.page_source)

        ul_data = html.find('div', id = 'submit-video-list').find('ul', attrs= {'class': 'clearfix cube-list'})

        for li in ul_data.find_all('li'):
            # url & title
            a = li.find('a', attrs = {'target':'_blank', 'class':'title'})
            a_url = 'https:{}'.format(a['href'])
            a_title = a.text
            # pub_date & play
            date_str = li.find('span', attrs = {'class':'time'}).text.strip()
            pub_date = self.date_convert(date_str)
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            play = li.find('span', attrs = {'class':'play'}).text.strip()
            # duration
            time_str = li.find('span', attrs = {'class':'length'}).text
            duration = self.time_convert(time_str)
            # append
            urls_page.append(a_url)
            titles_page.append(a_title)
            dates_page.append((pub_date, now))
            plays_page.append(play)
            durations_page.append(duration)

        return urls_page, titles_page, plays_page, dates_page, durations_page

    def get(self):
        # 获取该 up 主的所有基础视频信息
        self.page_num, self.user_name = self.get_page_num()

        bvs = []
        urls = []
        titles = []
        plays = []
        dates = []
        durations = []   # by seconds

        for idx in range(self.page_num):
            print('>>>> page {}/{}'.format(idx+1, self.page_num))
            urls_page, titles_page, plays_page, dates_page, durations_page = self.get_videos_by_page(idx)
            while len(urls_page) == 0:
                print('failed, try again page {}/{}'.format(idx+1, self.page_num))
                urls_page, titles_page, plays_page, dates_page, durations_page = self.get_videos_by_page(idx)
            bvs_page = [x.split('/')[-1] for x in urls_page]
            assert len(urls_page) == len(titles_page), '{} != {}'.format(len(urls_page), len(titles_page)) 
            assert len(urls_page) == len(plays_page), '{} != {}'.format(len(urls_page), len(titles_page)) 
            assert len(urls_page) == len(dates_page), '{} != {}'.format(len(urls_page), len(dates_page))  
            assert len(urls_page) == len(durations_page), '{} != {}'.format(len(urls_page), len(durations_page))  
            print('result:')
            print(zip(bvs_page, titles_page, dates_page[0], durations_page, plays_page))
            bvs.extend(bvs_page)
            urls.extend(urls_page)
            titles.extend(titles_page)
            plays.extend(plays_page)
            dates.extend(dates_page)
            durations.extend(durations_page)

        data_list = []
        for i in range(len(urls_page)):
            result = {}
            result['user_name'] = self.user_name
            result['bv'] = bvs[i]
            result['url'] = urls[i]
            result['title'] = titles[i]
            result['play'] = plays[i]
            result['duration'] = durations[i]
            result['pub_date'] = dates[i][0]
            result['now'] = dates[i][1]
            data_list.append(result)
        
        json_path = osp.join(self.save_dir_json, '{}_{}.json'.format(self.user_name, self.uid))
        print('write json to {}'.format(json_path))
        mkdir_if_missing(self.save_dir_json)
        write_json(data_list, json_path)
        print('dump json file done. total {} urls'.format(len(urls)))



            
            


