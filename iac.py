import pandas as pd
import requests
import datetime as dt
import csv
import numpy as np
import matplotlib.pyplot as plt
import psycopg2 as ps
import re

DB_NAME = 'iac_task'
DB_USER = 'postgres'
DB_PASS = 'password'
DB_HOST = 'localhost'
DB_PORT = '5432'

beg_day = dt.date.today()
end_day = beg_day + dt.timedelta(days=7)

i = 1
has_later = False
end_cycle = False

final_df = pd.DataFrame()

while (True):
    tables = pd.read_html(f'https://rosseti-lenenergo.ru/planned_work/?PAGEN_1={i}')
    df = tables[1] # искомая таблица - вторая на странице
    
    for j in range(len(df.index)):
        date_object = dt.datetime.strptime(df.iloc[j][4], '%d-%m-%Y').date()
        if date_object > end_day:
            has_later = True
            later_index = j
        if date_object < beg_day:
            end_cycle = True
            earlier_index = j
            break

    if has_later:
        df.drop(df.index[:later_index+1], inplace=True)
    if end_cycle:
        df.drop(df.index[later_index:], inplace=True)
        
    
    final_df = df if i == 1 else pd.concat([final_df, df], ignore_index=True)
    
    i += 1
    has_later = False

    if end_cycle:
        break

final_df.dropna(subset=[('Улица', 'Улица')], inplace=True)
final_df = final_df[final_df[('Регион РФ(область, край, город фед. значения, округ)', 'Регион РФ(область, край, город фед. значения, округ)')] != 'Ленинградская область']

# for database

conn = ps.connect(database=DB_NAME,
                  user=DB_USER,
                  password=DB_PASS,
                  host=DB_HOST,
                  port=DB_PORT)

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS info 
            (building_id INT, 
             longitude FLOAT, 
             latitude FLOAT, 
             district_id INT)""")

conn.commit()

street = ''
house = ''
corp = ''
same_house_i = -1
num_points = 0
for j in range(len(final_df.index)):
    ls = re.split(r'[,;]', final_df.iloc[j][3])
    for i in range(len(ls)):
        try:
            if ls[i][0] == ' ':
                ls[i] = ls[i][1:]
        except:
            continue

    for i in range(len(ls)):
        if len(ls[i]) > 0 and same_house_i != i:
            ls[i] = ls[i].replace('Санкт-Петербург', '')
            try:
                if ls[i][0] == 'д' or ls[i][0].isdigit():
                    house = ls[i]
                    if i != len(ls) - 1 and ls[i+1][0] == 'к':
                        corp = ls[i+1]
                        same_house_i = i + 1
                    else:
                        corp = ''
                elif ls[i][0] == 'к':
                    corp = ls[i]
                else:
                    street = ls[i]
                    house = ''
                    corp = ''
            except:
                continue

        if house != '':
            api_url = f"https://geocode.gate.petersburg.ru/parse/free?street='{street + ' ' + house + ' ' + corp}'"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if 'Building_ID' in data:
                    plt.scatter(np.array([data['Longitude']]), np.array([data['Latitude']]), c='red', s=3.0)
                    num_points += 1
                    cur.execute(f"""INSERT INTO info VALUES 
                                ({data['Building_ID']}, 
                                 {data['Longitude']}, 
                                 {data['Latitude']},
                                 {data['District_ID']})""")
                    conn.commit()

print(f'{num_points} points')
print("Houses' coordinates:")
plt.show()

cur.close()
conn.close()