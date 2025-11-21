# import os
# import json
# import re
# import pandas as pd
# from wordcloud import WordCloud
# import matplotlib
# matplotlib.use('Agg') # 使用非GUI后端，适合Web服务
# import matplotlib.pyplot as plt
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
# import whisper

# model = whisper.load_model("base")

# def transcribe_audio(path):
#     return model.transcribe(path)['text']

# def recommend_by_topic(df, transcript):
#     scores = {}
#     for i, row in df.iterrows():
#         kws = eval(row['keywords'])
#         score = sum(k.lower() in transcript.lower() for k in kws)
#         scores[row['topic_name']] = scores.get(row['topic_name'], 0) + score

#     best = max(scores, key=scores.get)
#     recs = df[df['topic_name'] == best].drop_duplicates('file_name').head(5)
#     return best, [{'file': r['file_name'], 'year': r['year']} for _, r in recs.iterrows()]

import os
import json
import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import whisper

model = whisper.load_model("base")

def transcribe_audio(path):
    return model.transcribe(path)['text']

def recommend_by_topic(df, transcript):
    scores = {}
    for i, row in df.iterrows():
        kws = eval(row['keywords'])
        score = sum(k.lower() in transcript.lower() for k in kws)
        scores[row['topic_name']] = scores.get(row['topic_name'], 0) + score

    best = max(scores, key=scores.get)
    recs = df[df['topic_name'] == best].drop_duplicates('file_name').head(5)
    return best, [{'file': r['file_name'], 'year': r['year'], 'speaker_url': f"https://www.ted.com/speakers/{camel_to_snake(r['file_name'].split('_')[0])}"} for _, r in recs.iterrows()]

def camel_to_snake(name):
    parts = re.findall(r'[A-Z][a-z]*', name)
    return '_'.join(p.lower() for p in parts)
