#!/usr/bin/env python2

import optparse, os, sys
import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True


def pruned_sorted(directory, files):
    dct = {}
    for iFilename, filename in enumerate(files):
        fullname = "%s/%s" % (directory, filename)

        skip = True
        f = open(fullname)

        for line in f:
            if options.match in line:
                skip = False

            if skip:
                continue

            fields = line.split()
            if len(fields) < 2:
                continue

            if fields[-1] != "T":
                continue

            if not fields[0].strip().startswith(options.cenMatch):
                continue

            date, time = fields[:2]
            dct[(date, time)] = filename
            break

        f.close()
    return sorted(dct.items())


def histos(directory, files):
    out = []

    for _, filename in pruned_sorted(directory, files):
        title = filename.replace(".dat", "")
        h_B = r.TH1D(filename, "%s;measured magnitude of B (Tesla);entries / bin" % title, 400, 0.0, options.bmax)
        h_BxB = r.TH1D(filename + "BxB", "%s; B_{x} / |B|;entries / bin" % title, 200, -1.0, 1.0)
        h_ByB = r.TH1D(filename + "ByB", "%s; B_{y} / |B|;entries / bin" % title, 200, -1.0, 1.0)
        h_BzB = r.TH1D(filename + "BzB", "%s; B_{z} / |B|;entries / bin" % title, 200, -1.0, 1.0)
        h_phi = r.TH1D(filename + "phi", "%s; atan2(B_{y} , B_{x});entries / bin" % title, 200, -r.TMath.Pi(), r.TMath.Pi())
        h_dt = r.TH1D(filename + "dt", "%s; #Deltat between measurements (seconds);entries / bin" % title, 100, 0.0, options.deltatmax)

        g_B = r.TGraph()
        iPoint = 0

        t0 = ""
        tn = ""
        tPrev = None

        f = open("%s/%s" % (directory, filename))
        for line in f:
            fields = line.split()

            if len(fields) < 2:
                continue

            if not fields[0].strip().startswith(options.cenMatch):
                continue

            if fields[-1] != "T":
                print "ERROR!", fields
                continue

            try:
                date, time, b_x, t_x, b_y, t_y, b_z, t_z, b_mag, t_mag  = fields
            except ValueError:
                print "ERROR: ", filename, fields
                continue

            if len(set([t_x, t_y, t_z, t_mag])) != 1:
                print "ERROR!", fields
            if not b_mag:
                print "ERROR!", fields

            b_x = float(b_x)
            b_y = float(b_y)
            b_z = float(b_z)
            b_mag = float(b_mag)

            hh, mm, sec = time.split(":")
            hh = float(hh)
            mm = float(mm)
            sec = float(sec)
            t = hh * 3600. + mm * 60. + sec

            if tPrev is not None:
                deltaT = (t - tPrev)
                if hhPrev is not None and hh < hhPrev:  # assume midnight
                    deltaT += 24. * 3600.
                h_dt.Fill(deltaT)
            tPrev = t
            hhPrev = hh

            h_B.Fill(b_mag)
            h_BxB.Fill(b_x / b_mag)
            h_ByB.Fill(b_y / b_mag)
            h_BzB.Fill(b_z / b_mag)
            h_phi.Fill(r.TMath.ATan2(b_y, b_x))
            g_B.SetPoint(iPoint, 1 + iPoint, b_mag)
            if not iPoint:
                t0 = truncated_date(fields[:2])
            iPoint += 1
            tn = truncated_date(fields[:2])

        f.close()

        g_B.SetName("_".join([t0, tn]))
        out.append((g_B, h_dt, h_B, h_phi, h_BxB, h_ByB, h_BzB))

    return out


def truncated_date(lst):
    out = " ".join(lst)
    out = out[:out.find(".")]
    return out


