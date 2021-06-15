# #
import pvlib
import pandas as pd

# ## browse data base ##################

df1 = pvlib.pvsystem.retrieve_sam('CECMod')
df2 = pvlib.pvsystem.retrieve_sam('SandiaMod')
# SF AT 360-72M DG-B

for df in [df1, df2]:
    cols = []
    for col in df.columns:
        if (
            ('SF' in col) and
            (('AT' in col) or ('DG B' in col) or ('DG-B' in col))
           ):
            cols += [col]
    print(cols)
