import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv("./문해력/2019_청소년_SNS_문해력_가설분석용_한글컬럼.csv")
print(df.shape)
df.info()
print(df.head(5))

# 1. 필요 컬럼은 원본에서 추출후 따로 csv 파일 생성하여 저장
# 2. 결측값 탐색 및 처리
# 컬럼별 결측값 개수 및 비율 
missing_summary = pd.DataFrame( {"결측값 개수": df.isna().sum(), "결측 비율(%)": (df.isna().mean() * 100).round(2) } )
missing = missing_summary.sort_values("결측값 개수", ascending=False)
# 결측값 현황 저장
missing.to_csv("./문해력/전체_컬럼_결측현황.csv")

# 결측이 존재하는 컬럼만 시각화
missing_only = missing[missing['결측값 개수'] > 0]
plt.figure(figsize=(9,5))
plt.barh(missing_only.index, missing_only["결측 비율(%)"])
plt.title('컬럼별 결측 비율'); plt.xlabel('결측 비율(%)'); plt.ylabel('컬럼명')
plt.xlim(0,100); plt.tight_layout(); plt.show()

# 2-1. 결측값 발생 원인 분석
missing_cols = df.columns[df.isnull().any()] # true /false 통합적으로 있는지 없는 지 가상 통합 컬럼
print(missing_cols.to_list()) # 결측치 있는 컬럼명만 리스트로 

# SNS 이용 여부별 평일 이용 일수 결측 현황 
# 교차표 이용, margins=True(합계 행/열 추가)  # 1(이용) 2(미이용)
print(pd.crosstab( df['SNS이용여부'],df["SNS평일이용일수코드"].isnull(), margins=True, dropna=False ))

# SNS 이용 여부별 주말 이용 일수 결측 현황 # 1(이용) 2(미이용)
print(pd.crosstab(df['SNS이용여부'],df["SNS주말이용일수코드"].isnull(), margins=True, dropna=False))
# ==> SNS 이용자 1,573명은 모두 이용 일수에 응답, SNS 비이용자 790명은 모두 이용 일수가 공란. 평일과 주말 일치
# => SNS 이용 일수의 공란 790개는 SNS 비이용으로 인한 구조적 결측으로 판단 => 비용자는 0일로 처리 가능!

# SNS 이용 여부별 결측 현황 시각화 
# 평일 / 주말 결측 구조 동일 => 평일 기준으로 표시
sns_missing = pd.crosstab( df['SNS이용여부'],df["SNS평일이용일수코드"].isnull())
sns_missing = sns_missing.reindex(index=[1,2], columns=[False,True], fill_value=0)
sns_missing.index = ["SNS 이용자", "SNS 비이용자"]
sns_missing.columns = ["값 있음", "공란"]
sns_missing.plot(kind='bar', stacked=True, figsize=(7,5))
plt.title('SNS 이용 여부별 이용 일수 결측 현황'); plt.xlabel('SNS 이용 여부'); plt.ylabel('응답자 수')
plt.xticks(rotation=0); plt.tight_layout(); plt.show()

# 주요 뉴스 이용 결오 결측 현황 # 6=포털,7=언론사 사이트,8=SNS,9=메신저,10=동영상 플랫폼,11=AI 스피커
print(df['주요뉴스이용플랫폼코드'].value_counts(dropna=False))

# SNS 뉴스 이용 여부별 주요 뉴스 이용 경로 공란 # 1(이용) 2(미이용)
print( pd.crosstab(df['SNS뉴스이용여부'],df['주요뉴스이용플랫폼코드'].isnull(), margins=True,dropna=False))

# 학교급별 주요 뉴스 이용 경로 공란
print(pd.crosstab(df['학교급'],df['주요뉴스이용플랫폼코드'].isnull(),margins=True,dropna=False))


