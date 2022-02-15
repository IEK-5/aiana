   def plot_ground_heatmap(
        self,
        df: pd.DataFrame = None,
        destination_folder: Path = None,
        file_name: str = None,
        cm_unit: str = None,
        cumulative: bool = None,
        df_col_limits: pd.DataFrame = None
    ):
        """plots the ground insolation as a heat map and saves it into
            the results/plots folder.

        Args:
            df (pd.DataFrame): if None, a df is created
            from the csv file name stored in an instance of this class.
            Defaults to None.

            df_col_limits (pd.DataFrame): with same columns as in df with a min
            and max row (as e.g. returned by df_concatenated.agg([min, max]))
            to be used as color bar limits.
            Defaults to None.
        """
        if df is None:
            df = fi.df_from_file_or_folder(str(self.csv_file_path))
        if cm_unit is None:
            cm_unit = self.settings.sim.cm_quantity

        if cumulative is None:
            cumulative = self.settings.sim.cumulative

        ticklabels_skip_count_number = int(
            round(self.ghObj.x_field, 0)
            / (8*self.settings.sim.spatial_resolution))
        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        label_and_cm_input: dict = self.evalObj.get_label_and_cm_input(
            cm_unit=cm_unit, cumulative=cumulative,
            df_col_limits=df_col_limits)

        fig = plotting.plot_heatmap(
            df=df, x='x', y='y', c=label_and_cm_input['z'],
            cm=label_and_cm_input['colormap'],
            x_label='x [m]', y_label='y [m]',
            z_label=label_and_cm_input['z_label'],
            plot_title=self.return_plot_title(cumulative),
            ticklabels_skip_count_number=ticklabels_skip_count_number,
            vmin=label_and_cm_input['vmin'],
            vmax=label_and_cm_input['vmax'],
        )

        fig.axes[1] = plotting.add_north_arrow(
            fig.axes[1], self.settings.apv.sceneDict['azimuth'])

        if file_name is None:
            file_name = self.file_name

        if destination_folder is None:
            destination_folder = self.results_subfolder
        fi.save_fig(
            fig,
            cm_unit+'_'+file_name,
            parent_folder_path=destination_folder,
            sub_folder_name='',
        )

    def return_weather_description(self):
        if self.settings.sim.TMY_irradiance_aggfunc == 'min':
            return 'max cloudy'
        if self.settings.sim.TMY_irradiance_aggfunc == 'mean':
            return 'mean cloudy'
        if self.settings.sim.TMY_irradiance_aggfunc == 'max':
            return 'clear sky'  # TODO take clear_sky values then?

    def return_plot_title(self, cumulative: bool, title_comps=None) -> str:
        if title_comps is None:
            title_comps = self.settings.sim.plot_title_components
        title = ''
        if 'weather' in title_comps:
            title += f'Weather: {self.return_weather_description()}\n'
        if 'agg_func' in title_comps:  # redundant to weather
            title += (f'TMY aggregation function: '
                      f'{self.settings.sim.TMY_irradiance_aggfunc}\n')
        if 'resolution' in title_comps:
            title += f'Resolution: {self.settings.sim.spatial_resolution} m\n'
        if 'position' in title_comps:
            title += f'Scanned Position: {self.settings.sim.position}\n'
        if 'module_form' in title_comps:
            title += f'Module Form: {self.settings.apv.module_form}'
        if 'datetime' in title_comps:
            if self.settings.sim.sky_gen_mode == 'gendaylit' and not cumulative:
                title += f'\nDate & Time: {self.settings.sim.sim_date_time}'
            else:
                title += (f'\nFrom: [{self.settings.sim.startdt}] '
                          f'To: [{self.settings.sim.enddt}]')
        return title
