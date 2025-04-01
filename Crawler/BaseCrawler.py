import sys
sys.path.append("")

import asyncio
from abc import ABC, abstractmethod
import httpx
from pydantic import BaseModel
from typing import Any
import json
from .database import insert_one
from Front_end.config_front import cookies_config

class CommentID(BaseModel):
    uid: str
    mid: str

class CommmentResponseInfo(BaseModel):
    max_id: str
    total_number: int
    data_number: int

class BaseCrawler(ABC):
    def __init__(self,table_name:str,concurrency:int = 20):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.db = None # 数据库操作
        self.table_name = table_name # 表名


    @abstractmethod
    async def _get_request_params(self,client) -> list:
        """获取请求参数列表

        Returns:
            list: 请求参数列表
            client (httpx.Client): 会话客户端
        """
        ...

    @abstractmethod
    async def get_request(self, client:httpx.Response,param: Any) -> httpx.Response:
        """获取请求

        Args:
            client (httpx.Response): 请求客户端
            param (Any): 请求参数
        """
        ...

    @abstractmethod
    async def _process_response_asyncio(self, response: httpx.Response, *, param: Any) -> None:
        """处理请求并存储数据

        Args:
            response (httpx.Response): 需要处理的请求
            param (Any): 请求参数
        """
        ...


    @abstractmethod
    async def _download_single_asyncio(self, *, param:Any, client:httpx.Response):
        """下载单个请求(异步)

        Args:
            param (Any): 请求参数
            client (httpx.Response): 请求客户端
        """
        ...

    async def _save_to_database_asyncio(self, items:Any) -> None:
        """保存数据到数据库
        """
        for item in items:
            document = json.dumps(item)
            document = json.loads(document)
            insert_one(self.table_name,document)
        

    def _check_response(self, response: httpx.Response) -> bool:
        """检查响应是否正常

        Args:
            response (httpx.Response): 接受到的响应

        Returns:
            bool: 有问题返回 False, 否则返回 True
        """
        return response.status_code == httpx.codes.OK
    
    async def _download_asyncio(self):
        """异步下载
        """
        async with httpx.AsyncClient(cookies = cookies_config.cookies) as client:
            params = await self._get_request_params(client=client)
            tasks = []
            for param in params:
                async with self.semaphore:
                    task = self._download_single_asyncio(param=param, client=client)
                    tasks.append(task)
            await asyncio.gather(*tasks)

__all__ = [BaseCrawler]