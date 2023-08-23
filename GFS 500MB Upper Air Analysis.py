from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
import metpy.calc as mpcalc

def find_time_var(var, time_basename='time'):
    for coord_name in var.coordinates.split():
        if coord_name.startswith(time_basename):
            return coord_name
    raise ValueError('No time variable found for ' + var.name)
    
catalog_url = 'https://thredds-test.unidata.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p25deg/catalog.xml'
dataset_name = 'Best GFS Quarter Degree Forecast Time Series'
cat = TDSCatalog(catalog_url)
dataset = cat.datasets[dataset_name]
ncss = dataset.subset()
query = ncss.query()
query.lonlat_box(north=55, south=30, east=-70, west=-115).time(datetime.utcnow() + timedelta(hours=176))
query.accept('netcdf4')

print(ncss.variables)

query.variables('Temperature_isobaric','Geopotential_height_isobaric', 'u-component_of_wind_isobaric', 'v-component_of_wind_isobaric')
query.vertical_level(50000)

data = ncss.get_data(query)

temp_var = data.variables['Temperature_isobaric']
gph_var = data.variables['Geopotential_height_isobaric']
u_wind_var500 = data.variables['u-component_of_wind_isobaric'][:] * units('m/s')
v_wind_var500 = data.variables['v-component_of_wind_isobaric'][:] * units('m/s')
time_var = data.variables[find_time_var(temp_var)]
lat_var = data.variables['latitude']
lon_var = data.variables['longitude']

temp = temp_var[:].squeeze()
lat = lat_var[:].squeeze()
lon = lon_var[:].squeeze()
gph_var = gph_var[:].squeeze()
u_wind500 = u_wind_var500[:].squeeze()
v_wind500 = v_wind_var500[:].squeeze()

temp = units.Quantity(temp, 'kelvin')
temp = temp.to('degC')

u_wind500 = units.Quantity(u_wind500, 'm/s')
v_wind500 = units.Quantity(v_wind500, 'm/s')

wnd = mpcalc.wind_speed(u_wind500, v_wind500)
wnd = wnd.to('kt')

time = num2date(time_var[:].squeeze(), time_var.units)

lon_2d, lat_2d = np.meshgrid(lon, lat)

gph = ndimage.gaussian_filter(gph_var, sigma=2, order=0)

mapcrs = ccrs.LambertConformal(central_longitude=-85.6, central_latitude=44.3, standard_parallels=(30, 60))  
datacrs = ccrs.PlateCarree() 
proj = ccrs.Stereographic(central_longitude=-85, central_latitude=40) 

fig = plt.figure(figsize=(18,12)) 
ax = fig.add_subplot(1, 1, 1, projection=mapcrs) 
  
ax.set_extent([-94, -78, 38, 52], datacrs) 

ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=2)

contour_potemp = ax.contour(lon_2d, lat_2d, gph, colors='black', transform=datacrs)
ax.clabel(contour_potemp, fontsize=12, inline=1, inline_spacing=4, fmt='%i')

cf = ax.contour(lon_2d, lat_2d, temp, range(-50, 10, 3),
                 transform=datacrs, colors='red', linestlye = '--')
ax.clabel(cf, fontsize=12, inline=1, inline_spacing=4, fmt='%i')

cf = ax.contourf(lon_2d, lat_2d, wnd, range(0, 160, 20), cmap=plt.cm.BuPu,
                 transform=datacrs)

isotach = ax.contour(lon_2d, lat_2d, wnd, range(0, 160, 20), colors='black', transform=datacrs)
ax.clabel(isotach, fontsize=12, inline=1, inline_spacing=4, fmt='%i')

plt.colorbar(cf, orientation='horizontal', pad=0, aspect=50, shrink=0.50, label = 'Isotachs (kt)')

ax.barbs(lon_2d, lat_2d, u_wind500.m, v_wind500.m, pivot='middle', color='black', regrid_shape=12, transform=datacrs, zorder=2)

plt.title('GFS 500MB: Geo. Potential Heights, Temp, and Winds', loc='left')
plt.title('{:s} UTC'.format(str(time)), loc='right')
