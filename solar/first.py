# ============================================================
# ④ 전력 수요와 태양광 발전량 — 1단계: 데이터 전처리
# ------------------------------------------------------------
# 하는 일
#   1) 태양광 CSV 6개를 읽어서 하나로 합친다 (pd.concat)
#   2) 전력수요 CSV 3개를 읽어서 하나로 합친다
#   3) 두 데이터를 날짜 + 시간 기준으로 합친다 (pd.merge)
#   4) 결과를 '시간별_분석데이터.csv'로 저장한다 → 2단계 코드에서 사용
#
# 폴더 구성 (이 .py 파일이 있는 폴더 기준)
#   이 폴더/
#   ├─ 1_전처리.py
#   ├─ 한국전력거래소_시간별 전국 전력수요량_20221231.csv   (2023, 2024도)
#   └─ solar_data/
#        └─ 태양광 CSV 6개
# ============================================================

from pathlib import Path
import pandas as pd

# 이 .py 파일이 있는 폴더 (어디서 실행해도 같은 폴더를 찾음)
BASE_DIR = Path(__file__).resolve().parent
SOLAR_DIR = BASE_DIR / "solar_data"

# 분석 기간
START = "2022-01-01"
END = "2024-12-31"


# ============================================================
# 1. 태양광 파일 읽어서 합치기
# ============================================================
# 파일마다 형식이 달라서, 하나씩 읽으면서 같은 모양으로 맞춘다
#   - 2023년 11월까지: 가로형 (태양광 열, 풍력 열이 따로 있음)
#   - 2023년 12월부터: 세로형 ('연료원' 열에 태양광/풍력이 적혀 있음)

solar_list = []   # 형식을 맞춘 파일들을 모아둘 리스트

for path in sorted(SOLAR_DIR.glob("*.csv")):
    df = pd.read_csv(path, encoding="cp949", dtype=str)   # 일단 모두 글자로 읽기

    # 열 이름 정리: 앞뒤 공백 지우기, '지역명' → '지역'
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"지역명": "지역"})

    if "연료원" in df.columns:
        # 세로형: 연료원이 '태양광'인 행만 남기기
        df = df[df["연료원"].str.strip() == "태양광"]
        value_col = df.columns[4]          # 5번째 열이 발전량
    else:
        # 가로형: 이름에 '태양광'이 들어간 열 찾기
        for col in df.columns:
            if "태양광" in col:
                value_col = col

    # 필요한 4개 열만 남기고 이름 통일
    df = df[["거래일자", "거래시간", "지역", value_col]]
    df.columns = ["거래일자", "거래시간", "지역", "태양광"]

    solar_list.append(df)
    print("읽음:", path.name, len(df), "행")

# 리스트에 모은 파일들을 하나로 합치기
solar = pd.concat(solar_list, ignore_index=True)


# ============================================================
# 2. 태양광 값 정리하기
# ============================================================
# (1) 숫자로 바꾸기: 앞뒤 공백, 쉼표(1,011.69) 제거
solar["태양광"] = solar["태양광"].str.strip().str.replace(",", "")
solar["태양광"] = pd.to_numeric(solar["태양광"], errors="coerce")

# (2) 빈칸은 밤 시간대(거래 없음)라서 0으로 채우기
solar["태양광"] = solar["태양광"].fillna(0)

# (3) 날짜·시간 형식 바꾸기
solar["거래일자"] = pd.to_datetime(solar["거래일자"].str.strip())
solar["거래시간"] = solar["거래시간"].str.strip().astype(int)
solar["지역"] = solar["지역"].str.strip()

# (4) 분석 기간(2022~2024년)만 남기기
solar = solar[(solar["거래일자"] >= START) & (solar["거래일자"] <= END)]

# (5) 점검하기
print("\n[태양광 점검]")
print("행 개수:", len(solar), "(정상: 1,096일 × 24시간 × 17개 시도 = 447,168)")
print("결측값:", solar.isna().sum().sum())
print("중복 행:", solar.duplicated(["거래일자", "거래시간", "지역"]).sum())
print("음수 값:", (solar["태양광"] < 0).sum())

# (6) 17개 시도를 시간마다 더해서 '전국 합계' 만들기
solar_nat = solar.groupby(["거래일자", "거래시간"])["태양광"].sum().reset_index()


# ============================================================
# 3. 전력수요 파일 읽어서 합치기
# ============================================================
demand_list = []
for path in sorted(BASE_DIR.glob("*전력수요량*.csv")):
    df = pd.read_csv(path, encoding="cp949")
    demand_list.append(df)
    print("읽음:", path.name)

demand = pd.concat(demand_list, ignore_index=True)
demand = demand.dropna(subset=["날짜"])     # 맨 아래 빈 행이 있으면 지우기

# 가로형(날짜 | 1시 | 2시 | ... | 24시) → 세로형(날짜 | 거래시간 | 수요)
demand = demand.melt(id_vars="날짜", var_name="거래시간", value_name="수요")

demand["거래일자"] = pd.to_datetime(demand["날짜"])
demand["거래시간"] = demand["거래시간"].str.replace("시", "").astype(int)   # '13시' → 13
demand = demand[["거래일자", "거래시간", "수요"]]

print("\n[수요 점검]")
print("결측값:", demand.isna().sum().sum())
print("0 이하 값:", (demand["수요"] <= 0).sum())
print("최솟값:", demand["수요"].min(), "/ 최댓값:", demand["수요"].max())


# ============================================================
# 4. 두 데이터 합치기 + 태양광 비중 계산
# ============================================================
# 날짜와 시간이 같은 행끼리 옆으로 붙이기
df = pd.merge(demand, solar_nat, on=["거래일자", "거래시간"])

# 태양광 비중(%) = 그 시간에 쓴 전기 중 태양광이 채운 몫
df["비중"] = df["태양광"] / df["수요"] * 100

df = df.sort_values(["거래일자", "거래시간"]).reset_index(drop=True)

print("\n[합친 결과]")
print("행 개수:", len(df), "(정상: 1,096일 × 24시간 = 26,304)")
print("결측값:", df.isna().sum().sum())

# 연도별 태양광 합계 (TWh) — 해마다 늘어나는지 확인
print("\n연도별 태양광 합계(TWh)")
print((df.groupby(df["거래일자"].dt.year)["태양광"].sum() / 1000000).round(2))


# ============================================================
# 5. 저장하기 → 2단계 코드에서 이 파일을 읽어서 사용
# ============================================================
df.to_csv(BASE_DIR / "시간별_분석데이터.csv", index=False, encoding="utf-8-sig")
print("\n저장 완료: 시간별_분석데이터.csv")