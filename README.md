# Transmission Dashboard

Transmission Dashboard is a modern Flask-based monitoring console for Transmission log pipelines. The refreshed interface pairs a glassmorphism-inspired layout with live system indicators, FTP connectivity widgets, interactive tables, and export tools so that operations teams can inspect every scan with confidence.

## Highlights

- **Contemporary UI shell** – responsive grid, gradient cards, animated status chips, and darkened sidebar for quick navigation.
- **Real-time monitoring** – track total scans, success rate, uptime, recent activity, and FTP health in one place.
- **Powerful filtering** – dedicated OK/NOK log tables with search, status filters, and Excel export support.
- **Configurable settings** – adjust log directories, refresh cadence, and FTP targets directly from the dashboard.
- **Production-ready server** – Waitress runner and an updated PyInstaller spec for packaging a one-file Windows executable.

## Repository layout

| Path | Description |
| --- | --- |
| `app.py` | Flask application providing routes, APIs, Excel export, and FTP health monitoring. |
| `run.py` | Developer-friendly launcher that starts Flask's built-in server and opens a browser tab. |
| `server_runner.py` | Waitress entry point used for production serving and for PyInstaller builds. |
| `templates/` | Jinja templates including the redesigned `dashboard.html`. |
| `assets/` | Static CSS, JS, and vendor bundles consumed by the dashboard. |
| `logs/` | Default directory where Transmission log files are read from. |
| `server_runner.spec` | Updated PyInstaller build specification for producing a standalone executable. |
| `settings.json` | Persisted dashboard configuration (created automatically on first launch). |

## Requirements

- Python 3.9 or newer
- pip / virtualenv (recommended)
- [PyInstaller](https://pyinstaller.org/) for building the Windows executable

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

## Building a standalone Windows executable

The repository ships with an updated `server_runner.spec` that bundles the Flask app, templates, static assets, default settings, and the `logs/` folder into a single executable powered by Waitress. Build it as follows:

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

## Configuration tips

- All configuration changes made in the **Settings** screen are persisted to `settings.json`.
- FTP connectivity checks run on the configured interval and display status inside the overview card.
- Use the **Export Excel** action in the OK table to download filtered Transmission records for offline analysis.

## Troubleshooting

- If the dashboard cannot find log files, verify the directory path on the Settings page and confirm filesystem permissions.
- When packaging with PyInstaller, disable aggressive antivirus scanning or whitelist the build folder if the executable is quarantined.
- For verbose debugging during development, run `python app.py` to start Flask with console logging enabled.

Enjoy the refreshed Transmission Dashboard! ✨
