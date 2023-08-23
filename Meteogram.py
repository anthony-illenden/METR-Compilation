import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl

def roundup(x, base=5):
    x = x + 5
    base = base * round(x/base)
    return base 

def rounddown(x, base=5):
    x = x - 5
    base = base * round(x/base)
    return base

now = datetime.datetime.utcnow()

yesterday = now - datetime.timedelta(days=1)
tomorrow = now + datetime.timedelta(days=1)

month1 = str(yesterday.month).zfill(2)
day1 = str(yesterday.day).zfill(2)
year1 = str(yesterday.year)

month2 = str(tomorrow.month).zfill(2)
day2 = str(tomorrow.day).zfill(2)
year2 = str(tomorrow.year)

station = 'KVLL'

url = 'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?' + \
      'station=' + station + \
      '&data=all&year1=' + year1 + '&month1=' + month1 +'&day1=' + day1 + \
      '&year2=' + year2 +'&month2=' + month2 +'&day2=' + day2 + \
      '&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=no&missing=M&trace=T&direct=no&report_type=1&report_type=3&report_type=4'

df = pd.read_csv(url)

df['Time'] = pd.to_datetime(df['valid']).dt.strftime('%H:%M')
df['Date'] = pd.to_datetime(df['valid']).dt.strftime('%m-%d %H:%M')


fig, ax = plt.subplots()

ax.plot(df['Date'], df['tmpf'], c='darkred', label='air')
ax.plot(df['Date'], df['dwpf'], c='green', label='dew')

ax.fill_between(range(len(df['tmpf'])), df['tmpf'], color='lightcoral')
ax.fill_between(range(len(df['dwpf'])), df['dwpf'], color='lightgreen')

plt.xticks(range(0, len(df['Time']), 9), fontsize=8, rotation=30)

ax.set_xlim(df['Date'].iloc[0], df['Date'].iloc[-1])
#ax.set_ylim(0)
ax.set_ylim(rounddown(df['dwpf'].min()), roundup(df['tmpf'].max()))
ax.grid(color='gray', axis='y', linestyle='-', zorder=0)
ax.set_xlabel("Date time")
ax.set_ylabel("Temperature")

#ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d\n%H:%M'))

plt.title(station + ' ASOS data from ' + df['Date'].iloc[0] + " to " + df['Date'].iloc[-1])

