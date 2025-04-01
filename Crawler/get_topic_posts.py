import sys
sys.path.append("")

import time
import random
import httpx
import asyncio
from datetime import datetime,timedelta
from typing import Literal, Optional, Any
from copy import deepcopy

from .BaseCrawler import BaseCrawler
from Front_end.config_front import cookies_config, request_headers
from .parse import parse_list_html,get_page_num

def random_sleep():
    time.sleep(round(random.uniform(0.2, 1.0), 1))

def random_user_agent():
    user_agent_lists = [
        "Baiduspider",
        "Googlebot",
        "360spider",
        "Sogou web spider",
        "bingbot",
        "YisouSpider",
        "smspider",
        "HaosouSpider"
    ]
    return user_agent_lists[random.randint(0,len(user_agent_lists)-1)]

def get_start_time(time_interval:str, time_end:datetime,start:datetime) -> datetime:
    """获取开始时间

    Args:
        time_interval (str): 时间间隔
        time_end (datetime): 结束时间

    Returns:
        datetime: 开始时间
    """
    if time_interval == "year":
        time_start =  time_end - timedelta(days=365)
    if time_interval == "month":
        time_start =  time_end - timedelta(days=30)
    if time_interval == "week":
        time_start =  time_end - timedelta(days=7)
    if time_interval == "day":
        time_start =  time_end - timedelta(days=1)
    if time_interval == "hour":
        time_start =  time_end - timedelta(hours=1)
    time_start = max(time_start, start)
    return time_start

class TopicPostsDownloader(BaseCrawler):
    """
        获取话题的帖子
    """
    def __init__(self,search_for:str, concurrency:int = 100):
        table_name = "东部战区" # 处理数据表名称
        super().__init__(table_name = table_name, concurrency=concurrency)

        self.search_for = search_for

    
    async def _get_request_params(self,client,time_start:Optional[datetime] = None, time_end:Optional[datetime] = None) -> list:
        """获取请求参数列表
        
        Returns:
            list: 请求参数列表(字典列表)
        """
        base_url = "https://s.weibo.com/weibo"
        params = {
            "q": self.search_for,
            "suball": "1",
            "Refer": "g",
            "page": 1,
            "typeall": "1",
        }
        time_start = time_start.strftime("%Y-%m-%d-%H") if time_start else ""
        time_end = time_end.strftime("%Y-%m-%d-%H") if time_end else ""
        params["timescope"] = f"custom:{time_start}:{time_end}"
        headers = request_headers.body_headers
        headers["user-agent"] = random_user_agent()
        url = httpx.URL(url = base_url, params=params)

        response = await client.get(url, headers=headers)
        if self._check_response(response):
            page_num = get_page_num(response.text)
            if page_num == 0:
                return []
            else:
                return list(range(1, page_num + 1))
        return []
    
    async def get_request(self, client:httpx.Response,param: Any,time_start:Optional[datetime] = None, time_end:Optional[datetime] = None) -> httpx.Response:
        base_url = "https://s.weibo.com/weibo"
        params = {
            "q": self.search_for,
            "suball": "1",
            "Refer": "g",
            "page": param,
            "typeall": "1",
        }
        time_start = time_start.strftime("%Y-%m-%d-%H") if time_start else ""
        time_end = time_end.strftime("%Y-%m-%d-%H") if time_end else ""
        params["timescope"] = f"custom:{time_start}:{time_end}"
        headers = request_headers.body_headers

        if params["page"] > 1 :
            refer_params = deepcopy(params)
            refer_params["page"] = params["page"] - 1
            headers["Referer"] = str(httpx.URL(base_url, params=refer_params))

        url = httpx.URL(url = base_url, params=params)

        response = await client.get(url, headers=headers)
        print(f"获取第{param}页")
        return response
    
    async def _process_response_asyncio(self, response: httpx.Response, *, param: Any) -> None:
        """处理请求并存储数据

        Args:
            response (httpx.Response): 需要处理的请求
            param (Any): 请求参数
        """
        items = await parse_list_html(response.text)
        await self._save_to_database_asyncio(items= items)
        

    async def _download_single_asyncio(self, *, param:Any, client:httpx.Response,time_start: Optional[datetime] = None, time_end:Optional[datetime]=None):
        try:
            response = await self.get_request(client=client, param=param, time_start=time_start, time_end=time_end)
            if self._check_response(response):
                await self._process_response_asyncio(response=response, param=param)
        except Exception as e:
            print(f"第{param}页：{e}")

    async def _download_asyncio(self,time_start:Optional[datetime] = None, time_end:Optional[datetime] = None,skip = True) -> int:
        """异步下载

        Args:
            time_start (Optional[datetime], optional): 开始时间. Defaults to None.
            time_end (Optional[datetime], optional): 结束时间. Defaults to None
            skip (bool, optional): 如果页面过多，是否跳过. Defaults to False.

        Returns:
            int: 0 表示没有数据
            int: 1 表示正常
            int: 2 表示页面过多
        """
        async with httpx.AsyncClient(cookies = cookies_config.cookies,timeout = 20.0 ) as client:
            params = await self._get_request_params(client=client,time_start=time_start, time_end=time_end)
            print(f"{time_start} - {time_end} : {len(params)}")
            if params == []:
                return 0
            if len(params) >= 50 and skip:
                return 2
            tasks = []
            for param in params:
                async with self.semaphore:
                    task = self._download_single_asyncio(param=param, client=client,time_start=time_start, time_end=time_end)
                    tasks.append(task)
                    # await asyncio.sleep(round(random.uniform(0.1, 0.5), 2))
            await asyncio.gather(*tasks)
        return 1

    async def _download_all_asyncio(self):
        """下载所有
            Attention: 暂定大致两年内数据
        """
        now = datetime.now()
        if now.minute != 0 or now.second != 0 or now.microsecond != 0:
            now += timedelta(hours=1)
            now = now.replace(minute=0, second=0, microsecond=0)
        start = now - timedelta(days=365)
        print(f"{start}")
        time_end = now
        time_interval = ["year","month","day","hour"]
        flag = await self._download_asyncio()
        interval_index = 0

        if flag == 2:
            time_start = get_start_time(time_interval[interval_index], time_end,start)
            print(f"更改开始时间：{time_start},{time_end},{time_interval[interval_index]}")
            while(time_start != time_end):
                flag = await self._download_asyncio(time_start=time_start, time_end=time_end)
                if flag != 2 and interval_index > 0:
                    interval_index -= 1
                while(flag == 2 and interval_index < len(time_interval)):
                    time_start = get_start_time(time_interval[interval_index], time_end,start)
                    print(f"更改开始时间：{time_start},{time_end},{time_interval[interval_index]}")
                    flag = await self._download_asyncio(time_start=time_start, time_end=time_end)
                    interval_index += 1
                if flag == 2:
                    await self._download_asyncio(time_start=time_start, time_end=time_end,skip=False)
                interval_index = min(interval_index, len(time_interval) - 1)
                time_end = time_start
                time_start = get_start_time(time_interval[interval_index], time_end,start)
                print(f"更改开始时间-结束时间：{time_start}-{time_end},{time_interval[interval_index]}")



def get_topic_posts(search_for:str):
    downloader = TopicPostsDownloader(search_for=search_for)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(downloader._download_all_asyncio())
    except RuntimeError:
        asyncio.run(downloader._download_all_asyncio())
