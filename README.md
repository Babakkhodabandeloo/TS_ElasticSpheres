# Elastic Sphere Target Strength Calculator

A Python-based web application for calculating the theoretical broadband target strength (TS) of elastic spheres.

The application provides an interactive web interface for specifying sphere material properties, sphere diameter, water properties, and frequency range. Multiple sphere configurations can be calculated and compared on the same target-strength plot.

The web interface is implemented using Streamlit.

## Features

- Calculate broadband target strength of elastic spheres.
- Select predefined sphere materials.
- Define custom material properties:
  - Density, ρ
  - Compressional-wave speed, cₚ
  - Shear-wave speed, cₛ
- Specify sphere diameter.
- Specify water density and sound speed.
- Define frequency range and frequency resolution.
- Compare multiple spheres on the same TS plot.
- Display selected CW frequencies as vertical markers.
- Interactive Plotly visualization.
- Export calculated results to CSV.

Target strength is reported in **dB re 1 m²**.

## Installation

The project uses [uv](https://docs.astral.sh/uv/) for Python environment and dependency management.

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd TS_ElasticSpheres
```

Install the required dependencies:

```bash
uv sync
```

This creates the Python environment and installs the dependencies specified in `pyproject.toml` and `uv.lock`.

## Running the Web Application

From the root directory of the repository, run:

```bash
uv run streamlit run src/ts_elastic_spheres/app.py
```

Streamlit will start a local web server. The terminal should display something similar to:

```text
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Open a web browser and go to:

```text
http://localhost:8501
```

The Elastic Sphere Target Strength Calculator will then run directly in the browser.

No separate Python commands are required while using the web interface. The calculations are performed by the Python application running locally, while the inputs and results are displayed through the browser.

### WSL users

When running the application from Windows Subsystem for Linux (WSL), Streamlit may not automatically open the browser.

If a message such as

```text
gio: http://localhost:8501: Operation not supported
```

appears, the application is normally still running correctly.

Simply open a browser in Windows and enter:

```text
http://localhost:8501
```

The application can also be started without attempting to open a browser automatically:

```bash
uv run streamlit run src/ts_elastic_spheres/app.py --server.headless true
```

To stop the application, return to the terminal and press:

```text
Ctrl+C
```

## Running the Python Calculation Directly

The target-strength calculation can also be run without the web interface:

```bash
uv run python scripts/calculate_ts.py
```

This is useful for development, testing, and scientific calculations performed directly in Python.

## Project Structure

```text
TS_ElasticSpheres/
├── pyproject.toml
├── uv.lock
├── README.md
│
├── src/
│   └── ts_elastic_spheres/
│       ├── __init__.py
│       ├── backscatter.py
│       ├── materials.py
│       └── app.py
│
├── scripts/
│   └── calculate_ts.py
│
└── tests/
    └── test_backscatter.py
```

`backscatter.py` contains the elastic-sphere scattering calculation, `materials.py` contains predefined material properties, and `app.py` provides the Streamlit web interface.

## Web Deployment

The application is designed so that it can also be deployed on a public web server. In that case, users can access the calculator directly through a web browser without installing Python, `uv`, Streamlit, or any other software locally.

For local use and development, the application is available at:

```text
http://localhost:8501
```

after starting the Streamlit server as described above.

## License

License information will be added according to the requirements of the CRIMAC/Institute of Marine Research project.

temporary web: https://crimac-elastic-spheres-ts.streamlit.app/
