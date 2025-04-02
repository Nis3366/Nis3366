import httpx

def get_top_lists() -> dict:
    """获取排行榜的数据

    1. 这里的 client 会话客户端是在外部创建的.
    2. 这里的 url 是写死的，不是从外部传入的.
    3. 这里的返回值是解析后的数据，而不是 response.
    """
    client = httpx.Client()
    result = get_top_lists_reponse(client)
    client.close()
    return result

def get_top_lists_reponse(client:httpx.Client) -> dict :
    """获取排行榜的数据

    Args:
        client (httpx.Client): 会话客户端
        url (str): 排行榜 url

    Returns:
        httpx.Response: 排行榜的 response
    """
    url = "https://www.weibo.com/ajax/side/hotSearch"
    response = client.get(url)
    result = parse_top_lists(response)
    return result


def parse_top_lists(response:httpx.Response):
    """解析排行榜的数据

    Args:
        response (httpx.Response): 排行榜的 response

    Returns:
        dict: 解析后的数据
    """
    data = response.json()
    result = {}
    realtime_data = data.get("data",{}).get("realtime",{})
    for item in realtime_data:
        if 'realpos' in item and 'word_scheme' in item:
            realpos = item["realpos"]
            word_scheme = item["word_scheme"]
            result[realpos] = word_scheme
    return result
