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

In this 5 min conference poster presentation video the background for this package is introduced:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/pFz46pmF0vE/3.jpg)](https://www.youtube.com/watch?v=pFz46pmF0vE)

# Code structure
If this package is opened in vs-code with the drawio extension, you can use the class names in the class_structure.drawio.svg file as links to the source code.
<img src="./aiana/aiana_structure.PNG" alt="AIANA structure diagram" />

AIANA is connected to the atmosphere data store (ADS) provided by the [Copernicus Atmosphere Monitoring Service (CAMS)](https://ads.atmosphere.copernicus.eu/#!/home) granting up-to-date and high-res satellite weather data (1 min temporal and 5 km spatial resolution for sun irradiance).

AIANA partly uses the open-source package [Bifacial_radiance](https://bifacial-radiance.readthedocs.io/en/latest/), which is a python wrapper for the ray tracer [Radiance](https://www.radiance-online.org).
To add new geometry features, such as e.g. checkerboard and roof top module shapes, automated scan area visualiza-tion, and a mounting structure parametrization, AIANA also communicates directly with Radiance. AIANA also utilizes [Accelerad](https://nljones.github.io/Accelerad/rt.html) for real-time scene inspections and for the GPU-parallelization of the ray tracing simulations.


# Installation
(developed and tested only in Windows 10)
To run this code, you need several python packages (especially bifacial_radiance), an ADS API key for weather data, and third party software being installed on your computer:
- Radiance (comes with bifacial_radiance)
- Accelerad (optional, as GPU paralellisation can be switched
off in settings/simulation, but recommended)

## Python requirements:
python = "^3.9"
pandas = "^1.4.1"
pvlib = "^0.9.0"
numpy = "^1.22.2"
tqdm = "^4.63.0"
cdsapi = "^0.5.1"
urllib3 = "^1.26.8"
xarray = "^2022.3.0"
matplotlib = "^3.5.1"
seaborn = "^0.11.2"
joypy = "^0.2.6"
scipy = "^1.8.0"
PyYAML = "^6.0"
pytictoc = "^1.5.2"


## Installing bifacial_radiance v0.4.0 (including Radiance):

### Installation steps summarized:
- run "pip install bifacial_radiance -v 0.4.0"
- download ... replace ...
- After installing Radiance in Windows 10 search for "Change my environment variables" (German: "Systemumgebungsvariablen bearbeiten") and check if the Radiance path ".../Radiance/bin" is really in the environment variable "Path".
Enter it manually if necessary.

This video shows how to install the bifacial_radiance software and all associated software needed. More info on the Wiki. Instructions are also shown below.

https://youtu.be/4A9GocfHKyM



Further information:
- detailed instructions of how to install bifacial_radiance, you can also refer to the [installation guide](https://bifacial-radiance.readthedocs.io/en/stable/installation.html)
- Software training: https://www.youtube.com/watch?v=1X9L-R-RVGA
- PHD defense of Ms. Pelaez: https://www.youtube.com/watch?v=11Jp7GqzLPQ
- radiance user manual: https://floyd.lbl.gov/radiance/refer/usman2.pdf

## Installing Accelerad (after installing Radiance):

Copied from [Accelerad Docs](https://nljones.github.io/Accelerad/documentation.html):
### Before you begin
Verify that you have a CUDA-enabled GPU with compute capability 5.0 to 7.5.
If you are unsure what GPU you have:
Right click on Computer and select Properties > Device Manager > Display adapters.
Driver version 418.81 or later is required.

### Download
https://github.com/nljones/Accelerad/releases/tag/Accelerad_07_beta

### testing Accelerad installation
To confirm that Accelerad is successfully installed on your computer, run the included Windows .bat or Unix .sh files in the demo folder. By default, this folder is located at C:\Program Files\Accelerad\demo on Windows and /usr/local/accelerad/demo on Linux.

Running test_accelerad_rpict should produce a high dynamic range image file named test_rpict.hdr.
Running test_accelerad_rtrace should produce tabular data in a file named test_rtrace.txt.
Running test_accelerad_rcontrib should produce tabular data in a file named test_rcontrib.txt.
Running test_AcceleradRT should open an interactive false color view of a simple scene (available only on Windows).


## Insalling this AIANA package in vscode
- clone the repository (https://github.com/IEK-5/aiana)
- Click File / Add folder to Workspace... and chose the aiana.git folder
- make sure that the file path in the terminal is the one of the
package folder (aiana), in which "setup.py" is localized. If you have several folders in your workspace right click aiana and choose "Open in Integrated Terminal"

- run command:
      pip install -e .

- restart vscode

- if this did not help, try
    pip uninstall aiana
    restart
    pip install -e .

In vs code press strg+p and search for settings.json
add
    "jupyter.defaultCellMarker": "# #",
to make use of the cell exectuion
(strg+Enter to stay in a cell after execution or
strg+shift to go to next cell after execution).

## ADS API Key
Register at https://ads.atmosphere.copernicus.eu. After accepting conditions, you can see your UserIDs and API Keys in your user profiles in the web pages, which you need to enter into the API_credentials.txt file, after copying it from the main folder of this repository to the home directory of your PC.

# Workflow
As in the structure diagram shown, you can change the settings directly
in the .py files within the settings folder or create new childs within these
files to not overwrite the default values.

As shown in system_studies/minimal_example.py, you have to instantiate a
Settings object, which you can modify before passing it to an AianaMain object.
Afterwards you can run the AianaMain methods for szene visualization and for
simulation + evaluation.