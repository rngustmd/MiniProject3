"""
④ 가설 1·2 검증 + 그래프 4개 (2022~2024)
  그래프 1. [메인]   Matplotlib 선그래프    — 시간대별 태양광 비중
  그래프 2. [가설 1] seaborn 박스플롯       — 연도별 낮 비중 vs 피크 비중
  그래프 3. [가설 2] seaborn 카운트플롯     — 피크 시각 구간별 일수
  그래프 4. [팀 공유] seaborn 히트맵        — 계절 × 연도 태양광 비중
필요 파일 (이 .py와 같은 폴더)
  - 태양광_2022_2024_통합.csv
  - 한국전력거래소_시간별 전국 전력수요량_20221231.csv (2023, 2024도)
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent   # CSV가 다른 폴더에 있으면 경로를 바꾸세요
YEARS = [2022, 2023, 2024]
SEASON = {12: "겨울", 1: "겨울", 2: "겨울", 3: "봄", 4: "봄", 5: "봄",
          6: "여름", 7: "여름", 8: "여름", 9: "가을", 10: "가을", 11: "가을"}
YEAR_COLORS = {2022: "#86b6ef", 2023: "#2a78d6", 2024: "#104281"}   # 연도: 연함 → 진함
TYPE_COLORS = {"낮(11~15시)": "#2a78d6", "피크 시각": "#eb6834"}

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "Malgun Gothic"   # 윈도우 한글 폰트
plt.rcParams["axes.unicode_minus"] = False

# ===================== 1. 불러오기 + 합치기 =====================
solar = pd.read_csv(DATA_DIR / "태양광_2022_2024_통합.csv", encoding="utf-8-sig", parse_dates=["거래일자"])
solar = solar.groupby(["거래일자", "거래시간"], as_index=False)["태양광(MWh)"].sum()  # 17개 시도 → 전국

demand = pd.concat([pd.read_csv(f, encoding="cp949") for f in sorted(DATA_DIR.glob("*전력수요량*.csv"))])
demand = demand.dropna(subset=["날짜"]).melt(id_vars="날짜", var_name="거래시간", value_name="수요(MWh)")
demand["거래일자"] = pd.to_datetime(demand["날짜"])
demand["거래시간"] = demand["거래시간"].str.replace("시", "").astype(int)

df = demand.merge(solar, on=["거래일자", "거래시간"])
df["연도"] = df["거래일자"].dt.year
df["비중"] = df["태양광(MWh)"] / df["수요(MWh)"] * 100          # 태양광 비중(%)

# ===================== 2. 일별 지표 =====================
peak = df.loc[df.groupby("거래일자")["수요(MWh)"].idxmax()].set_index("거래일자")  # 하루 최대 수요 시각
daily = pd.DataFrame({
    "피크시각": peak["거래시간"],
    "피크비중": peak["비중"],
    "낮비중": df[df["거래시간"].between(11, 15)].groupby("거래일자")["비중"].mean(),
})
daily["격차"] = daily["낮비중"] - daily["피크비중"]
daily["저녁피크"] = daily["피크시각"] >= 17
daily["피크구간"] = pd.cut(daily["피크시각"], [0, 16, 18, 24], labels=["17시 전", "17~18시", "19시 이후"])
daily["연도"] = daily.index.year
daily["계절"] = pd.Categorical(daily.index.month.map(SEASON), ["봄", "여름", "가을", "겨울"])

# ===================== 3. 가설 검정 =====================
print("[가설 1] 연도별 평균(%)\n", daily.groupby("연도")[["낮비중", "피크비중", "격차"]].mean().round(2))
gap = [daily.loc[daily["연도"] == y, "격차"] for y in YEARS]
p_kw = stats.kruskal(*gap).pvalue
p_mw = stats.mannwhitneyu(gap[2], gap[0], alternative="greater").pvalue
h1 = "채택" if p_kw < 0.05 and p_mw < 0.05 else "기각"
print(f"Kruskal-Wallis p={p_kw:.3g} | Mann-Whitney(2024 > 2022) p={p_mw:.3g} → {h1}")

tab = pd.crosstab(daily["연도"], daily["저녁피크"])
evening = tab[True] / tab.sum(axis=1) * 100
p_chi = stats.chi2_contingency(tab).pvalue
h2 = "채택" if p_chi < 0.05 and evening[2024] > evening[2022] else "기각"
print(f"\n[가설 2] 저녁 피크일(17시 이후) 비율(%): {evening.round(1).to_dict()} | 카이제곱 p={p_chi:.3g} → {h2}")

tab19 = pd.crosstab(daily["연도"], daily["피크시각"] >= 19)
p_19 = stats.chi2_contingency(tab19).pvalue
print(f"추가 발견) 19시 이후 피크일 비율(%): {(tab19[True] / tab19.sum(axis=1) * 100).round(1).to_dict()} "
      f"| 카이제곱 p={p_19:.3g}")


def p_text(p):
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


# ===================== 4. 그래프 1: [메인] Matplotlib 선그래프 =====================
hourly = df.groupby(["연도", "거래시간"])["비중"].mean().unstack(0)   # 행: 시간, 열: 연도
fig, ax = plt.subplots(figsize=(10, 5))
ax.axvspan(16.5, 21.5, color="#eeeeee", zorder=0)
for y in YEARS:
    ax.plot(hourly.index, hourly[y], color=YEAR_COLORS[y], linewidth=2.5, label=y)
    ax.annotate(f"{y}  {hourly.loc[13, y]:.1f}%", (13, hourly.loc[13, y]), xytext=(0, 7),
                textcoords="offset points", ha="center", va="bottom", fontsize=9, color="#52514e")
ax.set_ylim(0, hourly.values.max() * 1.18)
ax.text(19, ax.get_ylim()[1] * 0.92, "수요 피크 시간대\n(17~21시)", ha="center", fontsize=10, color="#52514e")
ax.set(xticks=range(1, 25), xlim=(0.5, 24.5), xlabel="거래시간 (1 = 00~01시)", ylabel="태양광 비중(%)")
ax.set_title("태양광은 낮에만 해마다 늘고, 수요 피크 시간대에는 거의 없다", loc="left", fontweight="bold")
ax.legend(title="연도", loc="upper left")
plt.tight_layout()
plt.show()

# ===================== 5. 그래프 2: [가설 1] seaborn 박스플롯 =====================
box = daily.melt(id_vars="연도", value_vars=["낮비중", "피크비중"], var_name="구분", value_name="비중")
box["구분"] = box["구분"].map({"낮비중": "낮(11~15시)", "피크비중": "피크 시각"})
fig, ax = plt.subplots(figsize=(9, 5))
sns.boxplot(data=box, x="연도", y="비중", hue="구분", palette=TYPE_COLORS, saturation=1,
            width=0.6, fliersize=2, linewidth=1.2, ax=ax)
for i, y in enumerate(YEARS):                     # 중앙값 표시 (낮: 상자 안, 피크: 상자 오른쪽)
    med_day = daily.loc[daily["연도"] == y, "낮비중"].median()
    med_peak = daily.loc[daily["연도"] == y, "피크비중"].median()
    ax.text(i - 0.15, med_day, f"{med_day:.1f}", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color="white")
    ax.text(i + 0.33, med_peak, f"{med_peak:.1f}", ha="left", va="center", fontsize=9,
            fontweight="bold", color="#0b0b0b")
ax.set(xlabel="", ylabel="태양광 비중(%)")
ax.set_title(f"[가설 1 {h1}] 낮 비중만 해마다 올라가고 피크 비중은 제자리 (Kruskal-Wallis {p_text(p_kw)})",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(title="")
plt.tight_layout()
plt.show()

# ===================== 6. 그래프 3: [가설 2] seaborn 카운트플롯 =====================
fig, ax = plt.subplots(figsize=(9, 5))
sns.countplot(data=daily, x="피크구간", hue="연도", palette=YEAR_COLORS, saturation=1, ax=ax)
for c in ax.containers:
    ax.bar_label(c, fontsize=9, padding=2)
ax.set(xlabel="하루 최대 수요가 나온 시각", ylabel="일수")
ax.set_title(f"[가설 2 {h2}] 저녁 피크일 비율은 비슷({p_text(p_chi)}), "
             f"19시 이후 피크일은 증가(추가 발견, {p_text(p_19)})",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(title="연도")
plt.tight_layout()
plt.show()

# ===================== 7. 그래프 4: [팀 공유] seaborn 히트맵 =====================
day_tbl = daily.pivot_table(index="계절", columns="연도", values="낮비중", observed=True)
peak_tbl = daily.pivot_table(index="계절", columns="연도", values="피크비중", observed=True)
vmax = day_tbl.values.max()                       # 두 히트맵 색 기준을 같게
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
sns.heatmap(day_tbl, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=vmax, cbar=False,
            linewidths=2, linecolor="white", ax=axes[0])
sns.heatmap(peak_tbl, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=vmax,
            linewidths=2, linecolor="white", cbar_kws={"label": "태양광 비중(%)"}, ax=axes[1])
axes[0].set(title="낮(11~15시) 태양광 비중", xlabel="", ylabel="")
axes[1].set(title="피크 시각 태양광 비중", xlabel="", ylabel="")
axes[0].tick_params(axis="y", rotation=0)
fig.suptitle("계절 × 연도별 태양광 비중: 피크 때는 어느 계절이든 2% 미만", x=0.02, ha="left", fontweight="bold")
plt.tight_layout()
plt.show()