def write(lst, pdf, period=8):
    can = r.TCanvas("canvas_%s" % pdf, "", 1600, 900)

    keep = []

    can.Print(pdf + "[")
    for g_B, h_dt, h_B, h_phi, h_BxB, h_ByB, h_BzB in lst:
        can.cd(0)
        can.Clear()
        can.Divide(4, 2)

        text = r.TLatex()
        text.SetTextAlign(22)
        text.SetTextFont(102)
        # text.SetTextSize(1.1 * text.GetTextSize())
        text.SetNDC()
        keep.append(text.DrawText(0.5, 0.985, h_B.GetTitle()))

        for i in range(period):
            can.cd(1 + i)
            r.gPad.SetTickx()
            r.gPad.SetTicky()

            if i == 1:
                g_B.SetMarkerStyle(20)
                g_B.Draw("ap")
                g_B.GetXaxis().SetTitle("sequential measurement number")
                g_B.GetYaxis().SetTitle(h_B.GetXaxis().GetTitle())
                g_B.GetXaxis().SetTitleSize(1.3 * g_B.GetXaxis().GetTitleSize())
                g_B.GetYaxis().SetTitleSize(1.3 * g_B.GetYaxis().GetTitleSize())
                g_B.GetYaxis().SetTitleOffset(-11.65)
                # g_B.SetTitle(h_B.GetTitle())
            elif i == 3:
                text = r.TLatex()
                text.SetTextAlign(32)
                text.SetTextFont(102)
                text.SetTextSize(1.3 * text.GetTextSize())
                text.SetNDC()

                times = g_B.GetName().split("_")
                keep.append(text.DrawText(0.95, 0.95, h_B.GetTitle()))
                keep.append(text.DrawText(0.95, 0.85, "from " + times[0]))
                keep.append(text.DrawText(0.95, 0.75, "to " + times[1]))
                keep.append(text.DrawText(0.95, 0.55, "|B| = %6.4f +- %6.4f T"    % (h_B.GetMean(), h_B.GetRMS())))
                keep.append(text.DrawText(0.95, 0.35, "Bx / |B| = %6.3f +- %5.3f" % (h_BxB.GetMean(), h_BxB.GetRMS())))
                keep.append(text.DrawText(0.95, 0.25, "By / |B| = %6.3f +- %5.3f" % (h_ByB.GetMean(), h_ByB.GetRMS())))
                keep.append(text.DrawText(0.95, 0.15, "Bz / |B| = %6.3f +- %5.3f" % (h_BzB.GetMean(), h_BzB.GetRMS())))
                # keep.append(text.DrawText(0.95, 0.05, "atan(By/Bx) = %6.3f +- %5.3f" % (h_phi.GetMean(), h_phi.GetRMS())))
            else:
                h = [h_dt, g_B, h_B, None, h_BxB, h_ByB, h_BzB, h_phi][i]
                h.Draw()
                h.SetTitle("")
                h.GetXaxis().SetTitleSize(1.3 * h.GetXaxis().GetTitleSize())
                h.GetYaxis().SetTitleSize(1.3 * h.GetYaxis().GetTitleSize())
                r.gPad.Update()  # force stats box to be drawn
                st = h.FindObject("stats")
                st.SetX1NDC(0.65)
                st.SetX2NDC(1.00)

        can.cd(0)
        can.Print(pdf)

    can.Print(pdf + "]")


def opts():
    parser = optparse.OptionParser(usage="usage: %prog <directory_containing_data>")
    parser.add_option("--bmax",
                      dest="bmax",
                      default=4.0,
                      metavar="B",
                      type="float",
                      help="upper end of histogram of |B|")
    parser.add_option("--deltatmax",
                      dest="deltatmax",
                      default=10.0,
                      metavar="T",
                      type="float",
                      help="upper end of histogram of delta t")
    parser.add_option("--century",
                      dest="century",
                      default=21,
                      metavar="21",
                      type="int",
                      help="century to assume when matching dates")
    parser.add_option("--match",
                      dest="match",
                      default="Metrolab Technology SA,THM1176",
                      metavar="'Metrolab Technology SA,THM1176'",
                      help="string used to identify data files")
    options, args = parser.parse_args()
    options.cenMatch = str(options.century - 1)

    if len(args) != 1:
        sys.exit("\n".join(["", "Pass a directory containing the data as an argument, e.g.", "./plot.py ."]))
    return options, args


def main(directory):
    for root, dirs, files in os.walk(directory):
        pdf = "%s/mag.pdf" % root
        lst = histos(root, files)
        if lst:
            write(lst, pdf)
            print "Wrote %s" % pdf


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat("ourme")
    r.gErrorIgnoreLevel = r.kWarning
    options, args = opts()
    main(args[0])
