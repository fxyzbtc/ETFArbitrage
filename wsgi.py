import sys
path = '/home/ubuntu/arbitrage'
if path not in sys.path:
   sys.path.insert(0, path)

from main_flask import application as application