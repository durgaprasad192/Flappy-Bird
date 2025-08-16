# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['flappy.py'],
    pathex=[],
    binaries=[],
    datas=[('bg image.png', '.'), ('start button.png', '.'), ('start button pressed.png', '.'), ('restart button.png', '.'), ('down side rod.png', '.'), ('bird.png', '.'), ('start.mp3', '.'), ('point.mp3', '.'), ('background.mp3', '.'), ('death.mp3', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='flappy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
