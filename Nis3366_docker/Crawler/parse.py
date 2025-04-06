import re
import parsel
import json
from typing import Optional, List
from datetime import datetime, timedelta
from Front_end.config_front import request_headers,cookies_config
import httpx


'--------------------------------------------- basic funcitions  --------------------------------------------------'

def process_time_str(time_str:str) -> datetime:
    """这段代码是用来解析微博的时间字段的
         1. 处理 年、月、日、时、分
         2. 处理 分钟前，小时前，这里不处理秒前

    Args:
        time_str (str): 微博时间字段

    Returns:
        datatime: 返回时间字段
    """
    datetime_now = datetime.now()

    if "年" in time_str:
        year = re.search(r"(\d{4})年", time_str).group(1)
    else:
        year = datetime_now.year
    if "月" in time_str:
        month = re.search(r"(\d{1,2})月", time_str).group(1)
    else:
        month = datetime_now.month
    if "日" in time_str:
        day = re.search(r"(\d{1,2})日", time_str).group(1)
    else:
        day = datetime_now.day
    if ":" in time_str:
        hour = re.search(r"(\d{1,2}):", time_str).group(1)
        minute = re.search(r":(\d{1,2})", time_str).group(1)
    else:
        hour = datetime_now.hour
        minute = datetime_now.minute

    datetime_now = datetime(int(year), int(month), int(day), int(hour), int(minute))

    if "分钟前" in time_str:
        minute_before = re.search(r"(\d+)分钟前", time_str).group(1)
        datetime_now = datetime_now - timedelta(minutes=int(minute_before))
    if "小时前" in time_str:
        hour_before = re.search(r"(\d+)小时前", time_str).group(1)
        datetime_now = datetime_now - timedelta(hours=int(hour_before))

    return datetime_now

'--------------------------------------------- parse topic posts  --------------------------------------------------'

def get_mid(select: parsel.Selector) -> Optional[str]:
    """获取微博的mid

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的mid
    """
    mid = select.xpath("//div[@mid]/@mid").get()
    return mid


def get_uid(select: parsel.Selector) -> Optional[str]:
    """获取微博的uid

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的uid
    """
    uid = select.xpath("//a[@nick-name]/@href").get()
    if uid is None:
        return None
    else:
        uid = re.search(r"/(\d+)/?", uid).group(1)
        return uid
    

def get_mblogid(select: parsel.Selector) -> Optional[str]:
    """获取微博的mblogid

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的mblogid
    """
    mblogid = select.xpath('//div[@class="from"]/a[1]/@href').get()
    if mblogid is None:
        return None
    else:
        mblogid = re.search(r"/(\w+)\?", mblogid).group(1)
        return mblogid
    

def get_personal_name(select: parsel.Selector) -> Optional[str]:
    """获取微博的个人名称

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的个人名称
    """
    personal_name = select.xpath("//a[@nick-name]/@nick-name").get()
    return personal_name


def get_personal_href(select: parsel.Selector) -> Optional[str]:
    """获取微博的个人主页

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 个人主页的 URL
    """
    personal_href = select.xpath("//a[@nick-name]/@href").get()
    if personal_href is None:
        return None
    else:
        return "https:" + personal_href
    

def get_weibo_href(select: parsel.Selector) -> Optional[str]:
    """获取微博的链接

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的链接
    """
    weibo_href = select.xpath('//div[@class="from"]/a[1]/@href').get()
    if weibo_href is None:
        return None
    else:
        return "https:" + weibo_href
    

def get_publish_time(select: parsel.Selector) -> Optional[str]:
    """获取微博的发布时间

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[datetime]: 微博的发布时间
    """
    publish_time_str = select.xpath('//div[@class="from"]/a[1]/text()').get()
    if publish_time_str is None:
        return publish_time_str
    else:
        publish_time = process_time_str(publish_time_str).strftime("%Y-%m-%d %H:%M:%S")
        return publish_time
    

def get_content_from(select:parsel.Selector) -> Optional[str]:
    """获取微博的发送设备

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的发送设备
    """
    content_from = select.xpath('//div[@class="from"]/a[2]/text()').get()
    return content_from


