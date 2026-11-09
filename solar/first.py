"""
태양광 발전량 CSV 여러 개를 읽어서 pd.concat으로 하나의 DataFrame으로 합치는 코드
(한국전력거래소_지역별 시간별 태양광 및 풍력 발전량)

파일마다 형식이 달라서, 읽을 때 같은 형식으로 맞춘 뒤 concat 합니다.
  - 2017.01 ~ 2023.11 파일: 가로형  → 태양광 / 풍력이 각각 별도 열
  - 2023.12 ~ 2024.12 파일: 세로형  → '연료원' 열에 태양광 / 풍력
  - 열 이름도 조금씩 다름 (지역/지역명, MWh/Mwh, 앞뒤 공백 등)

합친 결과(solar)의 열: 거래일자 | 거래시간 | 지역 | 태양광(MWh)
  - 지역: 17개 시도 (풍력은 지역 구분이 달라서 제외)
"""
import glob
import pandas as pd

# ── 설정 ─────────────────────────────────────────────
DATA_DIR = r"C:\Users\user\Desktop\미니3\MiniProject3\solar\solar_data"               # 태양광 CSV를 모아둔 폴더 (Colab이면 "/content/solar_data")
START, END = "2022-01-01", "2024-12-31"  # 분석 기간


# ── 함수 ─────────────────────────────────────────────
def read_csv_kr(path):
    """공공데이터 CSV는 대부분 cp949. 안 되면 utf-8로 다시 시도."""
    for enc in ("cp949", "utf-8-sig"):
        try:
            return pd.read_csv(path, encoding=enc, dtype=str)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 읽을 수 없음: {path}")


def to_number(s):
    """'  1,234.5 ' 같은 값을 숫자로 변환.
    - 앞뒤 공백, 천 단위 쉼표 제거
    - 빈칸은 0으로 처리 (빈칸은 밤·새벽 시간대 = 거래량 없음)
    """
    s = s.astype(str).str.strip().str.replace(",", "", regex=False)
    s = s.replace({"": None, "nan": None})
    return pd.to_numeric(s, errors="coerce").fillna(0)


def standardize(df):
    """파일 하나를 [거래일자, 거래시간, 지역, 태양광(MWh)] 형태로 맞춤."""
    df.columns = [c.strip() for c in df.columns]
    region_col = "지역" if "지역" in df.columns else "지역명"

    if "연료원" in df.columns:  # 세로형 (2023.12~)
        df = df[df["연료원"].str.strip() == "태양광"]
        value_col = [c for c in df.columns if "mwh" in c.lower()][0]
    else:                       # 가로형 (~2023.11)
        value_col = [c for c in df.columns if "태양광" in c][0]

    return pd.DataFrame({
        "거래일자": pd.to_datetime(df["거래일자"].str.strip()),
        "거래시간": df["거래시간"].astype(str).str.strip().astype(int),
        "지역": df[region_col].str.strip(),
        "태양광(MWh)": to_number(df[value_col]),
    })


# ── 1. 폴더 안 CSV를 모두 읽어서 형식 맞추기 ─────────────
frames = []
for path in sorted(glob.glob(f"{DATA_DIR}/*.csv")):
    raw = read_csv_kr(path)
    if "거래시간" not in [c.strip() for c in raw.columns]:
        print("건너뜀 (태양광 파일 아님):", path)
        continue
    part = standardize(raw)
    print(f"{path}: {part['거래일자'].min().date()} ~ {part['거래일자'].max().date()}, {len(part):,}행")
    frames.append(part)

# ── 2. concat으로 합치고 분석 기간만 남기기 ───────────────
solar = pd.concat(frames, ignore_index=True)
solar = solar[(solar["거래일자"] >= START) & (solar["거래일자"] <= END)]

dup = solar.duplicated(["거래일자", "거래시간", "지역"]).sum()
if dup:
    print(f"주의: 겹치는 행 {dup:,}개 → 먼저 나온 값만 남김")
    solar = solar.drop_duplicates(["거래일자", "거래시간", "지역"])

solar = solar.sort_values(["거래일자", "거래시간", "지역"]).reset_index(drop=True)

# ── 3. 빠진 날짜·시간이 없는지 확인 ──────────────────────
all_days = pd.date_range(START, END)
missing = all_days.difference(solar["거래일자"].unique())
per_day = solar.groupby("거래일자").size()

print("\n[점검]")
print(f"날짜 수: {solar['거래일자'].nunique()} / {len(all_days)}")
print(f"빠진 날짜: {list(missing.date) if len(missing) else '없음'}")
print(f"하루 행 수가 408(17개 시도 × 24시간)이 아닌 날: {(per_day != 17 * 24).sum()}일")
print(f"지역 수: {solar['지역'].nunique()}개")

# ── 4. 전국 합계 (수요 데이터와 합칠 때 사용) ─────────────
# 수요 데이터도 1시~24시 형식이라, 거래일자 + 거래시간 기준으로 merge하면 됩니다.
solar_nat = (solar.groupby(["거래일자", "거래시간"], as_index=False)["태양광(MWh)"].sum())

print(f"\n전국 시간별 합계: {len(solar_nat):,}행 (= {len(all_days)}일 × 24시간)")
print("\n연도별 태양광 합계 (TWh)")
print((solar_nat.groupby(solar_nat["거래일자"].dt.year)["태양광(MWh)"].sum() / 1e6).round(2))

# 파일로도 저장하고 싶으면 아래 주석을 해제하세요
solar.to_csv("태양광_2022_2024_통합.csv", index=False, encoding="utf-8-sig")