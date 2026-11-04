import numpy as np
import pandas as pd

raw_life = pd.read_csv('삶의_만족도.csv', encoding='cp949', header=None)
raw_suicide = pd.read_csv('사망원인별_사망.csv', encoding='cp949', header=None)
raw_contents = pd.read_csv('콘텐츠_이용률.csv', encoding='cp949', header=None)

# 1. 삶의만족도 전처리
life_avg = raw_life.iloc[:, 13::12]
life = life_avg.iloc[2]
# 년도별 만족도 데이터프레임
df_life = pd.DataFrame({'연도': life_avg.iloc[0], '만족도': life})
print(df_life)

# 2. 자살률 전처리
suicide = raw_suicide.iloc[42: ,4::2]
years = raw_suicide.iloc[0, 4::2]
df_suicide = pd.DataFrame({'연도': years, '10_14_사망률': suicide.iloc[0], '15_19_사망률':suicide.iloc[1]})
print(df_suicide)

# 3. 콘텐츠이용률 전처리
years = raw_contents.iloc[0]               # 연도 줄
items = raw_contents.iloc[1].str.strip()   # 항목 줄

cond = (items == 'SNS') & (years != '2016') # SNS 항목과 2016년 빼고 다
sns = raw_contents.iloc[10, cond]

df_sns = pd.DataFrame({'연도': years[cond], 'SNS이용률': sns})
print(df_sns)