#!/usr/bin/env python2

import ROOT as r

def histos(directory="2018-07-18"):
    out = []
    for iFilename, filename in enumerate(["surface2.dat",
                                          "near-x4p-meas1.dat",
                                          "near-x4p-meas2.dat",
                                          "near-x4p-meas3.dat",
                                          "near-x4p-meas4.dat",
                                          "near-x4p-meas5.dat",
                                          "near-x4m-meas1.dat",
                                          "near-x4m-meas2.dat",
                                          "near-x4m-meas3.dat",
                                          "near-x4m-meas4.dat",
                                          "near-x4m-meas5.dat",
                                          "far-x4m-meas1.dat",
                                          "far-x4m-meas2.dat",
                                          "far-x4m-meas3.dat",
                                          "far-x4m-meas4.dat",
                                          "far-x4m-meas5.dat",
                                          "far-x4p-meas1.dat",
                                          "far-x4p-meas2.dat",
                                          "far-x4p-meas3.dat",
                                          "far-x4p-meas4.dat",
                                          "far-x4p-meas5.dat",
                                          "surface3.dat"]):

        title = filename.replace(".dat", "").replace("2018-07-18/", "")
        title = title.replace("surface2", "zero field chamber on surface")
        title = title.replace("surface3", "zero field chamber on surface")
        h_B = r.TH1D(filename, "%s;measured magnitude of B (Tesla);entries / bin" % title, 400, 0.0, 0.4)
        h_BxB = r.TH1D(filename + "BxB", "%s; B_{x} / |B|;entries / bin" % title, 200, -1.0, 1.0)
        h_ByB = r.TH1D(filename + "ByB", "%s; B_{y} / |B|;entries / bin" % title, 200, -1.0, 1.0)
        h_BzB = r.TH1D(filename + "BzB", "%s; B_{z} / |B|;entries / bin" % title, 200, -1.0, 1.0)

        g_B = r.TGraph()
        iPoint = 0

        t0 = ""
        tn = ""

        f = open("%s/%s" % (directory, filename))
        for iLine, line in enumerate(f):
            if "2018" not in line:
                continue

            fields = line.split()
            if len(fields) < 2:
                continue

            if fields[-1] != "T":
                print "ERROR!", fields
                continue

            # filter measurements during which probe was in motion
            if filename.endswith("near-x4p-meas2.dat") and 20 <= iLine:
                continue
            if filename.endswith("near-x4p-meas5.dat") and 15 <= iLine:
                continue

            date, time, b_x, t_x, b_y, t_y, b_z, t_z, b_mag, t_mag  = fields
            if len(set([t_x, t_y, t_z, t_mag])) != 1:
                print "ERROR!", fields
            if not b_mag:
                print "ERROR!", fields

            b_x = float(b_x)
            b_y = float(b_y)
            b_z = float(b_z)
            b_mag = float(b_mag)

            h_B.Fill(b_mag)
            h_BxB.Fill(b_x / b_mag)
            h_ByB.Fill(b_y / b_mag)
            h_BzB.Fill(b_z / b_mag)
            g_B.SetPoint(iPoint, 1 + iPoint, b_mag)
            if not iPoint:
                t0 = truncated_date(fields[:2])
            iPoint += 1
            tn = truncated_date(fields[:2])

        f.close()

        g_B.SetName("_".join([t0, tn]))
        out.append(g_B)
        out.append(h_B)
        out.append(None)
        out.append(h_BxB)
        out.append(h_ByB)
        out.append(h_BzB)

    return out


def truncated_date(lst):
    out = " ".join(lst)
    out = out[:out.find(".")]
    return out


def write(lst, pdf, period=6):
    can = r.TCanvas("canvas", "", 1600, 900)

    keep = []
    can.Print(pdf + "[")
    for i, h in enumerate(lst):
        if not (i % period):
            can.cd(0)
            can.Clear()
            can.Divide(3, 2)

        can.cd(1 + i % period)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        if h is None and 2 <= i:
            text = r.TLatex()
            text.SetTextAlign(32)
            text.SetTextFont(102)
            text.SetTextSize(1.4 * text.GetTextSize())
            text.SetNDC()

            times = lst[i-2].GetName().split("_")
            keep.append(text.DrawText(0.95, 0.95, lst[i - 1].GetTitle()))
            keep.append(text.DrawText(0.95, 0.85, "from " + times[0]))
            keep.append(text.DrawText(0.95, 0.75, "to " + times[1]))
            keep.append(text.DrawText(0.95, 0.55, "|B| = %6.4f +- %6.4f T" % (lst[i - 1].GetMean(), lst[i - 1].GetRMS())))
            keep.append(text.DrawText(0.95, 0.35, "Bx / |B| = %6.3f +- %5.3f" % (lst[i + 1].GetMean(), lst[i + 1].GetRMS())))
            keep.append(text.DrawText(0.95, 0.25, "By / |B| = %6.3f +- %5.3f" % (lst[i + 2].GetMean(), lst[i + 2].GetRMS())))
            keep.append(text.DrawText(0.95, 0.15, "Bz / |B| = %6.3f +- %5.3f" % (lst[i + 3].GetMean(), lst[i + 3].GetRMS())))

        elif h.ClassName().startswith("TH1"):
            h.Draw()
            r.gPad.Update()  # force stats box to be drawn
            st = h.FindObject("stats")
            st.SetX1NDC(0.65)
            st.SetX2NDC(1.00)
        elif h.ClassName().startswith("TGraph") and (i + 1) < len(lst):
            h.SetMarkerStyle(20)
            h.Draw("ap")
            h.GetXaxis().SetTitle("sequential sample number (\Deltat = 2 seconds)")
            h.GetYaxis().SetTitle(lst[i + 1].GetXaxis().GetTitle())
            h.GetYaxis().SetTitleOffset(-15.0)
            h.SetTitle(lst[i + 1].GetTitle())


        if (i % period) == (period - 1):
            can.cd(0)
            can.Print(pdf)

    can.Print(pdf + "]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat("mer")
    r.gErrorIgnoreLevel = r.kWarning

    write(histos(), "mag.pdf")
