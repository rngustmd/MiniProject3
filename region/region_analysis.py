# 지역 파트 분석 · 시각화 : 한전 시간별 전력사용량 CSV 하나로 H3 · H4 검증
# 그래프 저장 위치 : ./region/images/ ( 폴더를 먼저 만들어 두기 )
# 수업에서 배운 문법만 사용 : read_csv , loc , groupby , agg , merge , dt , np.where , for , if , plot/bar/barh

# 0] 준비
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
pd.set_option( 'display.unicode.east_asian_width' , True )

Blue = '#2a78d6'    # 수도권 ( 강조 )
Gray = '#b4b2ab'    # 비수도권
Dark = '#52514e'    # 기준선

df = pd.read_csv( './region/region_data/한국전력공사_전국 시간별 전력사용량_20241231.csv' )

# 1] 전처리
# 이상치 검토 결과 검침 오류로 추정되는 급감 구간 2건( 2022-10-02 오전 , 2023-02-27 오후 남서울본부 )이 있으나
# 보정 전후 결과가 같아 원자료를 그대로 사용함
print( '========== 전처리 ==========' )
print( '원본 행·열 :' , df.shape )
print( '결측치 :' , df.isnull().sum().sum() , '개' )
print( '중복 행 :' , len( df ) - len( df.drop_duplicates() ) , '개' )

# 이상치 확인 : 2022-10-02 값을 일주일 전 같은 요일 · 같은 본부 · 같은 시각 값과 비교 ( 날짜 변환 전에 실행 )
그날 = df[ df['기준일자'] == '2022-10-02' ][ [ '본부명' , '기준시' , '전력사용량' ] ].rename( columns={ '전력사용량' : '당일' } )
지난주 = df[ df['기준일자'] == '2022-09-25' ][ [ '본부명' , '기준시' , '전력사용량' ] ].rename( columns={ '전력사용량' : '1주전' } )
비교 = pd.merge( 그날 , 지난주 , on=[ '본부명' , '기준시' ] , how='inner' )
비교['비율'] = ( 비교['당일'] / 비교['1주전'] * 100 ).round( 1 )
print( '\n[ 이상치 확인 : 2022-10-02 , 일주일 전의 60% 미만인 값 ]' )
print( 비교[ 비교['비율'] < 60 ] )

본부목록 = [ '서울본부' , '남서울본부' , '경기본부' , '경기북부본부' , '인천본부' ,
            '강원본부' , '충북본부' , '대전세종충남본부' , '전북본부' , '광주전남본부' ,
            '대구본부' , '경북본부' , '부산울산본부' , '경남본부' , '제주본부' ]

# 1-1] 고객호수는 원격검침 확대로 계속 늘어나서 빼고 필요한 열만 남기기
df = df[ [ '기준일자' , '기준시' , '본부명' , '전력사용량' ] ]

# 1-2] 권역 붙이기 : 본부 → 권역 표를 직접 만들어서 merge
권역표 = pd.DataFrame( {
    '본부명' : 본부목록 ,
    '권역' : [ '수도권' , '수도권' , '수도권' , '수도권' , '수도권' ,
              '비수도권' , '비수도권' , '비수도권' , '비수도권' , '비수도권' ,
              '비수도권' , '비수도권' , '비수도권' , '비수도권' , '비수도권' ] } )
df = pd.merge( df , 권역표 , on='본부명' , how='inner' )

# 1-3] 날짜 형식으로 바꾸고 연도 · 월 열 추가
df['기준일자'] = pd.to_datetime( df['기준일자'] )
df['연도'] = df['기준일자'].dt.year
df['월'] = df['기준일자'].dt.month
print( '\n처리 후 행·열 :' , df.shape )
print( '기간 :' , np.min( df['기준일자'] ) , '~' , np.max( df['기준일자'] ) )

# 2] EDA 1 : 본부별 사용량 비중 ( 3년 합계 )
본부별 = df.groupby( '본부명' ).agg( 사용량=( '전력사용량' , 'sum' ) ).reset_index()
본부별['비중'] = ( 본부별['사용량'] / 본부별['사용량'].sum() * 100 ).round( 1 )
본부별 = pd.merge( 본부별 , 권역표 , on='본부명' , how='inner' )
본부별 = 본부별.sort_values( '비중' , ascending=True )   # 작은 값부터 → 가로막대에서 큰 값이 위로

