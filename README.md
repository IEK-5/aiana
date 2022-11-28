# License
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Three methods were copied and modified from bifacrial_radiance, which fall
    under the BSD 3-Clause License.


# Introduction
AIANA is an acronym for "Agrivoltaic Irradiance ANAlyzer", meaning also “everlasting bloom” in native American. It can carry out ray-tracing simulations and evaluates the results in the context of the light availibilty for plants below agrivoltaic systems.

<img src="./aiana/input-output_overview.jpg" alt="AIANA structure diagram" />

In this 5 min conference poster presentation video, the background for this package is introduced:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/pFz46pmF0vE/3.jpg)](https://www.youtube.com/watch?v=pFz46pmF0vE)

# Code structure
AIANA connects to the atmosphere data store (ADS) provided by the [Copernicus Atmosphere Monitoring Service (CAMS)](https://ads.atmosphere.copernicus.eu/#!/home) granting up-to-date and high-res satellite weather data (1 min temporal and 5 km spatial resolution for sun irradiance).

AIANA partly uses the open-source package [Bifacial_radiance](https://bifacial-radiance.readthedocs.io/en/latest/), which is a python wrapper for the ray tracer [Radiance](https://www.radiance-online.org).
To add new geometry features, such as e.g. checkerboard and roof top module shapes, automated scan area visualiza-tion, and a mounting structure parametrization, AIANA also communicates directly with Radiance. AIANA also utilizes [Accelerad](https://nljones.github.io/Accelerad/rt.html) for real-time scene inspections and for the GPU-parallelization of the ray tracing simulations.
<img src="./aiana/aiana_structure.PNG" alt="AIANA structure diagram" />
NOTE: If this package is opened in VS-code with the drawio extension, you can use the class names in the class_structure.drawio.svg file as links to the source code.




# Installation Quickguide
! Developed and tested only in Windows 10, with the VS-code IDE.

1. Installations:
    - Radiance: https://github.com/LBNL-ETA/Radiance/releases
    -> choose “Add radiance to the system PATH for current user”
(if you forget this, you can add it later by searching in windows for "Change my environment variables"
(German: "Systemumgebungsvariablen bearbeiten") and add ".../Radiance/bin" to the environment variable "Path".
If aiana cannot find Radiance, check again if the entry is realy there.)

    - Accelerad: https://github.com/nljones/Accelerad/releases/tag/Accelerad_07_beta

    - VS-code (otherwise you have to adapt this guide to your IDE): https://code.visualstudio.com/Download

    - Anaconda, recommended to handle virtual environments and package versions: https://www.anaconda.com/products/distribution/start-coding-immediately

2. Within Anaconda:
    - Virtual environments (top left): create new for "aiana", with python = 3.10
    - Home (top left): start VS-code via Anaconda within the new virtual environment.


3. Within VS-code (skip already satisfied steps):
    - Go to Extensions [Ctrl+Shift+X], install Python, and GitLens.
    - Go to Source Controll [Ctrl+Shift+G] -> Clone Repository https://github.com/IEK-5/aiana
    - Choose folder (if you  choose '~home/Documents/agri-PV', you don’t have to change UserPaths settings) -> Open -> Trust
    - Open terminal [`Strg + ö`] and run:

	    - `conda install -n aiana ipykernel --update-deps --force-reinstall` (to run cells in .py-files as in jupyter notebooks)

	    - `conda install pip` (otherwise pip command will not install packages into the virtual env!)

	    - Check with `ls` or `dir` if you are really in the folder having setup.py and run `pip install -e .`

	    - and `pip install -r requirements.txt`

4. For the weather data api access register at https://ads.atmosphere.copernicus.eu. After accepting conditions, you can see your UserIDs and API Keys in your user profiles in their web page, which you need to enter into the API_credentials.txt file, after copying it from the main folder of this repository to your PCs home directory.

4. To test Aiana, run the cells in `system_studies/example.py`

# Further / more detailed installation information:

## Installing bifacial_radiance (including Radiance):

This video shows how to install bifacial_radiance completly, including all associated software needed to fully use bifacial_radiance (not done by aiana): https://youtu.be/4A9GocfHKyM

Further information:
- [bifacial_radiance installation guide](https://bifacial-radiance.readthedocs.io/en/stable/installation.html)
- Software training: https://www.youtube.com/watch?v=1X9L-R-RVGA
- PHD defense of Ms. Pelaez: https://www.youtube.com/watch?v=11Jp7GqzLPQ
- radiance user manual: https://floyd.lbl.gov/radiance/refer/usman2.pdf

## Installing Accelerad:
Aiana utilizes accelerad for the raytracing simulation by adding the "accelerad_" suffix to the rtrace command as namend in Programs/Accelerad/bin after installation. With the bool `use_accelerad_GPU_processing` (located in `settings/simulation_settings.py`) the usage of accelerad/GPU can be turned on/off. If your GPU does not meet the accelerad requirements (see below), you have to turn it off (`False`).

Copied from [Accelerad Docs](https://nljones.github.io/Accelerad/documentation.html):
>### Before you begin
>Verify that you have a CUDA-enabled GPU with compute capability 5.0 to 7.5.
If you are unsure what GPU you have:
Right click on Computer and select Properties > Device Manager > Display adapters.
Driver version 418.81 or later is required.
>### Download
>https://github.com/nljones/Accelerad/releases/tag/Accelerad_07_beta
>### testing Accelerad installation
>To confirm that Accelerad is successfully installed on your computer, run the included Windows .bat or Unix .sh files in the demo folder. By default, this folder is located at C:\Program Files\Accelerad\demo on Windows and /usr/local/accelerad/demo on Linux.
Running test_accelerad_rpict should produce a high dynamic range image file named test_rpict.hdr.
Running test_accelerad_rtrace should produce tabular data in a file named test_rtrace.txt.
Running test_accelerad_rcontrib should produce tabular data in a file named test_rcontrib.txt.
Running test_AcceleradRT should open an interactive false color view of a simple scene (available only on Windows).

# Workflow
As in the structure diagram shown, you can change the settings directly
in the .py files within the settings folder or create new childs within these
files to not overwrite the default values.

As shown in `system_studies/example.py`, you have to instantiate a
`Settings()` object, which you still can modify before passing it to an instance of `AianaMain()`.
Afterwards you can run its methods `create_and_view_octfile_for_SceneInspection()` and
`simulate_and_evaluate()`. The plots are shown in the interactive window and
stored together with csv-files in your results folder (see `settings/user_paths.py`)
 subfolder name study_name

To make use of the cell exectuion in VS-code, `# #` is used as cell marker.
With the cursor in a cell press `strg+Enter` to run the cell and stay in it, or `strg+shift` to run and go to next cell. If cells are not recognized press `strg+p` and search for `settings.json` and add
    `"jupyter.defaultCellMarker": "# #",` or replace all `# #` with the cell marker of your choice.