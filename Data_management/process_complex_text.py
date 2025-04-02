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
    return semantic_cls(input=text)

