import sys
sys.path.append("")

import httpx
import asyncio
from datetime import datetime,timedelta
from typing import Literal, Optional, Any, Union, List
from copy import deepcopy
import json
import random

from .BaseCrawler import BaseCrawler,CommentID
from Front_end.config_front import cookies_config, request_headers

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

class PostCommandDownloader(BaseCrawler):
    """
        获取帖子的评论
    """
    def __init__(self, uid: Union[List[str], str], mid: Union[List[str], str], concurrency = 100,max_failed_times: int = 20):
        table_name = "test_command"
        super().__init__(table_name, concurrency)
        if isinstance(uid, str) and isinstance(mid, str):
            self.ids = [CommentID(uid=uid, mid=mid)]
        elif isinstance(uid, list) and isinstance(mid, list) and len(uid) == len(mid):
            self.ids = [CommentID(uid=u, mid=m) for u, m in zip(uid, mid)]
        else:
            raise ValueError("uid and mid must be both str or list and the length of uid and mid must be equal")
        self.max_failed_times = max_failed_times

    async def _get_request_params(self, client) -> list:
        """获取请求参数列表

        Returns:
            list: 请求参数列表
        """
        return self.ids
    
    async def get_request(uid: str, mid : str, *, client: httpx.AsyncClient, max_id: Optional[str]=None) -> httpx.Response:
        """获取请求

        Args:
            uid (str): 用户id
            mid (str): 微博id
            client (httpx.Response): 请求客户端
            param (Any): 请求参数
        """
        base_url = "https://weibo.com/ajax/statuses/buildComments"
        headers = request_headers.comment1_buildComments_headers
        headers["user-agent"] = random_user_agent()
        params = {
            "is_reload": "1",
            "id": f"{mid}",
            "is_show_bulletin": "2",
            "is_mix": "0",
            "count": "20",
            "uid": f"{uid}",
            "fetch_level": "0",
            "locale": "zh-CN",
        }
        if max_id is not None:
            params["flow"] = "0"
            params["max_id"] = max_id
        response = await client.get(base_url, params=params, headers=headers)
        return response

    async def _process_response_asyncio(self, response: httpx.Response, *, param: Any) -> None:
        """处理请求并存储数据

        Args:
            response (httpx.Response): 需要处理的请求
            param (Any): 请求参数
        """
        data = response.json()
        max_id = data.get("max_id", "")
        total_number = data.get("total_number", 0)
        data_number = len(data.get("data", []))
        data_list = data["data"]
        transform_dict = {
            "mid": "mid",
            "uid": ["user", "idstr"],
        }

    async def _download_single_asyncio(self, *, param:Any, client:httpx.Response):
        """下载单个请求(异步)

        Args:
            param (Any): 请求参数
            client (httpx.Response): 请求客户端
        """
        response = await self.get_request(param.uid, param.mid, client=client)
        if self._check_response(response):
            pass