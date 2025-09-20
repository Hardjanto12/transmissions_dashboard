import sys
import os
import subprocess
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QSystemTrayIcon, QMenu, QAction, QMessageBox, QStyle
)
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# --- Configuration ---
SERVER_EXE_PATH = "dist/TransmissionWebServer.exe" # Path to the server executable
SERVER_URL = "http://localhost:5000"
ICON_PATH = "icon.ico" # Assuming icon.ico exists in the root

class ServerThread(QThread):
    """Thread to run the server executable and capture its output."""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_process = None

    def run(self):
        try:
            self.server_process = subprocess.Popen(
                SERVER_EXE_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Hide console window
            )
            self.output_signal.emit(f"Server started: {SERVER_EXE_PATH}\n")
            
            # Read stdout and stderr in separate loops
            for line in iter(self.server_process.stdout.readline, ''):
                self.output_signal.emit(line)
            for line in iter(self.server_process.stderr.readline, ''):
                self.output_signal.emit(f"ERROR: {line}")

            self.server_process.wait()
            self.output_signal.emit("Server process finished.\n")
        except FileNotFoundError:
            self.output_signal.emit(f"ERROR: Server executable not found at {SERVER_EXE_PATH}\n")
        except Exception as e:
            self.output_signal.emit(f"ERROR starting server: {e}\n")
        finally:
            self.finished_signal.emit()

    def stop(self):
        if self.server_process and self.server_process.poll() is None:
            self.output_signal.emit("Stopping server...\n")
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            if self.server_process.poll() is None:
                self.server_process.kill()
            self.output_signal.emit("Server stopped.\n")

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transmission Web Server Controller")
        self.setGeometry(100, 100, 800, 600)

        self.server_thread = ServerThread()
        self.server_thread.output_signal.connect(self.append_log)
        self.server_thread.finished_signal.connect(self.on_server_finished)

        self.init_ui()
        self.init_tray_icon()

        self.server_running = False
        self.update_ui_state()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)
        button_layout.addWidget(self.stop_button)

        self.open_browser_button = QPushButton("Open Web App")
        self.open_browser_button.clicked.connect(self.open_web_app)
        button_layout.addWidget(self.open_browser_button)

        self.quit_button = QPushButton("Quit App")
        self.quit_button.clicked.connect(self.close)
        button_layout.addWidget(self.quit_button)

        main_layout.addLayout(button_layout)

        # Log display
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        main_layout.addWidget(self.log_text_edit)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
        else:
            self.tray_icon.setIcon(QIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))) # Fallback icon

        tray_menu = QMenu()
        self.start_action = QAction("Start Server", self)
        self.start_action.triggered.connect(self.start_server)
        tray_menu.addAction(self.start_action)

        self.stop_action = QAction("Stop Server", self)
        self.stop_action.triggered.connect(self.stop_server)
        tray_menu.addAction(self.stop_action)

        tray_menu.addSeparator()

        self.show_hide_action = QAction("Show/Hide Window", self)
        self.show_hide_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(self.show_hide_action)

        self.open_web_app_action = QAction("Open Web App", self)
        self.open_web_app_action.triggered.connect(self.open_web_app)
        tray_menu.addAction(self.open_web_app_action)

        tray_menu.addSeparator()

        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.close)
        tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger: # Left-click
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow()

    def start_server(self):
        if not self.server_running:
            self.log_text_edit.append("Attempting to start server...")
            self.server_thread.start() # Start the QThread
            self.server_running = True
            self.update_ui_state()
        else:
            self.append_log("Server is already running.\n")

    def stop_server(self):
        if self.server_running:
            self.server_thread.stop()
            self.server_running = False
            self.update_ui_state()
        else:
            self.append_log("Server is not running.\n")

    def on_server_finished(self):
        self.server_running = False
        self.update_ui_state()
        self.append_log("Server thread has finished.\n")

    def open_web_app(self):
        import webbrowser
        webbrowser.open(SERVER_URL)
        self.append_log(f"Opening web app in browser: {SERVER_URL}\n")

    def append_log(self, text):
        self.log_text_edit.moveCursor(QTextCursor.End)
        self.log_text_edit.insertPlainText(text)
        self.log_text_edit.moveCursor(QTextCursor.End)

    def update_ui_state(self):
        self.start_button.setEnabled(not self.server_running)
        self.stop_button.setEnabled(self.server_running)
        self.start_action.setEnabled(not self.server_running)
        self.stop_action.setEnabled(self.server_running)

    def closeEvent(self, event):
        if self.server_running:
            reply = QMessageBox.question(self, 'Quit Application',
                                         "Server is still running. Do you want to stop the server and quit?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.stop_server()
                event.accept()
            elif reply == QMessageBox.No:
                self.hide() # Minimize to tray
                event.ignore()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ensure the application does not quit when the last window is closed
    app.setQuitOnLastWindowClosed(False)

    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())