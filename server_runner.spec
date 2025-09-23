# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['server_runner.py'],
    pathex=['X:\Source Codes\Web\transmissions_dashboard'],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('app.py', '.'),
        ('settings.json', '.'),
        ('logs', 'logs'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TransmissionWebServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_info_entries=None,
    console=True, # This is a console application
    disable_window_close=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