print( '\n========== EDA 1 : 본부별 사용량 비중 (2022~2024 합계) ==========' )
print( 본부별.sort_values( '비중' , ascending=False )[ [ '본부명' , '권역' , '비중' ] ] )
print( '서울특별시 ( 서울본부 + 남서울본부 ) :' ,
       본부별.loc[ ( 본부별['본부명'] == '서울본부' ) | ( 본부별['본부명'] == '남서울본부' ) , '비중' ].sum() , '%' )

색 = []
for 권역 in 본부별['권역'] :
    if 권역 == '수도권' :
        색.append( Blue )
    else :
        색.append( Gray )

plt.figure( figsize=( 8 , 5.5 ) )
plt.barh( 본부별['본부명'] , 본부별['비중'] , color=색 )
plt.title( '본부별 사용량 비중 : 수도권 5개 본부(파란색) 합계 약 39% (2022~2024)' )
plt.xlabel( '사용량 비중(%)' )
plt.grid( axis='x' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './region/images/EDA1_본부별_비중.png' , dpi=150 )
plt.show()


# 3] 권역별 · 날짜별 · 시간별 합계 ( 아래 분석에서 계속 사용 )
권역시간 = df.groupby( [ '권역' , '기준일자' , '기준시' ] ).agg( 사용량=( '전력사용량' , 'sum' ) ).reset_index()
수도권시간 = 권역시간[ 권역시간['권역'] == '수도권' ]
비수도권시간 = 권역시간[ 권역시간['권역'] == '비수도권' ]

# 4] EDA 2 : 권역별 하루 사용 패턴 ( 하루 평균 = 1 로 맞춰서 모양만 비교 )
수도권패턴 = 수도권시간.groupby( '기준시' )['사용량'].mean()
수도권패턴 = 수도권패턴 / 수도권패턴.mean()
비수도권패턴 = 비수도권시간.groupby( '기준시' )['사용량'].mean()
비수도권패턴 = 비수도권패턴 / 비수도권패턴.mean()

print( '\n========== EDA 2 : 권역별 하루 사용 패턴 (하루 평균 = 1.00) ==========' )
for 이름 , 패턴 in [ [ '수도권' , 수도권패턴 ] , [ '비수도권' , 비수도권패턴 ] ] :
    높은순 = 패턴.sort_values( ascending=False )
    print( 이름 , ': 최고' , 높은순.index[0] , '시' , round( 높은순.iloc[0] , 3 ) , '배 /' ,
           '최저' , 높은순.index[-1] , '시' , round( 높은순.iloc[-1] , 3 ) , '배 /' ,
           '최고÷최저' , round( 높은순.iloc[0] / 높은순.iloc[-1] , 2 ) , '배' )

plt.figure( figsize=( 8 , 4.5 ) )
plt.plot( 비수도권패턴.index , 비수도권패턴 , color=Gray , marker='o' , label='비수도권' )
plt.plot( 수도권패턴.index , 수도권패턴 , color=Blue , marker='o' , label='수도권' )
plt.plot( [ 1 , 24 ] , [ 1 , 1 ] , color=Dark , linestyle='--' )   # 하루 평균선
plt.title( '권역별 하루 사용 패턴 : 수도권은 새벽에 더 낮고 낮에 더 높음' )
plt.xlabel( '시각(시)' )
plt.ylabel( '하루 평균 대비 배율' )
plt.xticks( 수도권패턴.index )
plt.legend()
plt.grid( axis='y' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './region/images/EDA2_권역별_하루패턴.png' , dpi=150 )
plt.show()

# 5] 가설 3 : 수도권 사용량 비중 40% 이상
# 5-1] 날짜별 비중
수도권일 = 수도권시간.groupby( '기준일자' ).agg( 수도권=( '사용량' , 'sum' ) ).reset_index()
비수도권일 = 비수도권시간.groupby( '기준일자' ).agg( 비수도권=( '사용량' , 'sum' ) ).reset_index()
일별 = pd.merge( 수도권일 , 비수도권일 , on='기준일자' , how='inner' )
일별['수도권비중'] = 일별['수도권'] / ( 일별['수도권'] + 일별['비수도권'] ) * 100
일별['연도'] = 일별['기준일자'].dt.year

