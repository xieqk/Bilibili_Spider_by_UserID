import re
import os
import os.path as osp
import sys
import json
import time
import argparse
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse as url_parse
import random

from .tools import mkdir_if_missing, write_json, read_json


class Bilibili_Spider():

    def __init__(self, uid, save_dir_json='json', save_by_page=False, t=2):
        self.t = t
        self.uid = uid
        self.user_url = 'https://space.bilibili.com/{}'.format(uid)
        self.save_dir_json = save_dir_json
        self.save_by_page = save_by_page
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(options=options)
        print('spider init done.')

    def close(self):
        # 关闭浏览器驱动
        self.browser.quit()

    def time_convert(self, time_str):
        time_item = time_str.split(':')
        # assert len(time_item) == 2, 'time format error: {}, x:x expected!'.format(time_str)
        if len(time_item) == 2:
            seconds = int(time_item[0]) * 60 + int(time_item[1])
        elif len(time_item) == 3:
            seconds = int(time_item[0]) * 3600 + int(time_item[1]) * 60 + int(time_item[2])
        return seconds

    def date_convert(self, date_str):
        date_item = date_str.split('-')
        assert len(date_item) == 2 or len(date_item) == 3, 'date format error: {}, x-x or x-x-x expected!'.format(
            date_str)
        if len(date_item) == 2:
            year = datetime.datetime.now().strftime('%Y')
            date_str = '{}-{:>02d}-{:>02d}'.format(year, int(date_item[0]), int(date_item[1]))
        else:
            date_str = '{}-{:>02d}-{:>02d}'.format(date_item[0], int(date_item[1]), int(date_item[2]))
        return date_str

    def get_page_num(self):
        page_url = self.user_url + '/video?tid=0&page={}&keyword=&order=pubdate'.format(1)
        self.browser.get(page_url)
        time.sleep(self.t + 2 * random.random())
        html = BeautifulSoup(self.browser.page_source, features="html.parser")

        page_number = html.find('span', attrs={'class': 'be-pager-total'}).text
        user_name = html.find('span', id='h-name').text

        return int(page_number.split(' ')[1]), user_name

    def get_videos_by_page(self, idx):
        # 获取第 page_idx 页的视频信息
        urls_page, titles_page, plays_page, dates_page, durations_page = [], [], [], [], []
        page_url = self.user_url + '/video?tid=0&pn={}&keyword=&order=pubdate'.format(idx + 1)
        self.browser.get(page_url)
        time.sleep(self.t + 2 * random.random())
        html = BeautifulSoup(self.browser.page_source, features="html.parser")

        ul_data = html.find('div', id='submit-video-list').find('ul', attrs={'class': 'clearfix cube-list'})

        for li in ul_data.find_all('li'):
            # url & title
            a = li.find('a', attrs={'target': '_blank', 'class': 'title'})
            a_url = 'https:{}'.format(a['href'])
            a_title = a.text
            # pub_date & play
            date_str = li.find('span', attrs={'class': 'time'}).text.strip()
            pub_date = self.date_convert(date_str)
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            play = li.find('span', attrs={'class': 'play'}).text.strip()
            # duration
            time_str = li.find('span', attrs={'class': 'length'}).text
            duration = self.time_convert(time_str)
            # append
            urls_page.append(a_url)
            titles_page.append(a_title)
            dates_page.append((pub_date, now))
            plays_page.append(play)
            durations_page.append(duration)

        return urls_page, titles_page, plays_page, dates_page, durations_page

    def save(self, json_path, bvs, urls, titles, plays, durations, dates):
        data_list = []
        for i in range(len(urls)):
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

        print('write json to {}'.format(json_path))
        dir_name = osp.dirname(json_path)
        mkdir_if_missing(dir_name)
        write_json(data_list, json_path)
        print('dump json file done. total {} urls. \n'.format(len(urls)))

    def get(self):
        # 获取该 up 主的所有基础视频信息
        print('Start ... \n')
        self.page_num, self.user_name = self.get_page_num()
        while self.page_num == 0:
            print('Failed to get user page num, poor network condition, retrying ... ')
            self.page_num, self.user_name = self.get_page_num()
        print('Pages Num {}, User Name: {}'.format(self.page_num, self.user_name))

        bvs = []
        urls = []
        titles = []
        plays = []
        dates = []
        durations = []  # by seconds

        for idx in range(self.page_num):
            print('>>>> page {}/{}'.format(idx + 1, self.page_num))
            urls_page, titles_page, plays_page, dates_page, durations_page = self.get_videos_by_page(idx)
            while len(urls_page) == 0:
                print('failed, try again page {}/{}'.format(idx + 1, self.page_num))
                urls_page, titles_page, plays_page, dates_page, durations_page = self.get_videos_by_page(idx)
            bvs_page = [x.split('/')[-1] for x in urls_page]
            assert len(urls_page) == len(titles_page), '{} != {}'.format(len(urls_page), len(titles_page))
            assert len(urls_page) == len(plays_page), '{} != {}'.format(len(urls_page), len(titles_page))
            assert len(urls_page) == len(dates_page), '{} != {}'.format(len(urls_page), len(dates_page))
            assert len(urls_page) == len(durations_page), '{} != {}'.format(len(urls_page), len(durations_page))
            print('result:')
            print('{}_{}: '.format(self.user_name, self.uid), bvs_page, ', {} in total'.format(len(urls_page)))
            sys.stdout.flush()
            bvs.extend(bvs_page)
            urls.extend(urls_page)
            titles.extend(titles_page)
            plays.extend(plays_page)
            dates.extend(dates_page)
            durations.extend(durations_page)
            if self.save_by_page:
                json_path_page = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'primary',
                                          'page_{}.json'.format(idx + 1))
                self.save(json_path_page, bvs_page, urls_page, titles_page, plays_page, durations_page, dates_page)

        json_path = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'primary', 'full.json')
        self.save(json_path, bvs, urls, titles, plays, durations, dates)

    def get_url(self, url):
        self.browser.get(url)
        time.sleep(self.t + 2 * random.random())
        html = BeautifulSoup(self.browser.page_source, features="html.parser")

        video_data = html.find('div', id='viewbox_report').find_all('span')
        play = int(video_data[1]['title'][4:])
        danmu = int(video_data[2]['title'][7:])
        date = video_data[3].text

        multi_page = html.find('div', id='multi_page')
        if multi_page is not None:
            url_type = 'playlist'
            pages = multi_page.find('span', attrs={'class': 'cur-page'}).text
            page_total = int(pages.split('/')[-1])
        else:
            url_type = 'video'
            page_total = 1

        return play, danmu, date, url_type, page_total

    def get_detail(self):
        print('Start to get detailed information for each url.')
        if self.save_by_page:
            data = []
            for idx in range(self.page_num):
                json_path = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'primary',
                                     'page_{}.json'.format(idx + 1))
                data_page = read_json(json_path)
                for j, item in enumerate(data_page):
                    url = item['url']
                    print('>>>> page {}/{}, No. {}/{}'.format(idx + 1, self.page_num, j + 1, len(data_page)))
                    play, danmu, date, url_type, page_total = self.get_url(url)
                    # print(play, danmu, date, url_type, page_total)
                    assert page_total > 0, page_total
                    if page_total == 1:
                        assert url_type == 'video', (url_type, page_total)
                        data_page[j]['play'] = play
                        data_page[j]['danmu'] = danmu
                        data_page[j]['pub_date'] = date
                        data_page[j]['type'] = url_type
                        data_page[j]['num'] = page_total
                    else:
                        assert url_type == 'playlist', (url_type, page_total)
                        data_page[j]['play'] = play
                        data_page[j]['danmu'] = danmu
                        data_page[j]['pub_date'] = date
                        data_page[j]['type'] = url_type
                        data_page[j]['num'] = page_total

                json_path_save = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'detailed',
                                          'page_{}.json'.format(idx + 1))
                print('write json to {}'.format(json_path_save))
                write_json(data_page, json_path_save)
                print('dump json file done. total {} urls. \n'.format(len(data_page)))
                data.extend(data_page)

            json_path_save = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'detailed',
                                      'full.json')
            print('write json to {}'.format(json_path_save))
            write_json(data, json_path_save)
            print('dump json file done. total {} urls. \n'.format(len(data)))
        else:
            json_path = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'primary', 'full.json')
            data = read_json(json_path)
            for j, item in enumerate(data):
                url = item['url']
                print('>>>> No. {}/{}'.format(j + 1, len(data)))
                play, danmu, date, url_type, page_total = self.get_url(url)
                assert page_total > 0, page_total
                if page_total == 1:
                    assert url_type == 'video', (url_type, page_total)
                    data[j]['play'] = play
                    data[j]['danmu'] = danmu
                    data[j]['pub_date'] = date
                    data[j]['type'] = url_type
                    data[j]['num'] = page_total
                else:
                    assert url_type == 'playlist', (url_type, page_total)
                    data[j]['play'] = play
                    data[j]['danmu'] = danmu
                    data[j]['pub_date'] = date
                    data[j]['type'] = url_type
                    data[j]['num'] = page_total

            json_path_save = osp.join(self.save_dir_json, '{}_{}'.format(self.user_name, self.uid), 'detailed',
                                      'full.json')
            print('write json to {}'.format(json_path_save))
            write_json(data, json_path_save)
            print('dump json file done. total {} urls. \n'.format(len(data)))
