# -*- mode: python ; coding: utf-8 -*-

#############################################################################
#
#  Created by Hamano0813
#  用于pyinstaller构建项目为单EXE程序的小工具
#  命令行执行输入 pyinstaller file.spec
#  可搭配build.bat使用
#  需要的第三方库
#  pyinstaller
#
#############################################################################

block_cipher = None

# noinspection PyUnresolvedReferences
a = Analysis(
    ['release\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
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

# Exclude Binaries
binaries = []
binaries_exclude = {
    'opengl32sw.dll',
    'Qt6Network.dll',
    'Qt6OpenGL.dll',
    'Qt6Qml.dll',
    'Qt6QmlModels.dll',
    'Qt6Quick.dll',
    'Qt6Svg.dll',
    'Qt6VirtualKeyboard.dll',
    'MSVCP140.dll',
    'MSVCP140_1.dll',
    'MSVCP140_2.dll',
    'libcrypto-1_1.dll',
    'VCRUNTIME140.dll',
    'VCRUNTIME140_1.dll',
    'qsvgicon.dll',
    'qgif.dll',
    'qicns.dll',
    'qjpeg.dll',
    'qsvg.dll',
    'qtga.dll',
    'qtvirtualkeyboardplugin.dll',
    'qdirect2d.dll',
    'qoffscreen.dll',
    'qminimal.dll',
    'qwebp.dll',
    'qtiff.dll',
    'qwbmp.dll',
    'qpdf.dll',
    'qnetworklistmanager.dll',
    'qcertonlybackend.dll',
    'qopensslbackend.dll',
    'qschannelbackend.dll',
    'QtNetwork.pyd',
    '_webp.cp310-win_amd64.pyd',
    '_bz2.pyd',
    '_decimal.pyd',
    '_lzma.pyd',
    '_socket.pyd',
    'unicodedata.pyd',
    'select.pyd',
}

for (dest, source, kind) in a.binaries:
    # noinspection PyUnresolvedReferences
    if os.path.split(source)[1] in binaries_exclude:
        continue
    binaries.append((dest, source, kind))

a.binaries = binaries

# Exclude Datas
datas = []

for (dest, source, kind) in a.datas:
    # noinspection PyUnresolvedReferences
    if os.path.split(source)[1].startswith('qtbase_'):
        continue
    datas.append((dest, source, kind))

a.datas = datas

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# noinspection PyUnresolvedReferences
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FTX',
    icon='./rec/icon.ico',
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
    version='version.txt',
)
