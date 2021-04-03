import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import harrixpylib as h

print(h.open_file("C:/Windows/System32/drivers/etc/hosts"))
