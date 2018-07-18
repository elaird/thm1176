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
        title = title.replace("surface2", "probe in zero field chamber on surface")
        title = title.replace("surface3", "probe in zero field chamber on surface")
        h = r.TH1D(filename, "%s;measured magnitude of B (Tesla);entries / bin" % title, 400, 0.0, 0.4)
        g = r.TGraph()
        iPoint = 0

        t0 = ""

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

            b_mag = float(fields[-2])
            h.Fill(b_mag)
            g.SetPoint(iPoint, 1 + iPoint, b_mag)
            if not iPoint:
                t0 = " ".join(fields[:2])
                t0 = t0[:t0.find(".")]
                g.SetName(t0)
            iPoint += 1

        f.close()
        out.append(h)
        out.append(g)

    return out


def write(lst, pdf):
    can = r.TCanvas("canvas", "", 1600, 900)
    can.Divide(2, 1)
    for iPad in [1, 2]:
        can.cd(iPad)
        r.gPad.SetLeftMargin(0.15)
        r.gPad.SetRightMargin(0.15)
        r.gPad.SetTopMargin(0.15)
        r.gPad.SetBottomMargin(0.15)

    can.cd(0)
    can.Print(pdf + "[")
    for i, h in enumerate(lst):
        can.cd(1 + i % 2)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        if h.ClassName().startswith("TH1"):
            h.Draw()
            r.gPad.Update()  # force stats box to be drawn
            st = h.FindObject("stats")
            st.SetX1NDC(0.65)
            st.SetX2NDC(1.00)
        elif i and h.ClassName().startswith("TGraph"):
            h.SetMarkerStyle(20)
            h.Draw("ap")
            text = r.TText()
            text.SetTextAlign(22)
            text.SetTextSize(0.7 * text.GetTextSize())
            text.SetNDC()
            k = text.DrawText(0.5, 0.88, "from " + h.GetName())
            h.GetXaxis().SetTitle("sequential sample number (\Deltat = 2 seconds)")
            h.GetYaxis().SetTitle(lst[i - 1].GetXaxis().GetTitle())
            h.SetTitle(lst[i - 1].GetTitle())
            if i == 31:
                h.GetYaxis().SetTitleOffset(2.4)

        if (i % 2):
            can.cd(0)
            can.Print(pdf)

    can.Print(pdf + "]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat("mer")
    r.gErrorIgnoreLevel = r.kWarning

    write(histos(), "mag.pdf")
