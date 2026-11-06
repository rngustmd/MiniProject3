import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import requests
import pandas as pd

df_2022 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20221231.csv', encoding='cp949')
df_2023 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20231231.csv', encoding='cp949')
df_2024 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20241231.csv', encoding='cp949')

# 2022년 평일 시간대별 평균 수요량
df_2022['날짜'] = pd.to_datetime(df_2022['날짜']) # 날짜를 타입 datetime 바꾸기
weekday_2022 = df_2022[df_2022['날짜'].dt.dayofweek < 5] # 월~금요일 행 남기기
hours_2022 = [f'{i}시' for i in range(1, 25)] # ['1시', '2시', '3시', ..., '24시']
hourly_mean_2022 = weekday_2022[hours_2022].mean()
print(hourly_mean_2022)

# 2023년 평일 시간대별 평균 수요량
df_2023['날짜'] = pd.to_datetime(df_2023['날짜'])
weekday_2023 = df_2023[df_2023['날짜'].dt.dayofweek < 5]



# 2024년 평일 시간대별 평균 수요량