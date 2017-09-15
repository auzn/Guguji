#-*-coding:utf-8-*-

from base64 import b64encode
from datetime import datetime
from io import BytesIO

import imgkit
import requests
from PIL import Image


class Messages(object):
    """打印内容画布"""
    __IMAGE_MAX_WIDTH = 384

    def __init__(self):
        self._msgs = []

    def __img_to_str(self, img):
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = img.size
        # 缩放
        if width > self.__IMAGE_MAX_WIDTH:
            img = img.resize((self.__IMAGE_MAX_WIDTH, int(
                height * self.__IMAGE_MAX_WIDTH / width)), Image.ANTIALIAS)
        # TODO 翻转
        p = BytesIO()
        img = img.convert('1').save(p, 'BMP')
        return p.getvalue()

    def append_text(self, text):
        """添加纯文本内容"""
        self._msgs.append(('T', text))
        return self

    def append_img(self, file_path):
        """添加图片"""
        img = Image.open(file_path)
        self._msgs.append(('P', self.__img_to_str(img)))
        return self

    def append_img_from_url(self, url):
        """添加网页截图"""
        opt = {'zoom': '3', 'minimum-font-size': '28'}
        imgbytes = imgkit.from_url(url, False, options=opt)
        f = BytesIO()
        f.write(imgbytes)
        img = Image.open(f)
        self._msgs.append(('P', self.__img_to_str(img)))
        f.close()

    def append_img_with_html_sorce(self, html_source):
        """添加HTML源代码内容，可用作富文本展示"""
        opt = {'width': 384}
        imgbytes = imgkit.from_string(html_source, False, options=opt)
        f = BytesIO()
        f.write(imgbytes)
        img = Image.open(f)
        self._msgs.append(('P', self.__img_to_str(img)))
        f.close()

    def to_string(self):
        encoded = []
        last = len(self._msgs) - 1
        for index, (content_type, data) in enumerate(self._msgs):
            if content_type == "T":
                if not index == last and not data.endswith("\n"):
                    data += "\n"
                encoded.append(
                    "T:" + b64encode(self._ensure_gbk(data)).decode('ascii'))
            elif content_type == "P":
                encoded.append("P:" + b64encode(data).decode('ascii'))
        return "|".join(encoded)

    def _ensure_gbk(self, txt):
        try:
            txt = txt.decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        return txt.encode('GBK')


class Guguji(object):
    """咕咕机API"""
    __BASE_URL = 'http://open.memobird.cn/home'
    __headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    __css = '''
html {
            font-size: 20px;
        }

        body {
            width: 19.2em;
            font-size: 1em;
            font-family: Microsoft YaHei;
            text-align: center;
            color: #444;
            background: #e6e6e6;
            padding: 0;
            margin: 0;
        }

        #wrap {
            margin: 0 auto;
            background: #fff;
        }

        .f8 {
            font-size: 2.3em
        }

        .f10 {
            font-size: 1.8em;
        }

        .f12 {
            font-size: 1.5em
        }

        .f14 {
            font-size: 1.3em;
        }

        .f16 {
            font-size: 1.15em;
        }

        .f18 {
            font-size: 1em;
        }

        .f20 {
            font-size: 18px;
        }

        .f_normal {
            font-weight: normal;
        }

        .f_thick {
            font-weight: bold;
        }

        .f_thicker {
            font-weight: 900;
        }
    '''

    def __init__(self, device_id, user_id='', ak='c7548afbab99479e9f9a59aa1d65d5c6'):
        self._device_id = device_id
        self._ak = ak
        self.__session = requests.session()
        r = self._request('/setuserbind', {
            'memobirdID': device_id,
            'useridentifying': user_id
        })
        self.user_id = r['showapi_userid']

    def _request(self, uri, data):
        url = self.__BASE_URL + uri
        data.update({
            'ak': self._ak,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        r = self.__session.post(url, json=data, headers=self.__headers)
        r.raise_for_status()
        return r.json()

    def print_msgs(self, msgs):
        """打印画布"""
        r = self._request(
            '/printpaper',
            data={
                'printcontent': msgs.to_string(),
                'memobirdID': self._device_id,
                'userID': self.user_id
            })
        return r['printcontentid']

    def print_text(self, text):
        """打印纯文本"""
        m = Messages()
        m.append_text(text)
        return self.print_msgs(m)

    def print_img(self, file_path):
        """打印图片"""
        m = Messages()
        m.append_img(file_path)
        return self.print_msgs(m)

    def print_img_from_url(self, url):
        """打印网页截图"""
        m = Messages()
        m.append_img_from_url(url)
        return self.print_msgs(m)

    def print_img_with_html_source(self, html_source):
        """打印富文本/HTML源代码"""
        m = Messages()
        m.append_img_with_html_sorce(html_source)
        return self.print_msgs(m)

    def is_msgs_printed(self, msgs_id):
        """请求打印状态"""
        r = self._request('/getprintstatus', data={'printcontentid': msgs_id})
        return r['printflag'] == 1
