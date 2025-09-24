# Transmission Dashboard

Transmission Dashboard is a Flask-powered monitoring console that tracks X-ray transmission jobs in real time. The refreshed interface delivers a clean, modern layout with a responsive sidebar, vibrant metric tiles, and rich tables so operators can focus on operational health, log details, and FTP connectivity at a glance.

## Highlights

- **Polished UI/UX** – Redesigned navigation, cards, and typography provide a contemporary control room experience that works on desktops and tablets alike.
- **Live telemetry** – Aggregated statistics, activity feeds, and uptime counters update automatically while you browse the dashboard.
- **Deep log exploration** – Dedicated OK/NOK views with DataTables search, filters, pagination, and Excel export for audit-ready reports.
- **Connectivity monitoring** – Built-in FTP status widget with manual ping, configurable polling cadence, and visual health chips.
- **Flexible settings** – Runtime configuration for log directories, refresh cadence, and monitored FTP endpoints stored in `settings.json`.
- **Packaged distribution** – A curated PyInstaller spec (`server_runner.spec`) ships with the repository for producing a standalone Windows executable of the web server.

## Requirements

- Python 3.9 or newer (3.10+ recommended)
- pip for dependency management
- Windows users need the [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist) when running the packaged executable.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Getting Started

1. **Activate your environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .\.venv\Scripts\activate   # Windows
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the dashboard** – choose the method that best matches your workflow:
   - **Development server (auto reload)**
     ```bash
     python run.py
     ```
   - **Waitress production server**
     ```bash
     python server_runner.py
     ```
   - **Direct Flask entry point**
     ```bash
     python app.py
     ```
4. Open your browser to [http://localhost:5000](http://localhost:5000). The homepage features the Overview, Detail Log OK/NOK, Statistics, and Settings sections controlled from the left navigation.

### Initial configuration

- Place `Transmission.log` files (and rotated variants) inside the `logs/` directory or point the Settings page to an external folder.
- Adjust auto refresh, FTP targets, and ping interval from the **Settings** section. Changes persist automatically to `settings.json`.
- Use the **Validate Directory** button to confirm the dashboard can read your logs path before saving.

## Packaging the web server as an executable

A ready-to-use PyInstaller specification is included so the Flask/Waitress server can be delivered as a single `.exe`.

1. **Ensure dependencies are installed**, including `pyinstaller` (already listed in `requirements.txt`).
2. **(Optional) Clean previous builds**:
   ```bash
   pyinstaller --clean server_runner.spec
   ```
3. **Build the executable**:
   ```bash
   pyinstaller server_runner.spec
   ```
4. The packaged server lives at `dist/TransmissionWebServer/TransmissionWebServer.exe`. Launch it to start the Waitress host on port 5000.
5. Distribute the contents of the `dist/TransmissionWebServer/` directory. It already embeds templates, assets, settings, and a `logs/` folder scaffold. Update `settings.json` or replace the `logs/` directory with production data before shipping.

> **Tip:** Remove or trim large log archives before building so the bundled executable stays lean. You can also regenerate `settings.json` after deployment if the target environment requires different defaults.

## Project structure

```
transmissions_dashboard/
├── app.py                 # Flask application factory and routes
├── server_runner.py       # Waitress entry point used for production/packaging
├── templates/             # Jinja2 templates (modernised dashboard UI)
├── assets/                # Static assets bundled with the executable
├── logs/                  # Sample log files (replace with operational data)
├── settings.json          # Persisted UI/server configuration
├── server_runner.spec     # PyInstaller spec for building the web server exe
├── gui_controller.py/.spec# Desktop controller application and build spec
├── run.py                 # Convenience launcher that opens a browser window
└── requirements.txt       # Python dependencies
```

## Development tips

- The dashboard uses Bootstrap 5, Font Awesome 6, DataTables, and Chart.js via CDN. Custom styling lives directly in `templates/dashboard.html`.
- JavaScript utilities near the bottom of `dashboard.html` handle AJAX polling, DataTables initialisation, and notification handling.
- To tweak refresh cadence or log parsing defaults programmatically, edit the constants near the top of `app.py`.
- When contributing UI tweaks, keep the responsive layout in mind—most grid rows already use `col-md-6`/`col-xl-3` breakpoints for fluid layouts.

Enjoy the streamlined monitoring experience!
