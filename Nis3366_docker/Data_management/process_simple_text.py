from snownlp import SnowNLP

# 示例文本

class process_simple_text:
    def __init__(self, text):
        self.text = text
        self.s = SnowNLP(text)
    
    def get_words(self):
        return self.s.words
    
    def get_sentiment(self):
        return self.s.sentiments
