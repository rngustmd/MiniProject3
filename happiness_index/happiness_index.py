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

# 2. 자살률 전처리
suicide = raw_suicide.iloc[42: ,4::2]
suicide_years = raw_suicide.iloc[0, 4::2]
df_suicide = pd.DataFrame({'연도': suicide_years.astype(int).values,
                           '10_14_사망률': suicide.iloc[0].astype(float).values,
                           '15_19_사망률':suicide.iloc[1].astype(float).values})
#print(df_suicide)

# 3. 콘텐츠이용률 전처리
contents_years = raw_contents.iloc[0]               # 연도 줄
items = raw_contents.iloc[1].str.strip()   # 항목 줄

cond = (items == 'SNS') & (contents_years != '2016') # SNS 항목과 2016년 빼고 다
sns = raw_contents.iloc[10, cond]

df_sns = pd.DataFrame({'연도': contents_years[cond].astype(int).values, 'SNS이용률': sns.astype(float).values})
#print(df_sns)

# 4. 우울감 경험률 전처리
depress = raw_depress.iloc[2, 4::3]
depress_years = raw_depress.iloc[0, 4::3]
pd.DataFrame({'연도':depress_years.astype(int).values, '우울감경험률':depress.astype(float).values})
print(depress)


# merge하기
df_sns_life = pd.merge(df_sns, df_life, on='연도', how='inner')
df_total = pd.merge(df_sns_life, df_suicide, on='연도', how='inner')
print(df_total)

# 시각화
fig, axs = plt.subplots(2, 1, figsize=(10, 8))

axs[0].plot(df_total['연도'], df_total['SNS이용률'])
axs[0].set_title('청소년 SNS 이용률')
axs[0].set_ylabel('이용률 (%)')
axs[0].set_xlabel('연도')

axs[1].plot(df_total['연도'], df_total['만족도'])
axs[1].set_title('청소년 삶의 만족도')
axs[1].set_ylabel('점수(0~10)점')
axs[1].set_xlabel('연도')
plt.show()

plt.scatter(df_total['SNS이용률'], df_total['만족도'])
plt.title('SNS 이용률과 삶의 만족도')
plt.xlabel('SNS 이용률 (%)')
plt.ylabel('삶의 만족도')
plt.show()