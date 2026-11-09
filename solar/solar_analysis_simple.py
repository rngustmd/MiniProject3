# ============================================================
# ④ 전력 수요와 태양광 발전량 — 2단계: 가설 검정 + 그래프
# ------------------------------------------------------------
# 먼저 '1_전처리.py'를 실행해서 '시간별_분석데이터.csv'를 만들어 두세요.
#
# 가설 1: 낮 비중은 해마다 커지지만 피크 비중은 그대로라서, 둘의 격차가 커질 것이다.
# 가설 2: 저녁(17시 이후)에 피크가 오는 날의 비율이 해마다 늘어날 것이다.
#
# 그래프 1. 시간대별 태양광 비중        (Matplotlib 선그래프)
# 그래프 2. 연도별 낮 비중 vs 피크 비중  (seaborn 박스플롯)   → 가설 1
# 그래프 3. 피크 시각 구간별 일수        (seaborn 카운트플롯) → 가설 2
# 그래프 4. 계절 × 연도별 태양광 비중    (seaborn 히트맵)
# ============================================================

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent

# 그래프 기본 설정
sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "Malgun Gothic"   # 한글 폰트 (윈도우)
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

# 연도별 색: 2022 연한 파랑 → 2024 진한 파랑
YEAR_COLORS = {2022: "#86b6ef", 2023: "#2a78d6", 2024: "#104281"}


# ============================================================
# 1. 데이터 불러오기
# ============================================================
df = pd.read_csv(BASE_DIR / "시간별_분석데이터.csv", encoding="utf-8-sig")
df["거래일자"] = pd.to_datetime(df["거래일자"])
df["연도"] = df["거래일자"].dt.year
print("불러온 행 개수:", len(df))


# ============================================================
# 2. 일별 지표 만들기 (하루 = 1행)
# ============================================================
# (1) 피크: 하루 중 수요가 가장 많은 행 찾기
#     idxmax() = 가장 큰 값이 있는 행 번호
peak_index = df.groupby("거래일자")["수요"].idxmax()
peak = df.loc[peak_index, ["거래일자", "거래시간", "비중"]]
peak.columns = ["거래일자", "피크시각", "피크비중"]

# (2) 낮 비중: 11~15시 태양광 비중의 평균
day = df[(df["거래시간"] >= 11) & (df["거래시간"] <= 15)]
day = day.groupby("거래일자")["비중"].mean().reset_index()
day.columns = ["거래일자", "낮비중"]

# (3) 두 표를 날짜 기준으로 합치기
daily = pd.merge(peak, day, on="거래일자")

# (4) 새 변수 만들기
daily["격차"] = daily["낮비중"] - daily["피크비중"]
daily["저녁피크"] = daily["피크시각"] >= 17          # 17시 이후면 True
daily["연도"] = daily["거래일자"].dt.year
daily["월"] = daily["거래일자"].dt.month

# 계절 나누기
season_map = {3: "봄", 4: "봄", 5: "봄",
              6: "여름", 7: "여름", 8: "여름",
              9: "가을", 10: "가을", 11: "가을",
              12: "겨울", 1: "겨울", 2: "겨울"}
daily["계절"] = daily["월"].map(season_map)

# 피크 시각 구간 나누기: 1~16시 / 17~18시 / 19~24시
daily["피크구간"] = pd.cut(daily["피크시각"], bins=[0, 16, 18, 24],
                         labels=["17시 전", "17~18시", "19시 이후"])

print("일별 표 행 개수:", len(daily))


# ============================================================
# 3. 가설 1 검정: 격차가 해마다 커지는가
# ============================================================
print("\n========== 가설 1 ==========")
print(daily.groupby("연도")[["낮비중", "피크비중", "격차"]].mean().round(2))

gap_2022 = daily[daily["연도"] == 2022]["격차"]
gap_2023 = daily[daily["연도"] == 2023]["격차"]
gap_2024 = daily[daily["연도"] == 2024]["격차"]

# Kruskal-Wallis: 3개 연도의 격차가 서로 다른가
p_kw = stats.kruskal(gap_2022, gap_2023, gap_2024).pvalue
# Mann-Whitney: 2024년 격차가 2022년보다 큰가 (한쪽 방향 검정)
p_mw = stats.mannwhitneyu(gap_2024, gap_2022, alternative="greater").pvalue

# p값이 아주 작아서 지수 형태로 출력 (예: 4.23e-19 = 0.000...000423)
# print(f"Kruskal-Wallis p = {p_kw:.2e}")
# print(f"Mann-Whitney   p = {p_mw:.2e}")

if p_kw < 0.05 and p_mw < 0.05:
    h1 = "채택"
else:
    h1 = "기각"
print("→ 가설 1", h1)


# ============================================================
# 4. 가설 2 검정: 저녁 피크일 비율이 해마다 늘어나는가
# ============================================================
print("\n========== 가설 2 ==========")
# 교차표: 연도별로 저녁 피크(True)인 날, 아닌 날(False)이 며칠인지
table = pd.crosstab(daily["연도"], daily["저녁피크"])
print(table)

