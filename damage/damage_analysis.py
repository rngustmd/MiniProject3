# 피해 파트 분석 및 시각화
# 그래프 저장 위치 : ./damage/images/

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False   # 마이너스 기호 깨짐 방지
plt.rcParams['axes.spines.top'] = False      # 위·오른쪽 테두리 없애서 깔끔하게
plt.rcParams['axes.spines.right'] = False
pd.set_option('display.unicode.east_asian_width', True)

df1 = pd.read_csv( './damage/damage_data/1_피해경험률_연도별.csv' )
df3 = pd.read_csv( './damage/damage_data/3_피해경험률_학교급_연도별.csv' )
df4 = pd.read_csv( './damage/damage_data/4_피해유형_연도별.csv' )
df5 = pd.read_csv( './damage/damage_data/5_피해경로_연도별.csv' )
df6 = pd.read_csv( './damage/damage_data/6_가해자_모르는사람_연도별.csv' )
df7 = pd.read_csv( './damage/damage_data/7_피해경험률_이용시간_연도별.csv' )
df8 = pd.read_csv( './damage/damage_data/8_피해경험률_예방교육_연도별.csv' )

# 그래프 색깔
Blue = '#2a78d6'
Orange = '#eb6834'
Green = '#1baf7a'
Gray = '#8a8984'

# 1] 피해 경험률 추이 : 선 그래프
plt.figure( figsize=( 8 , 4 ) )
plt.plot( df1['연도'] , df1['피해경험률'] , color=Blue , linewidth=2 , marker='o' , markersize=8 )
for i in range( len( df1 ) ) : 
    plt.text( df1['연도'][i] , df1['피해경험률'][i] + 1.2 , str( df1['피해경험률'][i] ) + '%' , ha='center' )
plt.title( '청소년 사이버폭력 피해 경험률 추이' )
plt.xticks( df1['연도'] )
plt.ylabel( '피해 경험률(%)' )
plt.ylim( 0 , 45 )
plt.grid( axis='y' , alpha = 0.3 )
plt.tight_layout()
plt.savefig('./damage/images/EDA1_피해경험률_추이.png' , dpi=150 )
plt.show()

# 2] 2024년 피해 유형 : 가로 막대
category = df4[ df4['연도'] == 2024 ]
category = category.drop( columns='연도')
category = category.T
category.columns = [ '경험률' ]
category = category.sort_values( '경험률' )
print( category )

plt.figure( figsize=( 8 , 4 ) )
plt.barh( category.index , category['경험률'] , color=Blue , height=0.6 )
for i in range( len( category ) ) :
    plt.text( category['경험률'].iloc[i] + 0.4 , i , str( category['경험률'].iloc[i] ) + '%' , va='center' )
plt.title( '2024년 청소년 사이버폭력 피해 유형별 경험률' )
plt.xlabel( '경험률(%)' )
plt.grid( axis='x' , alpha=0.3)
plt.tight_layout()
plt.savefig( './damage/images/EDA2_피해유형_2024.png' , dpi=150)
plt.show()

# 3] 학교급별 피해 경험률 추이 : 선 3개
plt.figure( figsize=( 8 , 4 ) )
elementary = df3[ df3['학교급'] == '초등학교' ]
middle = df3[ df3['학교급'] == '중학교' ]
high = df3[ df3['학교급'] == '고등학교' ]

plt.plot( elementary['연도'] , elementary['피해경험률'] , color=Blue , linewidth=2 , marker='o' , label='초등학교')
plt.plot( middle['연도'] , middle['피해경험률'] , color=Orange , linewidth=2 , marker='o' , label='중학교')
plt.plot( high['연도'] , high['피해경험률'] , color=Green , linewidth=2 , marker='o' , label='고등학교')
plt.title( '학교급별 사이버폭력 피해 경험률 추이' )
plt.xticks( [ 2020 , 2021 , 2022 , 2023 , 2024 ] )
plt.xlim( 2019.7 , 2025.0 )
plt.ylabel( '피해 경험률(%)' )
plt.ylim( 0 , 50 )
plt.legend( loc='upper left' , frameon=False )
plt.grid( axis='y' , alpha=0.3 )
plt.tight_layout()
plt.savefig( './damage/images/EDA3_학교급_추이.png' , dpi=150 )
plt.show()