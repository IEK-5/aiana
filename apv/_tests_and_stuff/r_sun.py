# #
import grass as gs

def run_solar_radiation(scanned_elev, env, **kwargs):
    # convert date to day of year
    import datetime
    doy = datetime.datetime(2016, 5, 2).timetuple().tm_yday
    # precompute slope and aspect
    gs.run_command('r.slope.aspect', elevation=scanned_elev, slope='slope', aspect='aspect', env=env)
    gs.run_command('r.sun', elevation=scanned_elev, slope='slope', aspect='aspect', beam_rad='beam', step=1, day=doy, env=env)
    gs.run_command('r.colors', map='beam', color='grey', flags='e')
    
    grass.