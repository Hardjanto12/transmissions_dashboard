# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

block_cipher = None

project_root = Path(sys.argv[0]).resolve().parent

resource_roots = [
    (project_root / "templates", "templates"),
    (project_root / "assets", "assets"),
    (project_root / "logs", "logs"),
    (project_root / "settings.json", "."),
]

datas = []
for source, target in resource_roots:
    if source.exists():
        datas.append((str(source), target))


a = Analysis(
    ['gui_controller.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=['server_runner'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TransmissionController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_window_close=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
