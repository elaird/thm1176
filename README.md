### notes
*   https://www.metrolab.com/products/thm1176
*   https://github.com/python-ivi/python-usbtmc#configuring-udev

### install dependencies
```bash
pip2 install pyusb --user
pip2 install python-usbtmc --user
git clone https://github.com/elaird/thm1176
```

### acquire from probe
```bash
cd thm1176
./mag_usbtmc.py
```

### plot results using [pyROOT](https://root.cern.ch)
```bash
./plot.py 2018-07-18 --bmax=0.4
```
