
# 라이브러리 호출
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
import matplotlib
matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 1. 📂 데이터 불러오기 및 전처리

# [1-1] 데이터프레임으로 불러오기
df_raw = pd.read_excel("서울대기오염_2019.xlsx", sheet_name="Sheet1")
# (스프레드시트를 엑셀 파일로 저장해 불러옴)
# [1-2] 분석변수만 추출 및 컬럼명 변경: date, district, pm10, pm25
df = df_raw[['날짜', '측정소명', '미세먼지', '초미세먼지']].copy()
df.columns = ['date', 'district', 'pm10', 'pm25']
# [1-3] 결측치 확인 및 제거 (결측치 + 이상치 각각)
# print("결측치 개수:\n", df.isnull().sum()) 통해 사전 확인
df = df.dropna(subset=['date', 'district']) # 필수인 열들 - 결측치 제거
df['pm10'] = df['pm10'].fillna(df['pm10'].mean()) # 평균값 대체
df['pm25'] = df['pm25'].fillna(df['pm25'].mean()) # 평균값 대체
cond_pm10 = (df['pm10'] >= 0) & (df['pm10'] <= 600) # 이상치 제거 (0~600 살림)
cond_pm25 = (df['pm25'] >= 0) & (df['pm25'] <= 300) # 이상치 제거 (0~300 살림)
df = df[cond_pm10 & cond_pm25]
# [1-4] 자료형 변환: 문자형 → 날짜형, 실수형 등
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['pm10'] = pd.to_numeric(df['pm10'], errors='coerce')
df['pm25'] = pd.to_numeric(df['pm25'], errors='coerce')

# 2. 🧪 파생변수 만들기
# [2-1] month, day 파생변수 생성
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
# [2-2] 계절(season) 변수 생성: month 기준으로 spring/summer/autumn/winter
def get_season(month):
    if month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10, 11]:
        return 'autumn'
    else:
        return 'winter'
df['season'] = df['month'].apply(get_season)

# 3. ✅ 전처리 완료 데이터 확인 및 저장
# [3-1] 최종 분석 대상 데이터 확인
final_df = df.copy()
# [3-2] 'card_output.csv'로 저장
final_df.to_csv("card_output.csv", index=False)

# 4. 🔹 연간 미세먼지 평균 구하기
# [4-1] 전체 데이터 기준 PM10 평균
avg_pm10 = final_df['pm10'].mean()
print("평균 PM10:", round(avg_pm10, 2))
# 분석결과: 평균 PM10 수치는 약 41.75㎍/m³이고, 보통 등급에 해당함

# 5. 🔹 미세먼지 최댓값 날짜 확인
# [5-1] PM10 최댓값이 발생한 날짜, 구 출력
max_pm10_row = final_df.loc[final_df['pm10'].idxmax()]
print("PM10 최댓값 날짜:", max_pm10_row['date'])
print("PM10 최댓값 구:", max_pm10_row['district'])
# 분석결과: PM10 최댓값은 강북구에서 2019-03-05일에 발생했음

# 6. 🔹 구별 PM10 평균 비교
# [6-1] 각 구별 pm10 평균 계산
district_avg_pm10 = final_df.groupby('district')['pm10'].mean().reset_index(name='avg_pm10')
# [6-2] 상위 5개 구만 출력
top5_districts = district_avg_pm10.sort_values(by='avg_pm10', ascending=False).head(5)
print(top5_districts)
# 분석결과: 관악구, 양천구, 마포구, 강서구, 강북구에서 순서대로 평균 PM10 수치가 높게 나타남 

# 7. 🔹 계절별 PM10/PM2.5 평균 비교
# [7-1] 계절별 평균 pm10, pm2.5 동시 출력
season_avg = final_df.groupby('season')[['pm10', 'pm25']].mean().reset_index()
season_avg.columns = ['season', 'avg_pm10', 'avg_pm25']
# [7-2] 평균값 기준 오름차순 정렬
season_avg = season_avg.sort_values(by='avg_pm10')
print(season_avg)
# 분석결과: 봄/겨울에 미세먼지 수치가 가장 높고 여름에 가장 낮음. 초미세먼지는 겨울에 가장 높고 가을에 가장 낮음

# 8. 🔹 PM10 등급(pm_grade) 분류 및 분포 확인
# [8-1] pm10 값을 기준으로 등급 분류 (good/normal/bad/worse)
def classify_pm10(value):
    if value <= 30:
        return 'good'
    elif value <= 80:
        return 'normal'
    elif value <= 150:
        return 'bad'
    else:
        return 'worse'
final_df['pm_grade'] = final_df['pm10'].apply(classify_pm10)
# [8-2] 전체 데이터 기준 등급별 빈도, 비율 계산
grade_dist = final_df['pm_grade'].value_counts().reset_index()
grade_dist.columns = ['pm_grade', 'n']
grade_dist['pct'] = round((grade_dist['n'] / grade_dist['n'].sum()) * 100, 2)
print(grade_dist)
# 분석결과: 'normal' 등급이 가장 많고, 'good'이 다음으로 많음. 'worse'는 거의 없음

# 9. 🔹 구별 good 등급 비율 상위 5개 구 추출
# [9-1] good 빈도 및 비율 계산
district_grade = final_df.groupby(['district', 'pm_grade']).size().unstack(fill_value=0)
district_grade['total'] = district_grade.sum(axis=1)
district_grade['good_pct'] = (district_grade['good'] / district_grade['total']) * 100
# [9-2] 비율 기준 내림차순 정렬 후 상위 5개 구 출력
top5_good = district_grade[['good', 'good_pct']].sort_values(by='good_pct', ascending=False).head(5).reset_index()
top5_good.columns = ['district', 'n', 'pct']
print(top5_good)
# 분석결과: 용산구, 중구, 종로구, 도봉구, 금천구가 순서대로 good 등급 비율이 높음

# 10. 📉 1년간 일별 미세먼지 추이 그래프
# [10-1] x축: date, y축: pm10 (선그래프)
plt.figure(figsize=(14, 5))
sns.lineplot(data=final_df, x='date', y='pm10', label='PM10')
plt.title('Daily Trend of PM10 in Seoul, 2019')
plt.xlabel('Date')
plt.ylabel('PM10 (㎍/m³)')
plt.grid(True)
plt.tight_layout()
plt.show()
# 분석결과: 1~2월, 3월에 최고치를 찍으며 급증하는 모습을 보이고, 여름은 대체적으로 낮은 수치륿 보임

# 11. 📊 계절별 PM10 등급 비율 그래프
# [11-1] x축: season, y축: pct, fill: pm_grade
season_grade_dist = final_df.groupby(['season', 'pm_grade']).size().reset_index(name='n')
season_totals = season_grade_dist.groupby('season')['n'].transform('sum')
season_grade_dist['pct'] = (season_grade_dist['n'] / season_totals) * 100
# [11-2] seaborn barplot
plt.figure(figsize=(10, 6))
sns.barplot(data=season_grade_dist, x='season', y='pct', hue='pm_grade')
plt.title('Seasonal Distribution of PM10 Grades in Seoul, 2019')
plt.ylabel('비율 (%)')
plt.xlabel('계절')
plt.legend(title='PM10 등급', loc='upper right')
plt.tight_layout()
plt.show()
# 분석결과: 봄, 겨울에는 'normal' 등급의 비율이 가장 높고, 여름과 가을에는 'good' 등급 비욜이 가장 높음
