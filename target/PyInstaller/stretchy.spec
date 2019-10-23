# -*- mode: python -*-

block_cipher = None


a = Analysis(['/Users/alex/python-virtual-environments/STR_0/src/main/python/main.py'],
             pathex=['/Users/alex/python-virtual-environments/STR_0/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/alex/.virtualenvs/str0/lib/python3.7/site-packages/fbs/freeze/hooks'],
             runtime_hooks=['/Users/alex/python-virtual-environments/STR_0/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='stretchy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon='/Users/alex/python-virtual-environments/STR_0/target/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='stretchy')
app = BUNDLE(coll,
             name='stretchy.app',
             icon='/Users/alex/python-virtual-environments/STR_0/target/Icon.icns',
             bundle_identifier=None)
