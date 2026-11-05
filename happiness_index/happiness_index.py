import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False


raw_life = pd.read_csv('삶의_만족도.csv', encoding='cp949', header=None)
raw_suicide = pd.read_csv('사망원인별_사망.csv', encoding='cp949', header=None)
raw_contents = pd.read_csv('콘텐츠_이용률.csv', encoding='cp949', header=None)
raw_depress = pd.read_csv('우울감_경험률.csv', encoding='cp949', header=None)

# 1. 삶의만족도 전처리
life_avg = raw_life.iloc[:, 13::12]
life = life_avg.iloc[2]
# 년도별 만족도 데이터프레임
df_life = pd.DataFrame({'연도': life_avg.iloc[0].astype(int).values, '만족도': life.astype(float).values})
#print(df_life)

# 2. 콘텐츠이용률 전처리
contents_years = raw_contents.iloc[0]               # 연도 줄
items = raw_contents.iloc[1].str.strip()   # 항목 줄

cond = (items == 'SNS') & (contents_years != '2016') # SNS 항목과 2016년 빼고 다
sns = raw_contents.iloc[10, cond.values]

df_sns = pd.DataFrame({'연도': contents_years[cond].astype(int).values, 'SNS이용률': sns.astype(float).values})
#print(df_sns)

# 3. 우울감 경험률 전처리
depress = raw_depress.iloc[2, 4::3]
depress_years = raw_depress.iloc[0, 4::3]
df_depress = pd.DataFrame({'연도': depress_years.astype(int).values, '우울감경험률': depress.astype(float).values})
#print(df_depress)


# 가설1 : merge하기
df_sns_life = pd.merge(df_sns, df_life, on='연도', how='inner')
df_total = pd.merge(df_sns_life, df_depress, on='연도', how='inner')
print(df_total)

# 시각화

# 정규화 공식
def minmax(x):
    return (x - x.min()) / (x.max() - x.min())

# SNS이용률과 삶의 만족도
plt.plot(df_total['연도'], minmax(df_total['SNS이용률']), marker='o', label='SNS 이용률')
plt.plot(df_total['연도'], minmax(df_total['만족도']), marker='o', label='삶의 만족도')
plt.title('청소년 SNS 이용률과 삶의 만족도 추세 (2017~2025)')
plt.xlabel('연도')
plt.ylabel('정규화 값 (0~1)')
plt.legend()
plt.show()

# SNS이용률과 우울증
plt.plot(df_total['연도'], minmax(df_total['SNS이용률']), marker='o', label='SNS 이용률')
plt.plot(df_total['연도'], minmax(df_total['우울감경험률']), marker='o', label='우울감 경험률')
plt.title('청소년 SNS 이용률과 우울감 경험률 (2017~2025)')
plt.xlabel('연도')
plt.ylabel('정규화 값 (0~1)')
plt.legend()
plt.show()

