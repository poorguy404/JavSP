"""从dl.getchu官网抓取数据"""
import os
import re
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from web.base import resp2html, request_get
from web.exceptions import *
from core.datatype import MovieInfo
from lxml import etree

logger = logging.getLogger(__name__)

# https://cn.pornhub.com/view_video.php?viewkey=660aaf4a88768
# base_url = 'https://www.pornhub.com/view_video.php?viewkey='
base_url = 'https://cn.pornhub.com/view_video.php?viewkey='
cookies = {
    'accessAgeDisclaimerPH': '1',
    'accessAgeDisclaimerUK': '1',
    'accessPH': '1',
    'cookieBannerState': '1',
    'platform': 'pc'
}


def get_movie_categories(html):
    categories = html.xpath('//div[@class="categoriesWrapper"]/a/text()')
    return categories


def get_movie_title(html):
    title = html.xpath('//div[contains(@class, "title-container")]/h1/span/text()')
    if len(title) != 0:
        title = str(title[0]).strip()
        return title
    return ''


def get_movie_actress(html) -> str:
    actresses = html.xpath("//div[@class='userInfo']//span[@class='usernameBadgesWrapper']/a/text()")
    if len(actresses) != 0:
        return str(actresses[0]).strip()
    return ''


def get_movie_cover(html) -> str:
    # cover = html.xpath("//form[@id='shareToStream']/div/img")[0].get('src')
    cover = html.xpath("//form[@id='shareToStream']/div/img/@src")
    if len(cover) == 0:
        return ''
    return str(cover[0])


def get_actress_pics(html):
    src = html.xpath('//div[@class="userAvatar"]/img/@src')
    if len(src) == 0:
        return ''
    return str(src[0])


def parse_data(movie: MovieInfo):
    """解析指定番号的影片数据"""
    # 去除番号中的'GETCHU'字样
    id_uc = movie.dvdid.lower()
    if not id_uc.startswith('phub-'):
        raise ValueError('Invalid phub number: ' + movie.dvdid)
    phub_viewkey = id_uc.replace('phub-', '')
    # 抓取网页
    url = f'{base_url}{phub_viewkey}'
    print('url = ', url)
    r = request_get(url, cookies=cookies, delay_raise=True)
    if r.status_code == 404:
        raise MovieNotFoundError(__name__, movie.dvdid)

    html = resp2html(r)
    movie.title = get_movie_title(html)
    movie.cover = get_movie_cover(html)
    movie.preview_pics = movie.cover
    movie.dvdid = id_uc
    movie.url = url
    movie.genre = get_movie_categories(html)
    actress:str = get_movie_actress(html)
    actress_pic:str = get_actress_pics(html)

    movie.actress = [actress]
    movie.actress_pics = {actress:actress_pic}






if __name__ == "__main__":
    import pretty_errors

    pretty_errors.configure(display_link=True)
    logger.root.handlers[1].level = logging.DEBUG

    movie = MovieInfo('phub-660df5644baa9')
    try:
        parse_data(movie)
        print(movie)
    except CrawlerError as e:
        logger.error(e, exc_info=1)
