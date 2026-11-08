import pandas as pd

# [step1. 데이터 호출]
df22 = pd.read_csv("./weather/data/한국전력거래소_시간별 전국 전력수요량_20221231.csv",encoding="cp949")
df23 = pd.read_csv("./weather/data/한국전력거래소_시간별 전국 전력수요량_20231231.csv",encoding="cp949")
df24 = pd.read_csv("./weather/data/한국전력거래소_시간별 전국 전력수요량_20241231.csv",encoding="cp949")
df = pd.concat([df22, df23, df24],ignore_index=True)

# 데이터 구조 확인
print("\n컬럼명:")
print(df.columns.tolist())
print("\n상위 5개 행:")
print(df.head())
print("\n자료형:")
print(df.dtypes)
print("\n연도별 행 개수:")
print(df["날짜"].str[:4].value_counts().sort_index())
df.info()

# [STEP 2. 데이터 품질 확인 및 전처리]
# 전체 결측값 확인 --> 결측값 없음
print(df.isnull().sum())
print("전체 결측값:", df.isnull().sum().sum())

# 날짜 중복 확인 --> 중복된 날짜 없음.
print("중복 날짜:", df["날짜"].duplicated().sum())

# 날짜 컬럼을 datetime으로 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 변환 확인
print(df["날짜"].dtype)
print(df["날짜"].head())

# 날짜 기준 오름차순 정렬
df = df.sort_values("날짜").reset_index(drop=True)

# 시작일과 종료일 확인
print("시작일:", df["날짜"].min())
print("종료일:", df["날짜"].max())

# 컬럼 [1시 ~ 24시 ]
print(df.columns.tolist())

# 시간별 전력수요 컬럼 선택
hour_cols = [f"{i}시" for i in range(1, 25)]

# 기초통계량 확인
print(df[hour_cols].describe())

# 0 이하인 값 확인
print("0 이하인 값:",(df[hour_cols] <= 0).sum().sum())

# [STEP 3. 파생변수 생성]
# 월을 기준으로 계절 구분을 위해 날짜에서 연도, 월 추출
df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month
# 계절 구분 함수
def get_season(month):
    if month in [3, 4, 5]:
        return "봄"
    elif month in [6, 7, 8]:
        return "여름"
    elif month in [9, 10, 11]:
        return "가을"
    else:
        return "겨울"
# 계절 컬럼 생성
df["계절"] = df["월"].apply(get_season) # apply() : 특저열 모든행 데이터에 함수 일괄적용
print(df[["날짜", "연도", "월", "계절"]].head())
print(df["계절"].value_counts())

# 일별 최대 / 최저 전력 수요 계산
hour_cols = [f"{i}시" for i in range(1, 25)] # 시간별 전력수요 컬럼
df["일최대수요"] = df[hour_cols].max(axis=1) # 일별 최대 전력수요
df["일최저수요"] = df[hour_cols].min(axis=1) # 일별 최저 전력수요
df["일평균수요"] = df[hour_cols].mean(axis=1) # 일평균 전력수요 

# 일중 부하 변동 폭 계산 , 일중 부하 변동 폭 = 일최대수요-일최저수요
df["일중변동폭"] = df["일최대수요"] - df["일최저수요"]
# 필요한 컬럼만 출력
result_cols = [
    "날짜", "연도", "월", "계절",
    "일최대수요", "일최저수요",
    "일평균수요", "일중변동폭"
]
print(df[result_cols].head(10))
print(df[result_cols].isnull().sum()) # 파생변수 결측값 확인
print("음수 변동 폭:", (df["일중변동폭"] < 0).sum()) # 일중변동폭이 음수인 경우 확인

# [STEP 4. 탐색적 데이터 분석(EDA)]
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
season_order = ["봄", "여름", "가을", "겨울"]

# 일별 최대 전력 수요 시계열 그래프
plt.figure(figsize=(14, 5))
plt.plot(df["날짜"],df["일최대수요"],linewidth=0.9,label="일별 최대 전력 수요")
plt.title("2022~2024년 일별 최대 전력 수요 추이")
plt.xlabel("날짜")
plt.ylabel("일별 최대 전력 수요")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# 월별 평균 일 최대 전력 수요
monthly_peak = (df.groupby("월")["일최대수요"].mean().reindex(range(1, 13)))
print("월별 평균 일 최대 전력 수요")
print(monthly_peak.round(2))
# 월별 평균 그래프
plt.figure(figsize=(10, 5))
plt.plot(monthly_peak.index, monthly_peak.values, marker="o", linewidth=2,label="월별 평균 최대 수요")
plt.xticks(range(1, 13),[f"{i}월" for i in range(1, 13)])
plt.title("2022~2024년 월별 평균 일 최대 전력 수요")
plt.xlabel("월")
plt.ylabel("평균 일 최대 전력 수요")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# [계절별 일 최대 전력 수요 비교 — H1]
# 계절별 일 최대 전력 수요 기초통계
season_peak = (df.groupby("계절")["일최대수요"].agg(["mean", "std", "min", "max"]).reindex(season_order))
season_peak.columns = ["평균", "표준편차", "최솟값", "최댓값"] # 컬럼명 한글로 변경
print("계절별 일 최대 전력 수요 기초통계")
print(season_peak.round(2))

