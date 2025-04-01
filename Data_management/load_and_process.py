import process_simple_text as pst
import process_complex_text as pct
import get_item_mongodb as get_item

item_list, batch_size = get_item.get_items()
emotion_count = {}
location_count = {} 
for i, item in enumerate(item_list):
    emotion_max_index = pct.get_emotion(item['content_all'])['scores'].index(max(pct.get_emotion(item['content_all'])['scores']))
    emotion_max = pct.get_emotion(item['content_all'])['labels'][emotion_max_index]
    print(f"第 {i+1} 条文档：", item['content_all'],'\n',emotion_max,'\n')
    #print(f"第 {i+1} 条文档：", item['content_all'],'\n',pct.get_emotion(item['content_all']),'\n')
    emotion_count[emotion_max] = emotion_count.get(emotion_max, 0) + 1
    location_count[item['location']] = location_count.get(item['location'], 0) + 1

print(emotion_count)
print(location_count)