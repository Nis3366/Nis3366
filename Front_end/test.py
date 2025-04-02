import sys 
sys.path.append("") 
from Crawler import get_top_lists, get_topic_posts

if __name__ == "__main__":
    top_lists = get_top_lists()
    top_one = top_lists.get(2)
    get_topic_posts(search_for="愚人节")