# 계절별 박스플롯
peak_data = [df.loc[df["계절"] == season, "일최대수요"]for season in season_order]
plt.figure(figsize=(9, 5))
plt.boxplot(peak_data,tick_labels=season_order)
plt.title("계절별 일 최대 전력 수요 분포")
plt.xlabel("계절")
plt.ylabel("일 최대 전력 수요")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# 계절별 평균 비교 막대그래프
# 계절별 평균 일 최대 수요
season_peak_mean = (df.groupby("계절")["일최대수요"].mean().reindex(season_order))
plt.figure(figsize=(9, 5))
bars = plt.bar(season_peak_mean.index,season_peak_mean.values)
plt.title("계절별 평균 일 최대 전력 수요 비교")
plt.xlabel("계절")
plt.ylabel("평균 일 최대 전력 수요")
plt.bar_label(bars,fmt="%.0f",padding=3)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# [계절별 일중 부하 변동 폭 비교 — H2]
# 계절별 일중 부하 변동 폭 기초통계
season_range = (df.groupby("계절")["일중변동폭"].agg(["mean", "std", "min", "max"]).reindex(season_order))
season_range.columns = ["평균", "표준편차", "최솟값", "최댓값"] # 컬럼명 한글로 변경
print("계절별 일중 부하 변동 폭 기초통계")
print(season_range.round(2))

# 계절별 일중 부하 변동 폭 데이터
range_data = [df.loc[df["계절"] == season, "일중변동폭"]for season in season_order]
plt.figure(figsize=(9, 5))
plt.boxplot(range_data,tick_labels=season_order)
plt.title("계절별 일중 부하 변동 폭 분포")
plt.xlabel("계절")
plt.ylabel("일중 부하 변동 폭")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# 계절별 평균 일중 부하 변동 폭
season_range_mean = (df.groupby("계절")["일중변동폭"].mean().reindex(season_order))
plt.figure(figsize=(9, 5))
bars = plt.bar(season_range_mean.index, season_range_mean.values)
plt.title("계절별 평균 일중 부하 변동 폭 비교")
plt.xlabel("계절")
plt.ylabel("평균 일중 부하 변동 폭")
plt.bar_label(bars,fmt="%.0f",padding=3)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# [STEP 5. H1 가설 검증]
# H1. 여름철(6~8월)과 겨울철(12~2월)의 일별 최대 전력 수요 평균은 봄·가을(3~5월, 9~11월)보다 높을 것이다.
# H1 비교 집단 생성
summer = df.loc[df["계절"] == "여름", "일최대수요"]
winter = df.loc[df["계절"] == "겨울", "일최대수요"]
spring_fall = df.loc[df["계절"].isin(["봄", "가을"]),"일최대수요"]
print("여름:", len(summer))
print("겨울:", len(winter))
print("봄·가을:", len(spring_fall))

# 각 집단의 평균
summer_mean = summer.mean()
winter_mean = winter.mean()
spring_fall_mean = spring_fall.mean()

# 평균 차이
summer_diff = summer_mean - spring_fall_mean
winter_diff = winter_mean - spring_fall_mean

# 평균 차이율
summer_rate = (summer_diff / spring_fall_mean) * 100
winter_rate = (winter_diff / spring_fall_mean) * 100

print("=== H1 평균 비교 결과 ===")
print(f"여름 평균: {summer_mean:,.2f}")
print(f"겨울 평균: {winter_mean:,.2f}")
print(f"봄·가을 평균: {spring_fall_mean:,.2f}")

print(f"\n여름 평균 차이: {summer_diff:,.2f}")
print(f"여름 증가율: {summer_rate:.2f}%")

print(f"\n겨울 평균 차이: {winter_diff:,.2f}")
print(f"겨울 증가율: {winter_rate:.2f}%")

