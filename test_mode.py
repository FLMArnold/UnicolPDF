import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt6.QtWidgets import QApplication
_ = QApplication(sys.argv)

from app.dialogs.background_dlg import BackgroundDialog

modes = ['fill', 'crop', 'stretch', 'dense']
for mode in modes:
    dlg = BackgroundDialog('/some/path.png', mode)
    r = dlg.get_result()
    assert r['mode'] == mode, f'Expected {mode}, got {r["mode"]}'
    print(f'  Set {mode} -> get {r["mode"]} OK')

print('--- All mode persistance tests passed ---')
