#!/usr/bin/env python2

import datetime, optparse, time
import usbtmc


def env():
    log(str(usbtmc.list_devices()))
    log(str(usbtmc.list_resources()))


def probe(idVendor=0x1bfa, idProduct=0x0498):
    """ https://www.metrolab.com/products/thm1176/ """

    instr = usbtmc.Instrument(idVendor, idProduct)
    log(instr.ask("*IDN?"))
    log("Ranges: " + instr.ask(":SENS:ALL?"))
    log("Auto ranging? " + instr.ask(":SENS:AUTO?"))
    return instr


def B(x, y, z):
    units = set()
    mag = 0.0
    for s in [x, y, z]:
        f = s.split()
        units.add(f[1])
        mag += float(f[0])**2
    mag = mag ** 0.5

    if len(units) != 1:
        return "[ERROR: different units]"
    else:
        return "%7.5f %s" % (mag, units.pop())


def loop(instr, nSecSleep=None, nMax=None):
    header = "   %".join(["", "26s", "10s", "10s", "10s", "10s"]) % ("date", "Bx", "By", "Bz", "|B|")
    hyphens = "-" * len(header)
    log(hyphens)
    log(header)
    log(hyphens)

    i = 0
    while (i != nMax):
        try:
            i += 1
            if nSecSleep is not None:
                time.sleep(nSecSleep)
            log(measure_one(instr))
        except KeyboardInterrupt:
            break
    log(hyphens)


def measure_one(instr):
    instr.write(":MEAS?")
    # 5 digits each
    Bx = instr.ask(":FETC:X? 5")
    By = instr.ask(":FETC:Y? 5")
    Bz = instr.ask(":FETC:Z? 5")
    mag = B(Bx, By, Bz)
    s = "   %".join(["", "s", "s", "s", "s", "s"]) % (datetime.datetime.today(), Bx, By, Bz, mag)
    return s


def log(s):
    print s
    logfile.write("\n" + s)


def opts():
    parser = optparse.OptionParser(usage="usage: %prog")
    parser.add_option("--log-file",
                      dest="logfile",
                      default="mag.dat",
                      help="log file to which to append")
    parser.add_option("--n-seconds",
                      dest="nSeconds",
                      default=2,
                      type="int",
                      help="number of seconds to sleep between measurements")
    parser.add_option("--n-measurements",
                      dest="nMeasurements",
                      default=None,
                      type="int",
                      help="stop after this many measurements")

    options, args = parser.parse_args()
    return options


if __name__ == "__main__":
    options = opts()
    logfile = open(options.logfile, "append")
    env()
    loop(probe(), nSecSleep=options.nSeconds, nMax=options.nMeasurements)
    logfile.close()
