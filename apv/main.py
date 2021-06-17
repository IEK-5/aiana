# #
import importlib as imp
# #
import apv
import bifacial_radiance as br

if __name__ == "__main__":
    """will be shifted to br_wrapper:

    userPaths = apv.settings.UserPaths()
    simSettings = apv.settings.Simulation()
    print('checking folders')
    paths_list = [userPaths.root_folder,
                  userPaths.radiance_files_folder,
                  userPaths.results_folder,
                  userPaths.data_download_folder]
    apv.utils.files_interface.make_dirs_if_not_there(paths_list)

    print('starting simulation')
    radObj = br.RadianceObj(
        simSettings.name,
        path=userPaths.radiance_files_folder)
    radObj.setGround(simSettings.ground_albedo)
    # EPW data according lat/lon
    epwfile = radObj.getEPW(
        simSettings.apv_location.latitude,
        simSettings.apv_location.longitude)
    # read in the EPW weather data from above
    metdata = radObj.readEPW(epwfile)
    # Use this to simulate only one hour at a time.
    radObj.gendaylit(simSettings.hour_of_year)
    # radObj.genCumSky(radObj.epwfile)
    # Can use this instead of gendaylit to simulate the whole year.
    """

    df_gs = apv.utils.files_interface.df_from_file(
        apv.settings.UserPaths.results_folder / 'ground_merged.csv')

    fig = apv.utils.plots.plot_heatmap(
        df_gs, 'x', 'y', 'Wm2Ground',
        x_label='x [m]',
        y_label='y [m]',
        z_label='ground insolation [W m$^{-2}$]'
    )

    apv.utils.files_interface.save_fig(fig, 'apv_ground')


# #
