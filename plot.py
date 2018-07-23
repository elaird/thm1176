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
        h_phi = r.TH1D(filename + "phi", "%s; atan2(B_{y} , B_{x});entries / bin" % title, 200, -r.TMath.Pi(), r.TMath.Pi())

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
            h_phi.Fill(r.TMath.ATan2(b_y, b_x))
            g_B.SetPoint(iPoint, 1 + iPoint, b_mag)
            if not iPoint:
                t0 = truncated_date(fields[:2])
            iPoint += 1
            tn = truncated_date(fields[:2])

        f.close()

        g_B.SetName("_".join([t0, tn]))
        out.append((g_B, h_B, h_phi, h_BxB, h_ByB, h_BzB))

    return out


def truncated_date(lst):
    out = " ".join(lst)
    out = out[:out.find(".")]
    return out


def write(lst, pdf, period=6):
    can = r.TCanvas("canvas", "", 1600, 900)

    keep = []
    can.Print(pdf + "[")
    for g_B, h_B, h_phi, h_BxB, h_ByB, h_BzB in lst:
        can.cd(0)
        can.Clear()
        can.Divide(3, 2)

        for i in range(period):
            can.cd(1 + i)
            r.gPad.SetTickx()
            r.gPad.SetTicky()

            if i == 0:
                g_B.SetMarkerStyle(20)
                g_B.Draw("ap")
                g_B.GetXaxis().SetTitle("sequential sample number (\Deltat = 2 seconds)")
                g_B.GetYaxis().SetTitle(h_B.GetXaxis().GetTitle())
                g_B.GetXaxis().SetTitleSize(1.3 * g_B.GetXaxis().GetTitleSize())
                g_B.GetYaxis().SetTitleSize(1.3 * g_B.GetYaxis().GetTitleSize())
                g_B.GetYaxis().SetTitleOffset(-11.65)
                g_B.SetTitle(h_B.GetTitle())
            elif i == 2:
                text = r.TLatex()
                text.SetTextAlign(32)
                text.SetTextFont(102)
                text.SetTextSize(1.4 * text.GetTextSize())
                text.SetNDC()

                times = g_B.GetName().split("_")
                keep.append(text.DrawText(0.95, 0.95, h_B.GetTitle()))
                keep.append(text.DrawText(0.95, 0.85, "from " + times[0]))
                keep.append(text.DrawText(0.95, 0.75, "to " + times[1]))
                keep.append(text.DrawText(0.95, 0.55, "|B| = %6.4f +- %6.4f T"    % (h_B.GetMean(), h_B.GetRMS())))
                keep.append(text.DrawText(0.95, 0.35, "Bx / |B| = %6.3f +- %5.3f" % (h_BxB.GetMean(), h_BxB.GetRMS())))
                keep.append(text.DrawText(0.95, 0.25, "By / |B| = %6.3f +- %5.3f" % (h_ByB.GetMean(), h_ByB.GetRMS())))
                keep.append(text.DrawText(0.95, 0.15, "Bz / |B| = %6.3f +- %5.3f" % (h_BzB.GetMean(), h_BzB.GetRMS())))
            else:
                # h = [g_B, h_B, h_phi, h_BxB, h_ByB, h_BzB][i]
                h = [None, h_B, None, h_phi, h_BzB, None][i]
                if h is None:
                    continue
                h.Draw()
                h.GetXaxis().SetTitleSize(1.3 * h.GetXaxis().GetTitleSize())
                h.GetYaxis().SetTitleSize(1.3 * h.GetYaxis().GetTitleSize())
                r.gPad.Update()  # force stats box to be drawn
                st = h.FindObject("stats")
                st.SetX1NDC(0.65)
                st.SetX2NDC(1.00)

        can.cd(0)
        can.Print(pdf)

    can.Print(pdf + "]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat("mer")
    r.gErrorIgnoreLevel = r.kWarning

    write(histos(), "mag.pdf")