def get_content_all(select:parsel.Selector) -> Optional[str]:
    """获取微博的内容

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[str]: 微博的内容
    """
    content_all = select.xpath('string(//p[@node-type="feed_list_content_full"])').get()
    content_all = re.sub(r"\n[ \t]+", "\n", content_all)
    content_all = re.sub(r"(?<!\n)\n(?!\n)", "", content_all)
    content_all = re.sub(r"[ \t]*收起d[ \t]*", "", content_all)

    content_show = select.xpath('string(//p[@node-type="feed_list_content"])').get()
    content_show = re.sub(r"\n[ \t]+", "\n", content_show)
    content_show = re.sub(r"(?<!\n)\n(?!\n)", "", content_show)
    
    content_final = content_all if content_all else content_show
    content_final = content_final.replace("\u200b", "").strip()
    content_final = re.sub(r"[ \t]*\n+[ \t]*", "\n\n", content_final)

    return content_final


def get_retweet_num(select: parsel.Selector) -> Optional[int]:
    """获取微博的转发数量

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[int]: 微博的转发数量
    """
    retweet_num = select.xpath('string(//div[@class="card-act"]/ul[1]/li[1])').get()
    if retweet_num:
        retweet_num = re.findall(r"\d+", retweet_num)
        return int(retweet_num[0]) if retweet_num else 0
    else:
        return None
    

def get_comment_num(select:parsel.Selector) -> Optional[int]:
    """获取微博的评论数量

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[int]: 微博的评论数量
    """
    comment_num = select.xpath('string(//div[@class="card-act"]/ul[1]/li[2])').get()
    if comment_num:
        comment_num = re.findall(r"\d+", comment_num)
        return int(comment_num[0]) if comment_num else 0
    else:
        return None
    

def get_star_num(select: parsel.Selector) -> Optional[int]:
    """获取微博的点赞数量

    Args:
        select (parsel.Selector): 经过 parsel 解析 html 后得到的 Selector 对象

    Returns:
        Optional[int]: 微博的点赞数量
    """
    star_num = select.xpath('string(//div[@class="card-act"]/ul[1]/li[3])').get()
    if star_num:
        star_num = re.findall(r"\d+", star_num)
        return int(star_num[0]) if star_num else 0
    else:
        return None
    

def get_page_num(html: str) -> int:
    """获取微博列表页数

    Args:
        html (str): 爬虫获取到的 html 文本

    Returns:
        int: 微博列表页数
    """
    select = parsel.Selector(html)
    page_list = select.xpath('//ul[@node-type="feed_list_page_morelist"]')
    if page_list:
        page_links = page_list.xpath('.//li/a/@href').getall()
        page_numbers = []
        for link in page_links:
            match = re.search(r'page=(\d+)', link)
            if match:    
                page_numbers.append(int(match.group(1)))
        if page_numbers:
            return max(page_numbers)
    return 0

def get_location(uid: str) -> str:
    """获取微博用户的地理位置

    Args:
        uid (str): 微博用户的uid

    Returns:
        Optional[str]: 微博用户的地理位置
    """
    url = "https://weibo.com/ajax/profile/detail?uid="+uid
    headers = request_headers.body_headers
    cookies = cookies_config.cookies
    location = ""
    
    with httpx.Client() as client:
        try:
            response = client.get(url,headers=headers,cookies=cookies)
            data = response.json()
            location = data.get("data", {}).get("ip_location", "IP属地：未知")
            location = location.replace("IP属地：", "")
        except Exception as e:
            print(e)
    return location


async def parse_list_html(html: str) -> List[dict]:
    """解析微博列表主体的html

    Args:
        html (str): 爬虫获取到的 html 文本

    Returns:
        List[dict]: 整理后的 List[dict]
    """
    select = parsel.Selector(html)
    div_list = select.xpath('//*[@id="pl_feedlist_index"]//div[@action-type="feed_list_item"]').getall()
    lst = []
    for div_string in div_list:
        select = parsel.Selector(div_string)
        item = {
            "mid": get_mid(select),
            "uid": get_uid(select),
            "mblogid": get_mblogid(select),
            "personal_name": get_personal_name(select),
            "personal_href": get_personal_href(select),
            "weibo_href": get_weibo_href(select),
            "publish_time": get_publish_time(select),
            "content_from": get_content_from(select),
            "content_all": get_content_all(select),
            "retweet_num": get_retweet_num(select),
            "comment_num": get_comment_num(select),
            "star_num": get_star_num(select),
        }
        item["location"] = get_location(item["uid"])
        lst.append(item)

    return lst