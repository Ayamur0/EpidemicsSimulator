# EpidemicsSimulator

## Running from source

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

##ä Running the file
```bash
python App.py
```

## Usage

The GUI has five different tabs, each with a different functionality for creating/simulating/analyzing an epidemic.

- **Network Editor:** In this tab you can create your network and see it in a 3D space.

- **Disease Editor:** Here you can create your diseases that will spread around in the network.

- **Simulation:** To simulate the spread, this tab can be used. It shows the spread in the network in a 3D space.

- **Text Simulation:** If only the numbers of the simulation matter, this simulation only shows the changes in text format.

- **Statistics:** After simulating, the resulting stats can be shown in this tab.