# 5-2] 연도별 비중
연도별 = 일별.groupby( '연도' ).agg( 수도권=( '수도권' , 'sum' ) , 비수도권=( '비수도권' , 'sum' ) ).reset_index()
연도별['비중'] = ( 연도별['수도권'] / ( 연도별['수도권'] + 연도별['비수도권'] ) * 100 ).round( 1 )

plt.figure( figsize=( 7 , 4.5 ) )
plt.bar( 연도별['연도'].astype( str ) , 연도별['비중'] , color=Blue , width=0.5 )
plt.plot( [ -0.4 , 2.4 ] , [ 40 , 40 ] , color=Dark , linestyle='--' , label='기준 40%' )   # 기준선
plt.title( '[가설 3] 연도별 수도권 비중 : 3년 모두 기준(40%)에 못 미침' )
plt.ylabel( '수도권 비중(%)' )
plt.legend()
plt.grid( axis='y' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './region/images/H3_수도권_비중.png' , dpi=150 )
plt.show()

# 6] 가설 4 : 피크 집중도 = 하루 최대 1시간 사용량 ÷ 그날 시간당 평균
수도권피크 = 수도권시간.groupby( '기준일자' ).agg( 최대=( '사용량' , 'max' ) , 평균=( '사용량' , 'mean' ) ).reset_index()
수도권피크['수도권'] = 수도권피크['최대'] / 수도권피크['평균']
비수도권피크 = 비수도권시간.groupby( '기준일자' ).agg( 최대=( '사용량' , 'max' ) , 평균=( '사용량' , 'mean' ) ).reset_index()
비수도권피크['비수도권'] = 비수도권피크['최대'] / 비수도권피크['평균']

집중도 = pd.merge( 수도권피크[ [ '기준일자' , '수도권' ] ] , 비수도권피크[ [ '기준일자' , '비수도권' ] ] , on='기준일자' , how='inner' )
집중도['연도'] = 집중도['기준일자'].dt.year
집중도['월'] = 집중도['기준일자'].dt.month

# 월평균으로 묶기 ( 1,096일 → 36개월 )
월별 = 집중도.groupby( [ '연도' , '월' ] ).agg( 수도권=( '수도권' , 'mean' ) , 비수도권=( '비수도권' , 'mean' ) ).reset_index()

# 배 → % 로 바꾸기 ( 1.18배 = 하루 평균보다 18% 많음 )
월별['수도권%'] = ( 월별['수도권'] - 1 ) * 100
월별['비수도권%'] = ( 월별['비수도권'] - 1 ) * 100
월별['차이'] = 월별['수도권%'] - 월별['비수도권%']

# x축 눈금 : 매년 1월 · 7월만 표시
위치 = []
라벨 = []
for i in range( len( 월별 ) ) :
    if 월별['월'][i] == 1 or 월별['월'][i] == 7 :
        위치.append( i )
        라벨.append( str( 월별['연도'][i] ) + '.' + str( 월별['월'][i] ) )

# 그래프 4-1] 두 권역 비교 ( % )
plt.figure( figsize=( 10 , 4.5 ) )
plt.plot( range( len( 월별 ) ) , 월별['비수도권%'] , color=Gray , marker='o' , label='비수도권' )
plt.plot( range( len( 월별 ) ) , 월별['수도권%'] , color=Blue , marker='o' , label='수도권' )
plt.title( '[가설 4] 가장 바쁜 1시간이 하루 평균보다 몇 % 많은가 : 수도권이 36개월 모두 더 높음' )
plt.ylabel( '하루 평균 대비 (%)' )
plt.xticks( 위치 , 라벨 )
plt.legend()
plt.grid( axis='y' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './region/images/H4_피크집중도.png' , dpi=150 )
plt.show()

# 그래프 4-2] 두 권역의 차이 ( 수도권 − 비수도권 )
plt.figure( figsize=( 10 , 4 ) )
plt.bar( range( len( 월별 ) ) , 월별['차이'] , color=Blue )
plt.title( '[가설 4] 수도권 − 비수도권 피크 집중도 차이 : 36개월 모두 0보다 큼' )
plt.ylabel( '차이 (%p)' )
plt.xticks( 위치 , 라벨 )
plt.grid( axis='y' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './region/images/H4_피크집중도_차이.png' , dpi=150 )
plt.show()

