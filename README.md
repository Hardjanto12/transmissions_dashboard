# Transmission Dashboard

Transmission Dashboard is a modern Flask-based monitoring console for Transmission log pipelines. The refreshed interface pairs a glassmorphism-inspired layout with live system indicators, FTP connectivity widgets, interactive tables, and export tools so that operations teams can inspect every scan with confidence.

## Highlights

- Contemporary UI shell - responsive grid, gradient cards, animated status chips, and darkened sidebar for quick navigation.
- Real-time monitoring - track total scans, success rate, uptime, recent activity, and FTP health in one place.
- Powerful filtering - dedicated OK/NOK log tables with search, status filters, and Excel export support.
- Configurable settings - adjust log directories, refresh cadence, and FTP targets directly from the dashboard.
- Production-ready server - Waitress runner with PyInstaller spec for a standalone backend when needed.
- Desktop controller app - PyQt-powered tray application with an embedded Waitress server for start/stop control.

## Repository layout

| Path | Description |
| --- | --- |
| `app.py` | Flask application providing routes, APIs, Excel export, and FTP health monitoring. |
| `run.py` | Developer-friendly launcher that starts Flask's built-in server and opens a browser tab. |
| `server_runner.py` | Waitress entry point used for production serving and for PyInstaller builds. |
| `templates/` | Jinja templates including the redesigned `dashboard.html`. |
| `assets/` | Static CSS, JS, and vendor bundles consumed by the dashboard. |
| `logs/` | Default directory where Transmission log files are read from. |
| `server_runner.spec` | PyInstaller build specification for producing a standalone backend executable. |
| `gui_controller.py` | Desktop controller application that manages the embedded backend server. |
| `gui_controller.spec` | PyInstaller build specification for the desktop controller bundle. |
| `settings.json` | Persisted dashboard configuration (created automatically on first launch). |

## Requirements

- Python 3.9 or newer
- pip / virtualenv (recommended)
- [PyInstaller](https://pyinstaller.org/) for building Windows executables
- PyQt5 (installed automatically through `requirements.txt`)

## Getting started

Clone the repository and install dependencies inside a virtual environment:

```bash
git clone https://github.com/<your-org>/transmissions_dashboard.git
cd transmissions_dashboard
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Running the dashboard (development)

```bash
python run.py
```

The script prints helpful console output and automatically opens `http://localhost:5000` in your browser. Place Transmission log files into the `logs/` directory (or update the path from the **Settings** panel) and the dashboard will immediately begin parsing them.

To serve the application via Waitress without launching a browser, run:

```bash
python server_runner.py
```

### Running the desktop controller (development)

The controller launches a PyQt interface and embeds the Waitress server directly, so the dashboard backend travels with the GUI.

```bash
python gui_controller.py
```

The window exposes Start/Stop controls, live console output, a tray icon, and a shortcut for opening `http://localhost:5000`. No separate server process is required during development.

## Building a standalone Windows executable (server)

The repository ships with `server_runner.spec`, which bundles the Flask app, templates, static assets, default settings, and the `logs/` folder into a single executable powered by Waitress. Build it as follows:

1. Install PyInstaller inside the virtual environment if it is not already available:
   ```bash
   pip install pyinstaller
   ```
2. From the project root execute the spec:
   ```bash
   pyinstaller --clean server_runner.spec
   ```
3. After the build completes, locate `TransmissionWebServer.exe` inside the `dist/` directory and launch it:
   ```bash
   dist\TransmissionWebServer.exe
   ```
4. The packaged server exposes the dashboard on `http://localhost:5000`. Because the spec includes templates, assets, and the default configuration file, the executable can run on systems without Python installed (logs should reside next to the executable or the configured path).

> Tip: keep the generated `logs` directory alongside the executable so the dashboard discovers data on first launch. You can replace it with your production log folder if desired.

## Packaging the desktop controller

The controller executable bundles the GUI, Flask app, templates, assets, and default configuration into a single portable file.

1. From the project root run:
   ```bash
   pyinstaller --clean gui_controller.spec
   ```
2. Launch the resulting `TransmissionController.exe` located in `dist/`.
3. The controller starts with the window visible. Closing the window offers to minimize to the system tray; choosing **Quit** or the tray **Quit** action stops the embedded server and exits the app.

## Configuration tips

- The controller hosts the Waitress server in-process; the Stop button signals a graceful shutdown before closing the window.
- All configuration changes made in the **Settings** screen are persisted to `settings.json`.
- FTP connectivity checks run on the configured interval and display status inside the overview card.
- Use the **Export Excel** action in the OK table to download filtered Transmission records for offline analysis.
- The embedded server uses the same Flask app and assets as development, so exports and templating behave identically.

## Troubleshooting

- If the dashboard cannot find log files, verify the directory path on the Settings page and confirm filesystem permissions.
- When packaging with PyInstaller, disable aggressive antivirus scanning or whitelist the build folder if the executable is quarantined.
- For verbose debugging during development, run `python app.py` to start Flask with console logging enabled.
- If the desktop controller fails to start the server, ensure no other process is bound to port 5000 and review the activity feed for stack traces.

Enjoy the refreshed Transmission Dashboard!