# 통계적 유의성 검정
from scipy.stats import ttest_ind  # 두 집단의 분산이 다를때
# 단측 검정: 여름 > 봄·가을
summer_test = ttest_ind(summer,spring_fall,equal_var=False,alternative="greater")
# 단측 검정: 겨울 > 봄·가을
winter_test = ttest_ind(winter,spring_fall,equal_var=False,alternative="greater")
print("=== H1 통계검정 결과 ===")
print(f"여름 t통계량: {summer_test.statistic:.4f}")
print(f"여름 p-value: {summer_test.pvalue:.6f}")
print(f"\n겨울 t통계량: {winter_test.statistic:.4f}")
print(f"겨울 p-value: {winter_test.pvalue:.6f}")

groups = ["여름", "겨울", "봄·가을"]
means = [summer_mean, winter_mean, spring_fall_mean]
plt.figure(figsize=(9, 5))
bars = plt.bar(groups, means)
plt.bar_label(bars,fmt="%.0f",padding=3)
plt.title("H1 검증: 계절별 평균 일 최대 전력 수요 비교")
plt.xlabel("비교 집단")
plt.ylabel("평균 일 최대 전력 수요")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# [STEP 6. H2 가설 검증]
# H2. 여름철(6~8월)의 일중 부하 변동 폭(일별 최대 수요 − 최저 수요)은 봄·가을보다 평균 10% 이상 클 것이다.
# H2 비교 집단 생성
summer_range = df.loc[df["계절"] == "여름", "일중변동폭"]
spring_fall_range = df.loc[df["계절"].isin(["봄", "가을"]), "일중변동폭"]
print("여름 관측 일수:", len(summer_range))
print("봄·가을 관측 일수:", len(spring_fall_range))

# 평균 변동 폭 및 증가율 계산 
# 증가율 = (여름평균 변동 폭 - 봄가을 평균 변동폭)/봄가을 평균변동 폭 *100
# 평균 변동 폭 계산
summer_range_mean = summer_range.mean()
spring_fall_range_mean = spring_fall_range.mean()
range_diff = summer_range_mean - spring_fall_range_mean # 평균 차이 및 증가율
range_rate = (range_diff / spring_fall_range_mean) * 100
print("=== H2 평균 비교 결과 ===")
print(f"여름 평균 변동 폭: {summer_range_mean:,.2f}")
print(f"봄·가을 평균 변동 폭: {spring_fall_range_mean:,.2f}")
print(f"평균 차이: {range_diff:,.2f}")
print(f"여름 증가율: {range_rate:.2f}%")
if range_rate >= 10:
    print("관측된 평균 차이율이 10% 이상입니다.")
else:
    print("관측된 평균 차이율이 10% 미만입니다.")

# H2 통계검정
# 검정 가설: H0: mu_여름 <= 1.1 mu_봄가을, H1: mu_여름 > 1.1 mu_봄가을
import numpy as np
from scipy.stats import norm
# 여름 평균 - (봄·가을 평균 × 1.1)
adjusted_diff = (summer_range_mean - 1.1 * spring_fall_range_mean)
# 평균 차이의 표준오차
se = np.sqrt(summer_range.var(ddof=1) / len(summer_range)+ (1.1 ** 2) * spring_fall_range.var(ddof=1) / len(spring_fall_range))
# 검정통계량
z_stat = adjusted_diff / se
# 단측 p-value
p_value = norm.sf(z_stat)
print("=== H2 통계검정 결과 ===")
print(f"검정통계량: {z_stat:.4f}")
print(f"p-value: {p_value:.4f}")


# 비교 집단
groups = ["여름", "봄·가을"]
means = [summer_range_mean, spring_fall_range_mean]
plt.figure(figsize=(8, 5))
bars = plt.bar(groups, means)
plt.bar_label(bars,fmt="%.0f",padding=3)
plt.title("H2 검증: 여름철과 봄·가을의 평균 일중 부하 변동 폭")
plt.xlabel("비교 집단")
plt.ylabel("평균 일중 부하 변동 폭")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# [STEP 7. 연도별 결과 비교]
season_order = ["봄", "여름", "가을", "겨울"]
year_season_peak = (
    df.groupby(["연도", "계절"])["일최대수요"]
    .mean()
    .unstack()
    .reindex(columns=season_order)
)
print("=== 연도별 계절 평균 일 최대 수요 ===")
print(year_season_peak.round(2))

# 연도별 봄·가을 기준 평균
year_base_peak = (df[df["계절"].isin(["봄", "가을"])].groupby("연도")["일최대수요"].mean())
# 연도별 H1 증가율
h1_year = pd.DataFrame({
    "여름 증가율(%)":
        (year_season_peak["여름"] / year_base_peak - 1) * 100,
    "겨울 증가율(%)":
        (year_season_peak["겨울"] / year_base_peak - 1) * 100
})
print("=== 연도별 H1 증가율 ===")
print(h1_year.round(2))

