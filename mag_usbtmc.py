#!/usr/bin/env python2

import datetime, optparse, subprocess, sys, time
import usbtmc


def commandOutputFull(cmd):
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
    stdout, stderr = p.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": p.returncode}


def probe(idVendor=0x1bfa, idProduct=0x0498):
    """ see https://www.metrolab.com/products/thm1176/ """

    log("USBTMC   devices: " + str(usbtmc.list_devices()))
    log("USBTMC resources: " + str(usbtmc.list_resources()))

    try:
        instr = usbtmc.Instrument(idVendor, idProduct)
    except usbtmc.usbtmc.UsbtmcException:
        msg = []
        for cmd in ["lsmod | grep usbtmc   ",
                    "lsusb | grep 'ID %s'" % (hex(idVendor)[2:]),
                    "ls -l /dev/usbtmc*"]:
            msg.append("`%s` returns %s" % (cmd, str(commandOutputFull(cmd))))
        msg.append("\nProbe not found.")
        sys.exit("\n".join(msg))

    settings(instr)
    return instr


def settings(instr):
    """ see THM1176_User_Manual_v1_3r1_4.pdf """

    if options.nSecondsTimeout is not None:
        log("Setting timeout to %d seconds" % options.nSecondsTimeout)
        instr.timeout = options.nSecondsTimeout

    log(instr.ask("*IDN?"))
    log()
    log("Resetting probe")
    instr.write(":*RST")

    log("Ranges: " + instr.ask(":SENS:ALL?"))
    log("Auto ranging? " + instr.ask(":SENS:AUTO?"))
    log("Temp,gain calib? " + instr.ask(":CAL:STAT?"))
    if options.factoryOffset:
        log("Restoring factory offset")
        if options.nSecondsTimeout < 10:
            log("WARNING: restore takes approximately 6 seconds but timeout is only %d seconds." % options.nSecondsTimeout)
        instr.write(":CAL:ZERO")
    if options.setOffset:
        log("Correcting offset based on current measurements (assuming zero field)")
        if options.nSecondsTimeout < 10:
            log("WARNING: zero-ing takes approximately 6 seconds but timeout is only %d seconds." % options.nSecondsTimeout)
        instr.write(":CAL:INIT")

    instr.write(":AVER:COUN %d" % options.nAverage)
    log("Averaging %s samples per measurement" % str(instr.ask(":AVER:COUN?")))

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
    header = "   %".join(["", "26s", "12s", "12s", "12s", "12s"]) % ("date", "Bx", "By", "Bz", "|B|")
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
    # instr.write(":MEAS?")  # resets to maximum range via *RST
    instr.write(":READ?")
    # 5 digits each
    Bx = instr.ask(":FETC:X? 5")
    By = instr.ask(":FETC:Y? 5")
    Bz = instr.ask(":FETC:Z? 5")
    mag = B(Bx, By, Bz)
    s = "   %".join(["", "26s", "12s", "12s", "12s", "12s"]) % (datetime.datetime.today(), Bx, By, Bz, mag)
    return s


def log(s=""):
    print s
    logfile.write("\n" + s)


def opts():
    parser = optparse.OptionParser(usage="usage: %prog")
    parser.add_option("--factory-offset",
                      dest="factoryOffset",
                      default=False,
                      action="store_true",
                      help="restore offset correction to factory setting")
    parser.add_option("--set-offset",
                      dest="setOffset",
                      default=False,
                      action="store_true",
                      help="perform offset correction procedure in zero field chamber")
    parser.add_option("--logfile",
                      dest="logfile",
                      default="mag.dat",
                      metavar="mag.dat",
                      help="log file to which to append")
    parser.add_option("--average",
                      dest="nAverage",
                      metavar="N",
                      default=100,
                      type="int",
                      help="number of samples to average in each measurement")
    parser.add_option("--measurements",
                      dest="nMeasurements",
                      metavar="N",
                      default=None,
                      type="int",
                      help="stop after this many measurements")
    parser.add_option("--sleep",
                      dest="nSecondsSleep",
                      metavar="N",
                      default=2,
                      type="int",
                      help="number of seconds to sleep between measurements")
    parser.add_option("--timeout",
                      dest="nSecondsTimeout",
                      metavar="N",
                      default=10,
                      type="int",
                      help="number of seconds to wait before timing out")

    options, args = parser.parse_args()
    return options


if __name__ == "__main__":
    options = opts()
    logfile = open(options.logfile, "append")
    loop(probe(), nSecSleep=options.nSecondsSleep, nMax=options.nMeasurements)
    logfile.close()
