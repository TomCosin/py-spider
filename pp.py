import queue
import requests
import re
import threading
import random
import string

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    'Referer': 'http://www.meizitu.com'
}

url = 'http://www.meizitu.com/a/more_'

local_path = 'D:/pix/'

def spider(album_url):
    count = 0
    while count < 3:
        album_html = requests.get(url=album_url, headers=headers)
        if str(album_html.status_code) == '200':
            picUrls = re.findall(re.compile('张" src="(\S+)"'), album_html.content.decode("GBK"))
            for pic in picUrls:
                with open(local_path + ''.join(random.sample(string.ascii_lowercase,5)) + pic.split('/')[-1], 'bw') as file:
                    img = requests.get(pic, headers=headers)
                    file.write(img.content)
            break
        count += 1


def get_img_url(pageUrl, qu2):
    count = 0
    while count < 3:
        r = requests.get(url=pageUrl, headers=headers)
        if str(r.status_code) == '200':
            pic = re.findall(re.compile('http://www.meizitu.com/a/[0-9]{4}\.html'), r.content.decode("GBK"))
            for albumUrl in pic:
                print(albumUrl)
                qu2.put(albumUrl)
            break
        count += 1


class Pthread(threading.Thread):
    def __init__(self, qu1, qu2):
        threading.Thread.__init__(self)
        self._queue1 = qu1
        self._queue2 = qu2

    def run(self):
        while not self._queue1.empty():
            get_img_url(self._queue1.get(), self._queue2)
        while not self._queue2.empty():
            spider(self._queue2.get())


def main():
    # 放入q1
    qu1 = queue.Queue()
    qu2 = queue.Queue()
    for i in range(1, 11):
        qu1.put(url + str(i) + '.html')
    threads = []
    thread_count = 10
    for i in range(thread_count):
        threads.append(Pthread(qu1, qu2))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
