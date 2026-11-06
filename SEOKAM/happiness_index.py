import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import requests
import pandas as pd

df_2022 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20221231.csv', encoding='cp949')
df_2023 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20231231.csv', encoding='cp949')
df_2024 = pd.read_csv('한국전력거래소_시간별 전국 전력수요량_20241231.csv', encoding='cp949')

print(df_2024.info())
