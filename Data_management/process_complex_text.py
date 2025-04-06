# 二郎神-RoBERTa-110M-情感分类，二分类
# from modelscope.pipelines import pipeline
# from modelscope.utils.constant import Tasks

# p = pipeline(Tasks.text_classification, 'Fengshenbang/Erlangshen-RoBERTa-110M-Sentiment')
# print(p(input='今天心情不好'))


#StructBERT情绪分类-中文-七分类-base

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

semantic_cls = pipeline(Tasks.text_classification, 'iic/nlp_structbert_emotion-classification_chinese-base', model_revision='v1.0.0')

def get_emotion(text):
    emotion_result = semantic_cls(input=text)
    emotion_max_index = emotion_result['scores'].index(max(emotion_result['scores']))
    emotion_max = emotion_result['labels'][emotion_max_index]
    print(f"情感分类结果: {emotion_result}"
          f"情感分类结果: {emotion_max}")
    return emotion_max
