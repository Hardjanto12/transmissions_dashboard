import html
import logging
import os
import sys
import threading
import time
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from server_runner import FLASK_HOST, FLASK_PORT, SHUTDOWN_TOKEN
from waitress import create_server
from app import app

SERVER_URL = f"http://{FLASK_HOST}:{FLASK_PORT}"
LOG_HISTORY_LIMIT = 400


def resource_path(relative: Path) -> Path:
    """Resolve a resource path for both development and PyInstaller builds."""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return (base_dir / relative).resolve()


class ServerThread(QThread):
    """Run the Waitress server inside a dedicated worker thread."""

    output_signal = pyqtSignal(str, str)
    state_signal = pyqtSignal(str)
    exit_signal = pyqtSignal(int)

    class QtLogHandler(logging.Handler):
        def __init__(self, signal):
            super().__init__()
            self._signal = signal

        def emit(self, record):
            try:
                msg = self.format(record)
            except Exception:
                msg = record.getMessage()
            level = "info"
            if record.levelno >= logging.ERROR:
                level = "error"
            elif record.levelno >= logging.WARNING:
                level = "warning"
            self._signal.emit(msg, level)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_requested = threading.Event()
        self.shutdown_event = None
        self.server = None
        self._loggers = []
        self._log_handler = None

    def describe_command(self) -> str:
        return f"Embedded Waitress server ({SERVER_URL})"

    def _attach_logging(self):
        handler = self.QtLogHandler(self.output_signal)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s :: %(message)s"))
        handler.setLevel(logging.INFO)

        targets = [logging.getLogger("waitress"), logging.getLogger("app"), logging.getLogger()]
        for logger in targets:
            if handler not in logger.handlers:
                logger.addHandler(handler)
                if logger.level > logging.INFO:
                    logger.setLevel(logging.INFO)
                self._loggers.append(logger)

        self._log_handler = handler

    def _detach_logging(self):
        if not self._log_handler:
            return
        for logger in self._loggers:
            try:
                logger.removeHandler(self._log_handler)
            except ValueError:
                pass
        self._loggers.clear()
        self._log_handler = None

    def stop(self):
        self._stop_requested.set()
        if self.shutdown_event and not self.shutdown_event.is_set():
            self.shutdown_event.set()
        server = self.server
        if not server:
            return
        try:
            self.output_signal.emit("Closing embedded server...", "info")
            server.close()
            dispatcher = getattr(server, "task_dispatcher", None)
            if dispatcher:
                try:
                    dispatcher.shutdown()
                except Exception:
                    pass
            trigger = getattr(server, "pull_trigger", None)
            if callable(trigger):
                try:
                    trigger()
                except Exception:
                    pass
        except Exception as exc:
            self.output_signal.emit(f"Error while closing server: {exc}", "warning")

    def run(self):
        self._stop_requested.clear()
        exit_code = 0

        self.shutdown_event = threading.Event()
        app.config['SHUTDOWN_EVENT'] = self.shutdown_event
        app.config['SHUTDOWN_TOKEN'] = SHUTDOWN_TOKEN

        self._attach_logging()

        try:
            self.state_signal.emit("starting")
            self.output_signal.emit(
                f"Bootstrapping Transmission server on {SERVER_URL}",
                "info",
            )

            self.server = create_server(app, host=FLASK_HOST, port=FLASK_PORT)
            self.state_signal.emit("running")
            self.output_signal.emit("Embedded server is now running.", "info")

            self.server.run()
        except Exception as exc:
            exit_code = -1
            self.output_signal.emit(f"Server error: {exc}", "error")
            self.state_signal.emit("error")
        finally:
            self._stop_requested.set()
            if self.server:
                server = self.server
                try:
                    server.close()
                except Exception:
                    pass
                dispatcher = getattr(server, "task_dispatcher", None)
                if dispatcher:
                    try:
                        dispatcher.shutdown()
                    except Exception:
                        pass
                trigger = getattr(server, "pull_trigger", None)
                if callable(trigger):
                    try:
                        trigger()
                    except Exception:
                        pass
                self.server = None
            if self.shutdown_event:
                self.shutdown_event.set()
            self._detach_logging()
            self.state_signal.emit("stopped")
            self.exit_signal.emit(exit_code)


class ServerControllerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transmission Server Control Center")
        self.setMinimumSize(900, 620)

        self.server_thread = None
        self.server_running = False
        self.server_started_at = None
        self._allow_close = False
        self._tray_message_shown = False

        self._build_ui()
        self._apply_theme()
        self._setup_tray_icon()

        self.uptime_timer = QTimer(self)
        self.uptime_timer.setInterval(1000)
        self.uptime_timer.timeout.connect(self._update_uptime)

        self._create_server_thread()
        self._update_ui_state()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)

        title = QLabel("Transmission Dashboard Server")
        title.setObjectName("headerTitle")
        subtitle = QLabel("Control panel for the embedded backend service")
        subtitle.setObjectName("headerSubtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        root_layout.addWidget(header_frame)

        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(18, 18, 18, 18)
        status_layout.setSpacing(12)

        status_row = QHBoxLayout()
        status_row.setSpacing(12)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(16, 16)
        self.status_indicator.setObjectName("statusIndicator")

        status_text_container = QVBoxLayout()
        status_text_container.setSpacing(2)

        self.status_label = QLabel("Server status: Offline")
        self.status_label.setObjectName("statusLabel")
        self.uptime_label = QLabel("Uptime: --:--:--")
        self.uptime_label.setObjectName("uptimeLabel")

        status_text_container.addWidget(self.status_label)
        status_text_container.addWidget(self.uptime_label)

        status_row.addWidget(self.status_indicator)
        status_row.addLayout(status_text_container)
        status_row.addStretch()

        self.command_label = QLabel()
        self.command_label.setObjectName("commandLabel")

        self.last_activity_label = QLabel("Last activity: Waiting for events...")
        self.last_activity_label.setObjectName("activityLabel")
        self.last_activity_label.setWordWrap(True)

        status_layout.addLayout(status_row)
        status_layout.addWidget(self.command_label)
        status_layout.addWidget(self.last_activity_label)

        root_layout.addWidget(status_frame)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)

        self.open_button = QPushButton("Open Dashboard")
        self.open_button.clicked.connect(self._open_dashboard)

        self.minimize_button = QPushButton("Minimize to Tray")
        self.minimize_button.clicked.connect(lambda: self._minimize_to_tray(True))

        self.quit_button = QPushButton("Quit Application")
        self.quit_button.clicked.connect(self._quit_application)

        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        button_row.addWidget(self.open_button)
        button_row.addWidget(self.minimize_button)
        button_row.addStretch()
        button_row.addWidget(self.quit_button)

        root_layout.addLayout(button_row)

        log_frame = QFrame()
        log_frame.setObjectName("logFrame")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(18, 18, 18, 18)
        log_layout.setSpacing(12)

        log_title = QLabel("Server activity feed")
        log_title.setObjectName("logTitle")

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setObjectName("logView")

        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_view)

        root_layout.addWidget(log_frame, stretch=1)

    def _apply_theme(self):
        QApplication.setStyle("Fusion")
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0f172a;
            }
            #headerTitle {
                font-size: 26px;
                font-weight: 600;
                color: #e2e8f0;
            }
            #headerSubtitle {
                font-size: 14px;
                color: #94a3b8;
            }
            #statusFrame, #logFrame {
                background-color: rgba(15, 23, 42, 0.65);
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 16px;
            }
            #statusLabel {
                font-size: 18px;
                font-weight: 500;
                color: #e2e8f0;
            }
            #uptimeLabel, #commandLabel, #activityLabel, #logTitle {
                color: #cbd5f5;
                font-size: 13px;
            }
            #logTitle {
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 600;
            }
            #logView {
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                color: #e2e8f0;
                font-family: "Cascadia Code", "Fira Code", monospace;
                font-size: 12px;
            }
            QPushButton {
                padding: 10px 18px;
                border-radius: 12px;
                border: 1px solid transparent;
                color: #0f172a;
                font-weight: 600;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #38bdf8,
                    stop:1 #6366f1
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0ea5e9,
                    stop:1 #4f46e5
                );
            }
            QPushButton:disabled {
                background: rgba(100, 116, 139, 0.4);
                color: rgba(15, 23, 42, 0.6);
            }
            #statusIndicator {
                border-radius: 8px;
                background-color: #64748b;
            }
            QMenu {
                background-color: #1f2937;
                color: #e2e8f0;
                border: 1px solid rgba(148, 163, 184, 0.3);
            }
            QMenu::item:selected {
                background-color: rgba(99, 102, 241, 0.6);
            }
            """
        )

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        tray_icon = self.windowIcon()
        if tray_icon.isNull():
            tray_icon = QIcon(self.style().standardPixmap(QStyle.SP_ComputerIcon))
        self.tray_icon.setIcon(tray_icon)

        tray_menu = QMenu()

        start_action = QAction("Start Server", self)
        start_action.triggered.connect(self.start_server)
        tray_menu.addAction(start_action)

        stop_action = QAction("Stop Server", self)
        stop_action.triggered.connect(self.stop_server)
        tray_menu.addAction(stop_action)

        tray_menu.addSeparator()

        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self._restore_from_tray)
        tray_menu.addAction(show_action)

        open_action = QAction("Open Dashboard", self)
        open_action.triggered.connect(self._open_dashboard)
        tray_menu.addAction(open_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _create_server_thread(self):
        if self.server_thread:
            self.server_thread.deleteLater()
        self.server_thread = ServerThread(self)
        self.server_thread.output_signal.connect(self._handle_log_event)
        self.server_thread.state_signal.connect(self._handle_state_change)
        self.server_thread.exit_signal.connect(self._handle_exit_code)
        self.command_label.setText(f"Target: {self.server_thread.describe_command()}")

    def _handle_state_change(self, state: str):
        state = state.lower()
        if state == "starting":
            self._set_status_indicator("#facc15")
            self.status_label.setText("Server status: Starting...")
        elif state == "running":
            self.server_running = True
            self.server_started_at = time.time()
            self.uptime_timer.start()
            self._set_status_indicator("#34d399")
            self.status_label.setText("Server status: Online")
            self._maybe_show_tray_message("Dashboard server is now running.")
        elif state == "stopped":
            self.server_running = False
            self.uptime_timer.stop()
            self.server_started_at = None
            self._set_status_indicator("#64748b")
            self.status_label.setText("Server status: Offline")
            self.uptime_label.setText("Uptime: --:--:--")
        elif state == "error":
            self.server_running = False
            self._set_status_indicator("#f87171")
            self.status_label.setText("Server status: Error")
        self._update_ui_state()

    def _handle_exit_code(self, exit_code: int):
        if exit_code != 0:
            self._maybe_show_tray_message(
                f"Server exited unexpectedly (code {exit_code})."
            )
        if not self.server_thread or not self.server_thread.isRunning():
            self._create_server_thread()

    def _handle_log_event(self, message: str, level: str):
        timestamp = time.strftime("%H:%M:%S")
        color = {
            "error": "#f87171",
            "warning": "#facc15",
            "info": "#a5f3fc",
        }.get(level, "#e2e8f0")
        safe_text = html.escape(message)
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.insertHtml(
            f'<span style="color:{color}">[{timestamp}] {safe_text}</span><br>'
        )
        self.log_view.moveCursor(QTextCursor.End)

        doc = self.log_view.document()
        while doc.blockCount() > LOG_HISTORY_LIMIT:
            cursor = self.log_view.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.last_activity_label.setText(
            f"Last activity: [{timestamp}] {message}"
        )
        self.last_activity_label.setToolTip(message)

    def _set_status_indicator(self, color: str):
        self.status_indicator.setStyleSheet(
            f"#statusIndicator {{ background-color: {color}; }}"
        )

    def _update_uptime(self):
        if not self.server_started_at:
            return
        elapsed = int(time.time() - self.server_started_at)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.uptime_label.setText(
            f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        )

    def _update_ui_state(self):
        running = self.server_thread and self.server_thread.isRunning()
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def start_server(self):
        if self.server_thread and self.server_thread.isRunning():
            self._handle_log_event("Server is already running.", "warning")
            return
        if not self.server_thread or self.server_thread.isFinished():
            self._create_server_thread()
        self.server_thread.start()

    def stop_server(self):
        if not self.server_thread or not self.server_thread.isRunning():
            self._handle_log_event("Server is not running.", "warning")
            return
        self._handle_log_event("Stop request sent to embedded server.", "info")
        self.server_thread.stop()

    def _open_dashboard(self):
        import webbrowser

        webbrowser.open(SERVER_URL)
        self._handle_log_event(f"Opening dashboard at {SERVER_URL}", "info")

    def _minimize_to_tray(self, show_message: bool):
        self.hide()
        if show_message:
            self._maybe_show_tray_message(
                "Transmission server controller is still running in the tray."
            )

    def _restore_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def _maybe_show_tray_message(self, message: str):
        if not self.tray_icon.isSystemTrayAvailable():
            return
        if self._tray_message_shown and "running" in message.lower():
            return
        self.tray_icon.showMessage(
            "Transmission Server",
            message,
            QSystemTrayIcon.Information,
            3000,
        )
        self._tray_message_shown = True

    def _quit_application(self):
        self._allow_close = True
        self.close()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isHidden():
                self._restore_from_tray()
            else:
                self._minimize_to_tray(False)

    def closeEvent(self, event):
        if self._allow_close:
            self.tray_icon.hide()
            if self.server_thread and self.server_thread.isRunning():
                self.server_thread.stop()
                if not self.server_thread.wait(5000):
                    self._handle_log_event("Server is still stopping; forcing application exit.", "warning")
            event.accept()
            QApplication.instance().quit()
            return

        reply = QMessageBox.question(
            self,
            "Minimize to tray",
            "Close the window to the system tray while keeping the controller running?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            event.ignore()
            self._minimize_to_tray(True)
        elif reply == QMessageBox.No:
            self._allow_close = True
            self.close()
        else:
            event.ignore()


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = ServerControllerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
