# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['interrogatorio_for_windows.py'],
             pathex=['C:\\Users\\elvis\\Interrogat-rio'],
             binaries=[],
             datas=[('www', 'www'), 
('.git', '.git'),
('requirements.txt', '.'), 
('favicon.ico', '.'), 
('README.md', '.'), 
('LICENSE', '.'),
('run_interrogatorio.sh', '.'),
('install_interrogatorio.sh', '.'),
('interrogatorio_for_windows.py', '.'),
('interrogatorio_for_windows.spec', '.'),
('.gitignore', '.'),
('index.html', '.'),
],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
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
          name='interrogatorio_for_windows',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='interrogatorio_for_windows')
