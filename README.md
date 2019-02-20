### notes
*   https://www.metrolab.com/products/thm1176
*   https://github.com/python-ivi/python-usbtmc#configuring-udev

### install dependencies
```bash
pip install pyusb --user
pip install python-usbtmc --user
git clone https://github.com/elaird/thm1176
```

### acquire from probe
```bash
cd thm1176
./mag_usbtmc.py --logfile=measurement1.dat
# interrupt with ctrl-c
```

### plot results using [pyROOT](https://root.cern.ch)
```bash
./plot.py 2018-07-18-uxc --bmax=0.4
```