# 연도별 여름 평균 일중 변동 폭
year_summer_range = (df[df["계절"] == "여름"].groupby("연도")["일중변동폭"].mean())
# 연도별 봄·가을 평균 일중 변동 폭
year_base_range = (df[df["계절"].isin(["봄", "가을"])].groupby("연도")["일중변동폭"].mean())
# 연도별 H2 증가율
h2_year = ((year_summer_range / year_base_range - 1) * 100)
print("=== 연도별 H2 증가율 ===")
print(h2_year.round(2))

# H1 연도별 증가율 비교
ax = h1_year.plot(kind="bar",figsize=(9, 5),rot=0)
plt.title("연도별 여름·겨울 최대 전력 수요 증가율")
plt.xlabel("연도")
plt.ylabel("봄·가을 대비 증가율(%)")
plt.axhline(0, color="black", linewidth=0.8)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# H2 연도별 증가율 비교
plt.figure(figsize=(9, 5))
bars = plt.bar(h2_year.index.astype(str),h2_year.values)
plt.axhline(y=10,linestyle="--",label="가설 기준: 10%")
plt.title("연도별 여름철 일중 부하 변동 폭 증가율")
plt.xlabel("연도")
plt.ylabel("봄·가을 대비 증가율(%)")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.bar_label(bars, fmt="%.1f%%", padding=3)
plt.tight_layout()
plt.show()


# [STEP 8. 연도별 가설 충족 여부 확인]
# H1: 여름과 겨울 모두 봄·가을보다 높은지
h1_check = ((h1_year["여름 증가율(%)"] > 0)& (h1_year["겨울 증가율(%)"] > 0))

# H2: 여름의 일중 부하 변동 폭 증가율이 10% 이상인지
h2_check = h2_year >= 10

print("=== 연도별 H1 검증 결과 ===")
print(h1_year.round(2))
print("\nH1 조건 충족 여부:")
print(h1_check)
print("H1 충족 연도:", h1_check.sum(), "/ 3")

print("\n=== 연도별 H2 검증 결과 ===")
print(h2_year.round(2))
print("\nH2 조건 충족 여부:")
print(h2_check)
print("H2 충족 연도:", h2_check.sum(), "/ 3")

# [STEP 9-1. H1·H2 가설 검증 결과 종합]
# 가설별 통계검정 결과
h1_summer_p = summer_test.pvalue
h1_winter_p = winter_test.pvalue
h2_p = p_value

# 최종 결과표 생성
final_result = pd.DataFrame({
    "가설": ["H1-여름", "H1-겨울", "H2"],
    "비교 기준": [
        "봄·가을 대비 일최대수요",
        "봄·가을 대비 일최대수요",
        "봄·가을 대비 일중변동폭"],
    "증가율(%)": [
        summer_rate,
        winter_rate,
        range_rate],
    "p-value": [
        h1_summer_p,
        h1_winter_p,
        h2_p],
    "가설 기준 충족": [
        summer_rate > 0,
        winter_rate > 0,
        range_rate >= 10]
})
print("=== H1·H2 최종 검증 결과 ===")
print(final_result.to_string(index=False))

# [STEP 9-2. 연도별 결과 종합]
year_result = h1_year.copy()
# H2 증가율 추가
year_result["H2 증가율(%)"] = h2_year
# 가설별 충족 여부
year_result["H1 충족"] = ((year_result["여름 증가율(%)"] > 0)& (year_result["겨울 증가율(%)"] > 0))
year_result["H2 충족"] = (year_result["H2 증가율(%)"] >= 10)
print("=== 연도별 가설 검증 결과 ===")
print(year_result.round(2).to_string())

# [STEP 9-3. 분석 결과 저장]
# 가설별 종합 결과
final_result.to_csv("./weather/H1_H2_가설검증_결과.csv",index=False,encoding="utf-8-sig")

# 연도별 분석 결과
year_result.to_csv("./weather/연도별_가설검증_결과.csv",encoding="utf-8-sig")

# 일별 전처리 및 파생변수 데이터
df.to_csv("./weather/전력수요_분석데이터_2022_2024.csv",index=False,encoding="utf-8-sig")
print("분석 결과 CSV 저장 완료")

# [STEP 10-1. 최종 분석 결과 확인]
print("========== H1·H2 최종 결과 ==========")
print(final_result.to_string(index=False))

print("\n========== 연도별 분석 결과 ==========")
print(year_result.round(2).to_string())

print("\n========== 계절별 평균 ==========")
print(
    df.groupby("계절")[["일최대수요", "일중변동폭"]]
    .mean()
    .reindex(["봄", "여름", "가을", "겨울"])
    .round(2)
)