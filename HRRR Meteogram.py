from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates

from siphon.catalog import TDSCatalog 

def temp(tairK):
    tairF = (tairK - 273.15) * 1.8 + 32
    return tairF

def roundup(x, base=5):
    x = x + 5
    base = base * round(x/base)
    return base 

def rounddown(x, base=5):
    x = x - 5
    base = base * round(x/base)
    return base

hrrr_catalog = ('https://thredds-test.unidata.ucar.edu/thredds/catalog/grib/NCEP/HRRR/CONUS_2p5km/latest.xml')

cat = TDSCatalog(hrrr_catalog)

ncss = cat.datasets[0].subset()
print(ncss.variables)

point_query = ncss.query()
point_query.time_range(datetime.utcnow(), datetime.utcnow() + timedelta(hours=18))
point_query.accept('csv') 
point_query.variables('Temperature_isobaric', 'Dewpoint_temperature_isobaric')
point_query.lonlat_point(-83.160449, 42.654588)
point_data = ncss.get_data(point_query)
print(point_data) 

df = pd.DataFrame(point_data)
print(df.head())

for index, row in df.iterrows():
    # Check if the cell value in a specific column is not equal to the desired value
    if row['alt'] != 100000:
        # Delete the entire row using the index
        df = df.drop(index)
        
df = df.reset_index(drop=True)

hours = np.arange(len(df)) * 1
print(hours)

df['Hours'] = hours

## Test

now = datetime.utcnow() - timedelta(hours=4)



df['hours'] = df['Hours']
df['hours'] = pd.to_timedelta(df['hours'], unit='h')
current_time = pd.to_datetime('now') - timedelta(hours=4)
df['future_time'] = current_time + df['hours']
df['future_time'] = df['future_time'].dt.strftime('%I:%M %p')

##

df['TairF']  = temp(df['Temperature_isobaric'])
df['Dewpf'] = temp(df['Dewpoint_temperature_isobaric'])

fig, (ax) = plt.subplots(nrows=1)
ax.plot(df['future_time'], df['TairF'], c='red')
ax.plot(df['future_time'], df['Dewpf'], c='green')

ax.fill_between(range(len(df['TairF'])), df['TairF'], color='lightcoral')
ax.fill_between(range(len(df['Dewpf'])), df['Dewpf'], color='lightgreen')

ax.set_xlim(df['Hours'].iat[0], df['Hours'].iat[-1])
ax.set_ylim(rounddown(df['Dewpf'].min()), roundup(df['TairF'].max()))
ax.grid(color='gray', axis='y', linestyle='-', zorder=0)
ax.set_xlabel("Date time")
ax.set_ylabel("Temperature (F)")
plt.xticks(rotation = 45)
#ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
plt.title('HRRR forecasted Air and Dewpoint Temperatures')