print( '\n[ 월별 차이 ] 최소' , round( np.min( 월별['차이'] ) , 1 ) , '%p / 최대' , round( np.max( 월별['차이'] ) , 1 ) , '%p / 0보다 큰 달' , ( 월별['차이'] > 0 ).sum() , '/' , len( 월별 ) )

# 7] 판정 출력 ( 보고서 Ⅴ장 표에 사용 )
print( '\n========== 가설 3 : 수도권 사용량 비중 40% 이상 ==========' )
for i in range( len( 연도별 ) ) :
    연도 = 연도별['연도'][i]
    비중 = 연도별['비중'][i]
    print( 연도 , '년 : 수도권 비중' , 비중 , '% ( 기준과 차이' , round( 비중 - 40 , 1 ) , '%p )' )

H3평균 = 일별['수도권비중'].mean()
넘은날 = ( 일별['수도권비중'] >= 40 ).sum()
print( '3년 일별 평균 :' , round( H3평균 , 1 ) , '%' )
print( '가장 높은 날 :' , round( np.max( 일별['수도권비중'] ) , 1 ) , '% / 가장 낮은 날 :' , round( np.min( 일별['수도권비중'] ) , 1 ) , '%' )
print( '40% 이상인 날 :' , 넘은날 , '/' , len( 일별 ) , '일 (' , round( 넘은날 / len( 일별 ) * 100 , 1 ) , '% )' )

넘은연도 = ( 연도별['비중'] >= 40 ).sum()
H3판정 = '채택' if 넘은연도 == len( 연도별 ) else '기각'   # 3년 모두 40% 이상이어야 채택
print( '> 판정 :' , H3판정 )

print( '\n========== 가설 4 : 수도권 피크 집중도 > 비수도권 ==========' )
수평균 = 집중도['수도권'].mean()
비평균 = 집중도['비수도권'].mean()
print( '전체 : 수도권' , round( 수평균 , 3 ) , '배 / 비수도권' , round( 비평균 , 3 ) , '배 / 차이' , round( 수평균 - 비평균 , 3 ) )

# 연도별
연도집중 = 집중도.groupby( '연도' ).agg( 수도권=( '수도권' , 'mean' ) , 비수도권=( '비수도권' , 'mean' ) ).round( 3 )
print( '\n[ 연도별 ]' )
print( 연도집중 )

# 계절별 ( 봄 3~5월 , 여름 6~8월 , 가을 9~11월 , 겨울 12~2월 )
집중도['계절'] = np.where( ( 집중도['월'] >= 3 ) & ( 집중도['월'] <= 5 ) , '봄' ,
                 np.where( ( 집중도['월'] >= 6 ) & ( 집중도['월'] <= 8 ) , '여름' ,
                 np.where( ( 집중도['월'] >= 9 ) & ( 집중도['월'] <= 11 ) , '가을' , '겨울' ) ) )
계절집중 = 집중도.groupby( '계절' ).agg( 수도권=( '수도권' , 'mean' ) , 비수도권=( '비수도권' , 'mean' ) ).round( 3 )
print( '\n[ 계절별 ]' )
print( 계절집중 )

높은날 = ( 집중도['수도권'] > 집중도['비수도권'] ).sum()
print( '\n수도권이 더 높은 날 :' , 높은날 , '/' , len( 집중도 ) , '일 (' , round( 높은날 / len( 집중도 ) * 100 , 1 ) , '% )' )
H4판정 = '채택' if 수평균 > 비평균 else '기각'
print( '> 판정 :' , H4판정 )

# 8] 한눈에 요약
print( '\n========== 요약 ==========' )
print( 'H3' , H3판정 , ': 수도권 비중 3년 평균' , round( H3평균 , 1 ) , '% ( 기준 40% )' )
print( 'H4' , H4판정 , ': 피크 집중도 수도권' , round( 수평균 , 3 ) , '배 vs 비수도권' , round( 비평균 , 3 ) , '배 ,' ,
       높은날 , '/' , len( 집중도 ) , '일 수도권이 높음' )