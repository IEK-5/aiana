# Overview

number of code lines 2.11.2021

648	br_wrapper.py
559	classes/weather_data.py
456	classes/geometries_handler.py
407	classes/APV_evaluation.py
201	utils/plots.py
182	examples/Typical_days_loop.py
181	settings/apv_systems.py
166	utils/files_interface.py
129	examples/debug_geometry.py
106	examples/full_day_morschenich.py
99	classes/sim_datetime.py
79	settings/simulation.py
67	utils/pvlib_wrapper_for_PVGRIP.py
58	utils/time.py
57	examples/checked_board.py
52	utils/evaluation.py
44	examples/dni_dhi_tests.py
43	utils/settings_adjuster.py
40	examples/declined_tables.py
31	apv_main.py
25	examples/declined_tables2.py
19	utils/browse_PVlib_modules.py
15	settings/user_pathes.py
10	resources/locations.py
5	utils/init.py
4	classes/init.py
3	settings/init.py
2	utils/pycache/.gitignore
1	resources/init.py

3693 total



# HOW TO install the package in vscode

- make sure that the file path in the terminal ist the one of the
package folder (agri-pv), in which "setup.py" is localized. If you have several folders in your workspace right click agri-pv and choose "Open in Integrated Terminal"

- run command:

      pip install -e .

- restart vscode

- if this did not help, try
    pip uninstall apv
    restart
    pip install -e .



replace this function in bifacial_radiance.main.py:

    def analysis(
            self, octfile, name, frontscan, backscan, groundscan=None, plotflag=False,
            accuracy='low', hpc=False):
        """
        General analysis function, where linepts are passed in for calling the
        raytrace routine :py:class:`~bifacial_radiance.AnalysisObj._irrPlot`
        and saved into results with
        :py:class:`~bifacial_radiance.AnalysisObj._saveResults`.

        This function can also pass in the linepts structure of the view
        along with a title string for the plots note that the plots appear in
        a blocking way unless you call pylab magic in the beginning

        Parameters
        ------------
        name : string
            Name to append to output files
        octfile : string
            Filename and extension of .oct file
        frontscan : scene.frontscan object
            Object with the sensor location information for the
            front of the module
        backscan : scene.backscan object
            Object with the sensor location information for the
            rear side of the module
        plotflag : boolean
            Include plot of resulting irradiance
        accuracy : string
            Either 'low' (default - faster) or 'high' (better for low light)

        Returns
        -------
         File saved in `\\results\\irr_name.csv`

        """
        if octfile is None:
            print('Analysis aborted - no octfile \n')
            return None, None

        if groundscan == None:
            linepts = self._linePtsMakeDict(frontscan)
            frontDict = self._irrPlot(octfile, linepts, name+'_Front',
                                      plotflag=plotflag, accuracy=accuracy, hpc=hpc)

            linepts = self._linePtsMakeDict(backscan)
            backDict = self._irrPlot(octfile, linepts, name+'_Back',
                                     plotflag=plotflag, accuracy=accuracy, hpc=hpc)
        else:
            linepts = self._linePtsMakeDict(groundscan)
            frontDict = self._irrPlot(octfile, linepts, name+'_Ground',
                                      plotflag=plotflag, accuracy=accuracy, hpc=hpc)
            backDict = None

        # don't save if _irrPlot returns an empty file.
        if frontDict is not None:
            self._saveResults(frontDict, backDict, 'irr_%s.csv' % (name))

        return frontDict, backDict