from pydantic import BaseModel

class RequestHeaders(BaseModel):
    """这个类主要用来保存一些请求参数的东西

    Attributes:
        body_headers (dict): 微博主页的请求头
        comment1_buildComments_headers (dict): 评论区buildComments的请求头
        comment1_rum_headers (dict): 评论区rum的请求头
        ....
    """
    list_headers: dict
    body_headers: dict
    comment1_buildComments_headers: dict
    comment1_rum_headers: dict
    comment2_buildComments_headers: dict
    comment2_rum_headers: dict
    login_signin_headers:dict
    login_qrcode_headers:dict
    login_final_headers:dict