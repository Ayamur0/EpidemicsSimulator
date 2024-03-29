# EpidemicsSimulator

This tool was designed to simulate an Epidemic. A social network and its nodes and node groups can 
be easily created and visualized. To simulate an epidemic, a disease with certain characeristics can be created, and the 
spread of it can be simulated and visualized in the network in a 3D space. To better understand its spread and 
outcomes, the result of a simulation can be analyzed using different graphs.

## Running from source

It is recommended to start the application using the executable (EXE) or binary file.
Only start the application from source if these files do not work.

### Requirements

- Python 3.9+
- Python3-venv
- pip

### Creating the virtual environment
```bash
python3 -m venv venv
```

### Activating the virtual environment
#### Linux
```bash
source ./venv/bin/activate
```
#### Windows
```bash
.\venv\Scripts\activate
```

### Installing python packages
```bash
pip install -r ./requirements.txt
```

### Running the file
After activating the virtual environment, start the Python script ```App.py```.
```bash
python App.py
```
> **Note:** Under Linux, make sure the ```venv``` directory has the right access permissions to allow the ```App.py``` to start a new Python process with the binary ```venv/bin/python```.
## Usage

The GUI has five different tabs, each with a different functionality for creating/simulating/analyzing an epidemic.

- **Network Editor:** In this tab you can create your network with its nodes and node groups and see it in a 3D space.
> **Note:** After building the network, it may take a while to load the 3D visualization.
- **Disease Editor:** Here you can create your diseases that will spread around in the network.
- **Simulation:** In this tab, the spreading of diseases is simulated and visualized in a 3D space.
- **Text Simulation:** If only the numbers of the simulation matter, this simulation only shows the changes in text format. It should be used for large networks or high numbers of simulation steps, as the §D simulation can be slow in those cases.
- **Statistics:** After simulating, the resulting stats can be analyzed using this tab.
