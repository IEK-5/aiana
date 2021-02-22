import xarray as xr

ds = xr.open_dataset('download.nc')
df = ds.to_dataframe()

df