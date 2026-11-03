import numpy as np
import pandas as pd

df_life = pd.read_csv('삶의_만족도.csv', encoding='cp949')
df_overdep = pd.read_csv('스마트폰_과의존위험군.csv', encoding='cp949')
df_content = pd.read_csv('콘텐츠_이용률.csv', encoding='cp949')

print(df_life.info())

print(df_life.head())
