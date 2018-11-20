import requests

import re

import queue

import threading

# 登陆账号和密码

pixiv_id = '****'

password = '****'

# 关键字注意空格和斜杠等符号的url编码，比如我要搜索含有Fate/GrandOrder和リッパー标签的图片，则url的word后面应为：Fate%2FGrandOrder%20AND%20(%20リッパー%20%20)

# 按旧排序：&order=date，默认无

# 标签完全相似：s_tag_full，部分相似：s_tag

# 尺寸：横长&ratio=0.5，长度&ratio=-0.5，正方形&ratio=0


# 保存在本地的路径

local_path = 'D:/pix/'

# 这里设置关键字，在‘word=’的后面，注意要进行url编码

url_index = 'http://www.pixiv.net/search.php?s_mode=s_tag&word=saber&p='

# 以下三个条件只要满足一个条件就会爬取下来

# 爬取图片的获赞数应达到多少

min_score = 1500

# 爬取图片的获赞率达到的10%的获赞数应达到多少

min_score1 = 1000

# 爬取图片的获赞率达到的30%的获赞数应达到多少

min_score2 = 500

headers = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',

    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'

}

login_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'

post_url = 'https://accounts.pixiv.net/api/login?lang=zh'

se = requests.Session()

referer = 'http://www.pixiv.net'

url_img = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='

url_manga = 'http://www.pixiv.net/member_illust.php?mode=manga&illust_id='

url_manga_big1 = 'http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id='

url_manga_big2 = '&page='


class P(threading.Thread):

    def __init__(self, qu1, qu2):

        threading.Thread.__init__(self)

        self._queue1 = qu1

        self._queue2 = qu2

    def run(self):

        while not self._queue1.empty():
            self.get_img_url(self._queue1.get(), self._queue2)
        while not self._queue2.empty():
            self.spider(self._queue2.get())

    def spider(self, num):

        url = url_img + num

        count1 = 0

        headers['Referer'] = referer

        while True:

            try:

                count1 = count1 + 1

                # 获取图片信息介绍页面

                img_page = se.get(url=url, headers=headers).content.decode('utf-8')

                people = re.findall(re.compile('"viewCount":(\d+)'), img_page)

                score = re.findall(re.compile('"likeCount":(\d+)'), img_page)

                avar = 0.1

                if float(str(people[0])) > 0:
                    avar = float(str(score[0])) / float(str(people[0]))

                if (float(str(score[0])) >= min_score) or (float(str(score[0])) >= min_score1 and avar >= 0.1) or (
                        float(str(score[0])) >= min_score2 and avar == 0.3):

                    multiple = re.findall(re.compile('gVu_bev'), img_page)

                    count2 = 0

                    if len(multiple):

                        manga_info_url = url_manga + num

                        headers['Referer'] = url

                        while True:

                            try:

                                count2 = count2 + 1

                                # 获取manga类型图片的套图页面

                                manga_page = se.get(url=manga_info_url, headers=headers).content.decode('utf-8')

                                manga_urls = re.findall(re.compile('data-src="(.*?)"'), manga_page)

                                # 不要manga类型的大于10张的图片

                                if len(manga_urls) >= 10:
                                    return

                                for i in range(len(manga_urls)):
                                    manga_urls[i] = re.sub('_master\d+', '', manga_urls[i])

                                    manga_urls[i] = re.sub('master', 'original', manga_urls[i])

                                headers['Referer'] = manga_info_url

                                for each_manga in manga_urls:

                                    with open(local_path + each_manga.split('/')[-1], 'bw') as file:

                                        img = se.get(each_manga, headers=headers)

                                        if str(img.status_code) == '404':
                                            each_manga = re.sub('.jpg', '.png', each_manga)

                                            img = se.get(each_manga, headers=headers)

                                        count3 = 0

                                        while not str(img.status_code) == '200' and not count3 == 3:
                                            count3 = count3 + 1

                                            img = se.get(each_manga, headers=headers)

                                        file.write(img.content)

                                print('mangaSuccess!')

                                break

                            except Exception as e:

                                print('mangaError:' + str(e))

                                if count2 == 3:
                                    break

                                continue

                    else:

                        while True:

                            try:

                                count2 = count2 + 1

                                img_src = re.findall(re.compile('"original".+?.jpg'),img_page)

                                if not len(img_src):
                                    break

                                picSrc = img_src[0][12:].replace("\\","")
                                print('img_src:', picSrc)

                                with open(local_path + picSrc.split('/')[-1], 'bw') as file:

                                    img = se.get(picSrc, headers=headers)

                                    file.write(img.content)

                                print('mediumSuccess!')

                                break

                            except Exception as e:

                                print('imgError:' + str(e))

                                if count2 == 3:
                                    break

                                continue

                else:

                    break

                break

            except Exception as e:

                print(str(e))

                if count1 == 3:
                    break

                continue

    def get_img_url(self, url_page, qu2):

        count = 0

        while True:

            try:

                count = count + 1

                html_page = se.get(url=url_page, headers=headers)

                print(html_page.status_code)

                nums = re.findall(re.compile('illustId&quot;:&quot;(\d+)&'),
                                  html_page.content.decode('utf-8'))  # data-click-label

                for i in range(len(nums)):
                    qu2.put(str(nums[i])[-8:])

                    print(str(nums[i])[-8:])

                break

            except Exception as e:

                print(str(e))

                if count == 3:
                    break

                continue


def main():
    page_login = se.get(url=login_url, headers=headers).content.decode('utf-8')
    post_key = re.findall(re.compile('post_key" value="(.+?)"'), page_login)[0]
    print(post_key)
    data = {
        'pixiv_id': pixiv_id,
        'password': str(password),
        'post_key': post_key,
        'source': 'pc',
        'return_to': 'www.pixiv.net'
    }
    se.post(post_url, data=data, headers=headers)
    qu1 = queue.Queue()
    qu2 = queue.Queue()
    for i in range(1, 101):
        qu1.put(url_index + str(i))
    threads = []
    thread_count = 10
    for i in range(thread_count):
        threads.append(P(qu1, qu2))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
