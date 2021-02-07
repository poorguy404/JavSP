"""网络请求的统一接口"""
import os
import sys
import requests
import lxml.html
from lxml import etree


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import cfg


__all__ = ['get_html', 'dump_xpath_node', 'is_url', 'is_connectable', 'download']


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}


def request_get(url):
    """获取指定url的原始请求"""
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r


def get_html_text(url, encoding=None):
    """获取指定网页的原始html文本"""
    r = request_get(url)
    if encoding:
        r.encoding = encoding
    else:
        r.encoding = r.apparent_encoding
    return r.text


def get_html(url, encoding='utf-8'):
    """获取指定网页经lxml解析后的document"""
    text = get_html_text(url, encoding=encoding)
    html = lxml.html.fromstring(text)
    html.make_links_absolute(url, resolve_base_href=True)
    # lxml.html.open_in_browser(html, encoding=encoding)  # for develop and debug
    return html


def dump_xpath_node(node, filename=None):
    """将xpath节点dump到文件"""
    if not filename:
        filename = node.tag + '.html'
    with open(filename, 'wt', encoding='utf-8') as f:
        content = etree.tostring(node, pretty_print=True).decode('utf-8')
        f.write(content)


def is_connectable(url, timeout=3):
    """测试与指定url的连接"""
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def download(url, file):
    """下载指定url的资源"""
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    with open(file, 'wb') as f:
        f.write(r.content)


if __name__ == "__main__":
    print(is_connectable('http://www.baidu.com'))