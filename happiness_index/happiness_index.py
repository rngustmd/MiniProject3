import numpy as np
import pandas as pd

df_overdep = pd.read_csv('.삶의_만족도.csv', encoding='utf-8-sig')
df_life = pd.read_csv('.스마트폰_과의존위험군.csv', encoding='utf-8-sig')
df_content = pd.read_csv('.콘텐츠_이용률.csv', encoding='utf-8-sig')
print(df_overdep.info())
print(df_life.info())
print(df_content.info())
