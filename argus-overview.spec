# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Argus Overview v2.4 Linux build
Creates standalone application with all dependencies bundled
"""
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all PySide6 data files and binaries
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')

# Collect watchdog submodules
watchdog_hiddenimports = collect_submodules('watchdog')

a = Analysis(
    ['src/main.py'],
    pathex=[os.path.abspath('.')],
    binaries=pyside6_binaries,
    datas=[
        ('assets', 'assets'),
    ] + pyside6_datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._xorg',
        'pynput.mouse',
        'pynput.mouse._xorg',
        'Xlib',
        'Xlib.display',
        'Xlib.X',
        'Xlib.XK',
        'Xlib.ext',
        'Xlib.ext.xtest',
        'numpy',
        'watchdog',
        'watchdog.observers',
        'watchdog.observers.inotify',
        'watchdog.observers.inotify_buffer',
        'watchdog.events',
    ] + pyside6_hiddenimports + watchdog_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Argus-Overview',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Argus-Overview',
)
