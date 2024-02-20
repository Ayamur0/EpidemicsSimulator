# EpidemicsSimulator

This tool was designed to simulate an Epidemic. A network and its nodes and node groups can 
be easily created and visualized. To simulate the epidemic, a disease can be created, and the 
spread of it can be simulated and visualized in 3D space. To better understand its spread and 
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
## Usage

The GUI has five different tabs, each with a different functionality for creating/simulating/analyzing an epidemic.

- **Network Editor:** In this tab you can create your network with its nodes and node groups and see it in a 3D space.
> **Note:** After building the network, it may take a while to load the 3D visualization.
- **Disease Editor:** Here you can create your diseases that will spread around in the network.
- **Simulation:** In this tab, the spread is simulated and visualized in a 3D space.
- **Text Simulation:** If only the numbers of the simulation matter, this simulation only shows the changes in text format.
- **Statistics:** After simulating, the resulting stats can be analyzed using this tab.
