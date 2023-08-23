# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:53:30 2023

@author: Tony
"""

import pandas as pd
import urllib.request
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units
import numpy as np
import re
from datetime import date

url = "https://sharp.weather.ou.edu/soundings/acars/2023/07/02/16/YNN_1620.txt"

with urllib.request.urlopen(url) as response:
    data = response.read().decode('utf-8')

start_pos = data.find("%RAW%") + len("%RAW%")
end_pos = data.find("%END%")

data_section = data[start_pos:end_pos].strip()

lines = data_section.split('\n')

lines = lines[1:]

df = pd.DataFrame()

for line in lines:
    line = line.strip()
    if line:
        values = line.split(',')
        temp_df = pd.DataFrame([values], columns=['LEVEL', 'HGHT', 'TEMP', 'DWPT', 'WDIR', 'WSPD'])
        df = df.append(temp_df, ignore_index=True)

df = df.apply(pd.to_numeric, errors='coerce')

print(df)


for i in url:
    match = re.search(r"/([A-Z]+)_([0-9]+)\.txt$", url)
    if match:
        city = match.group(1)
        time = match.group(2)

p = df['LEVEL'].values * units.hPa
T = df['TEMP'].values * units.degC
Td = df['DWPT'].values * units.degC
wind_speed = df['WSPD'].values * units.knots
wind_dir = df['WDIR'].values * units.degrees

ml_cape, ml_cin = mpcalc.mixed_layer_cape_cin(p, T, Td, depth=50 * units.hPa)
u, v = mpcalc.wind_components(wind_speed, wind_dir)

prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')


pressure = np.arange(1000, 499, -50) * units('hPa')
mixing_ratio = np.array([0.1, 0.2, 0.4, 0.6, 1, 1.5, 2, 3, 4,
                        6, 8, 10, 13, 16, 20, 25, 30, 36, 42]).reshape(-1, 1) * units('g/kg')

ds = mpcalc.parcel_profile_with_lcl_as_dataset(p, T, Td)

fig = plt.figure(figsize=(9, 9))
skew = SkewT(fig)

skew.plot(df['LEVEL'], df['TEMP'], 'r', linewidth=2)
skew.plot(df['LEVEL'], df['DWPT'], 'g', linewidth=2)
skew.plot_barbs(p[::2], u[::2], v[::2])
skew.plot(ds.isobaric, ds.parcel_temperature.metpy.convert_units('degC'), 'black', linestyle = '--', linewidth=2)
skew.shade_cin(p, T, prof, Td)
skew.shade_cape(p, T, prof)


wb = mpcalc.wet_bulb_temperature(p, T, Td).to('degC')
skew.plot(p, wb, 'lightskyblue', label='Wetbulb Temperature')

skew.plot_dry_adiabats(t0=np.arange(233, 533, 10) * units.K, alpha=0.25,
                       colors='orangered', linewidths=1)
skew.plot_moist_adiabats(t0=np.arange(233, 400, 5) * units.K, alpha=0.25,
                         colors='tab:green', linewidths=1)
skew.plot_mixing_lines(pressure=pressure, mixing_ratio=mixing_ratio, linestyles='dotted',
                       colors='dodgerblue', linewidths=1)

plt.xlabel("Temperature (C)")
plt.ylabel("Pressure (mb)")
plt.title(city + ' ACARS', loc='left')
plt.title(str(date.today()) + ' ' + time + ' UTC', loc='right')

ax_hod = inset_axes(skew.ax, '40%', '40%', loc=1)
h = Hodograph(ax_hod, component_range=80.)
h.add_grid(increment=20)
h.plot_colormapped(u, v, wind_speed)
