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