ratio = table[True] / table.sum(axis=1) * 100      # 저녁 피크일 비율(%)
print("저녁 피크일 비율(%):")
print(ratio.round(1))

# 카이제곱 검정: 연도에 따라 비율이 다른가
p_chi = stats.chi2_contingency(table).pvalue
print("카이제곱 p =", round(p_chi, 4))

if p_chi < 0.05 and ratio[2024] > ratio[2022]:
    h2 = "채택"
else:
    h2 = "기각"
print("→ 가설 2", h2)

# 추가 발견: 19시 이후 피크일 비율 (결과를 보고 정한 기준이라 '참고용')
table19 = pd.crosstab(daily["연도"], daily["피크시각"] >= 19)
ratio19 = table19[True] / table19.sum(axis=1) * 100
p_19 = stats.chi2_contingency(table19).pvalue
print("\n[추가 발견] 19시 이후 피크일 비율(%):")
print(ratio19.round(1))
print("카이제곱 p =", round(p_19, 4))


# ============================================================
# 5. 그래프 1: 시간대별 태양광 비중 (선그래프)
# ============================================================
# 연도·시간별 평균 비중 → 행: 시간(1~24), 열: 연도
hourly = df.groupby(["거래시간", "연도"])["비중"].mean().unstack()

plt.figure(figsize=(10, 5))
plt.axvspan(16.5, 21.5, color="#eeeeee")          # 수요 피크 시간대(17~21시)에 회색 배경

for year in [2022, 2023, 2024]:
    plt.plot(hourly.index, hourly[year], color=YEAR_COLORS[year], linewidth=2.5, label=year)
    # 13시 값을 선 위에 표시
    value_13 = hourly.loc[13, year]
    plt.text(13, value_13 + 0.15, f"{year}  {value_13:.1f}%", ha="center", fontsize=9)

plt.text(19, 6.5, "수요 피크 시간대\n(17~21시)", ha="center", fontsize=10, color="gray")
plt.xticks(range(1, 25))
plt.ylim(0, 7.5)
plt.xlabel("거래시간 (1 = 00~01시)")
plt.ylabel("태양광 비중(%)")
plt.title("시간대별 태양광 비중 (2022~2024)", loc="left", fontweight="bold")
plt.legend(title="연도", loc="upper left")
plt.tight_layout()
plt.show()


# ============================================================
# 6. 그래프 2: 연도별 낮 비중 vs 피크 비중 (박스플롯) → 가설 1
# ============================================================
# 박스플롯용으로 표 모양 바꾸기: '구분' 열에 낮/피크, '비중' 열에 값
box = daily.melt(id_vars="연도", value_vars=["낮비중", "피크비중"],
                 var_name="구분", value_name="비중")
box["구분"] = box["구분"].replace({"낮비중": "낮(11~15시)", "피크비중": "피크 시각"})

plt.figure(figsize=(9, 5))
sns.boxplot(data=box, x="연도", y="비중", hue="구분",
            palette={"낮(11~15시)": "#2a78d6", "피크 시각": "#eb6834"},
            width=0.6, fliersize=2)
plt.xlabel("")
plt.ylabel("태양광 비중(%)")
plt.title("연도별 낮 비중과 피크 비중 비교", loc="left", fontweight="bold")
plt.legend(title="")
plt.tight_layout()
plt.show()


# ============================================================
# 7. 그래프 3: 피크 시각 구간별 일수 (카운트플롯) → 가설 2
# ============================================================
plt.figure(figsize=(9, 5))
ax = sns.countplot(data=daily, x="피크구간", hue="연도", palette=YEAR_COLORS)

# 막대 위에 일수 숫자 표시
for bars in ax.containers:
    ax.bar_label(bars, fontsize=9)

plt.xlabel("하루 최대 수요가 나온 시각")
plt.ylabel("일수")
plt.title("피크 시각 구간별 일수 (연도별)", loc="left", fontweight="bold")
plt.legend(title="연도")
plt.tight_layout()
plt.show()


# ============================================================
# 8. 그래프 4: 계절 × 연도별 태양광 비중 (히트맵)
# ============================================================
season_order = ["봄", "여름", "가을", "겨울"]

# 표 만들기: 행 = 계절, 열 = 연도, 값 = 평균 비중
day_table = daily.pivot_table(index="계절", columns="연도", values="낮비중").reindex(season_order)
peak_table = daily.pivot_table(index="계절", columns="연도", values="피크비중").reindex(season_order)

# 두 히트맵의 색 기준을 같게 (0 ~ 낮 비중 최댓값)
max_value = day_table.values.max()

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

sns.heatmap(day_table, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=max_value,
            linewidths=2, cbar=False, ax=axes[0])
axes[0].set_title("낮(11~15시) 태양광 비중")

sns.heatmap(peak_table, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=max_value,
            linewidths=2, cbar_kws={"label": "태양광 비중(%)"}, ax=axes[1])
axes[1].set_title("피크 시각 태양광 비중")

for ax in axes:
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="y", rotation=0)   # 계절 글자 똑바로

plt.suptitle("계절·연도별 낮 비중과 피크 비중", fontweight="bold")
plt.tight_layout()
plt.show()