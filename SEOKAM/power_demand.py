import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import requests
import pandas as pd
from bs4 import BeautifulSoup

plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

# 공휴일 크롤링
holiday_list = []
for year in range(2022, 2025):
    url = f'https://www.month2k.com/dates/holidays/{year}'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.select('table')   # 모든 테이블 가져오기
    table = tables[0]               # 그중 첫번째 테이블
    trs = table.select('tbody tr')
    for tr in trs:
        time_tag = tr.select_one('time')
        date = time_tag['datetime']
        cells = tr.select('td')
        name = cells[1].get_text().strip()
        holiday_list.append({'날짜':date, '명칭': name})

holidays = pd.DataFrame(holiday_list)
holidays['날짜'] = pd.to_datetime(holidays['날짜'])
#print(holidays.shape)
#print(holidays)

df_2022 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20221231.csv', encoding='cp949')
df_2023 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20231231.csv', encoding='cp949')
df_2024 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20241231.csv', encoding='cp949')

# 2022년
df_2022['날짜'] = pd.to_datetime(df_2022['날짜']) # 날짜를 타입 datetime 바꾸기

# 2023년
df_2023['날짜'] = pd.to_datetime(df_2023['날짜'])

# 2024년
df_2024['날짜'] = pd.to_datetime(df_2024['날짜'])

# 가설1 시작 (1. 평일 수요는 오전과 저녁에 두 번 높아지고 점심 무렵 잠시 낮아질 것이다.)
# 합치기
df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)
df['날짜'] = pd.to_datetime(df['날짜'])
df = df.merge(holidays, on='날짜', how='left')

# 주일, 주말+공휴일 나누기 (22,23,24년)
is_weekday = (df['날짜'].dt.day_of_week < 5) & (df['명칭'].isnull()) # 주일만 + 명칭이 null값만
weekday = df[is_weekday] # 22,23,24 주일
holiday= df[~is_weekday] # 22, 23, 24 쉬는날
#print(weekday, holiday)

# 1~24시 까지 전력사용량의 평균값 구하기 (22,23,24년)
hours = [f'{i}시' for i in range(1, 25)]
hour_mean = weekday[hours].mean()
#print(hour_mean)

# 가설1 선 그래프
plt.plot(range(1,25), hour_mean.values, marker='o')
plt.title('평일 시간대별 평균 전력 수요(2022~2024)')
plt.xlabel('시간')
plt.ylabel('평균 전력 수요(MWh)')
plt.xticks(range(1,25))
plt.show()

# 가설2 시작 (2. 평일 주간(9~18시)의 평균 전력 수요는 주말 동일 시간대보다 10% 이상 높을 것이다.)
day_hours = [f'{i}시' for i in range(9,19)]

weekday_mean = weekday[day_hours].mean() # 평일 9시부터 18시까지 시간별 평균
weekday_all_mean = weekday_mean[day_hours].mean() # 9시부터 18시 전체 평균
holidays_mean = holiday[day_hours].mean() # 공휴일 9시부터 18시까지 시간별 평균
holidays_all_mean = holidays_mean[day_hours].mean() # 9시부터 18시 전체 평균
#print(weekday_mean, holidays_mean)

# 가설2 막대그래프
bars = plt.bar(['평일','주말,공휴일'], [weekday_all_mean, holidays_all_mean])
plt.bar_label(bars, fmt='%.0f')
plt.title('9~18시 평균 전력 수요 비교 (2022~2024)')
plt.xlabel('구분')
plt.ylabel('평균 전력 수요 (MWh)')
plt.show()

# *] 추가 그래프 -> 주일과 쉬는날 시간대별 평균 수요량
plt.plot(range(9, 19), weekday_mean.values, marker='o', label='평일')
plt.plot(range(9, 19), holidays_mean.values, marker='o', label='주말,공휴일')
plt.title('평일과 주말,공휴일의 9~18시간대별 평균 전력 수요 (2022~2024)')
plt.xlabel('시간')
plt.ylabel('평균 전력 수요 (MWh)')
plt.xticks(range(9,19))
plt.legend()
plt.tight_layout()
plt.show()