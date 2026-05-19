import re

def clean(text):
            text = re.sub(r'http\S+', '', text)
            text = re.sub(r'@\w+', '', text)
            text = re.sub(r'#\w+', '', text)
            text = text.replace('\u2019', "'")   
            text = text.replace('\u2018', "'")
            text = re.sub(r'\s+', ' ', text)
            return text.strip()