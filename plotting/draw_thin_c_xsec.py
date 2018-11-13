from ROOT import * 
import sys
from os import listdir as ls
from draw_utils import * 
from argparse import ArgumentParser 
from ROOT import * 
from math import log, sqrt

def init_parser():
  parser = ArgumentParser()
  parser.add_argument('--loc', type=str, help='Location of samples')
  parser.add_argument('--nom', type=str, help='nom File name')
  parser.add_argument('--cmd', type=str, help='Which command to execute ', default=" ")
  parser.add_argument('-f', type=str, help='Which input file')
  parser.add_argument('--plot',type=str, help='Plot name')
  return parser

def SetStyle(h):
  h.SetTitle("Pi+ Ar - Thin Target Scattering")
  h.SetXTitle("KE (MeV)")
  h.SetYTitle("#sigma (barn)")
  h.GetXaxis().SetTitleSize(.05)
  h.GetYaxis().SetTitleSize(.05)
  h.GetYaxis().SetTitleOffset(.8)
  h.GetXaxis().SetTitleOffset(.8)

gStyle.SetLabelFont(62,"XYZ")
gStyle.SetTitleFont(62,"XYZ")
 
args = init_parser().parse_args()
loc = args.loc
cmd = args.cmd
plot = args.plot
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

names = ["abs", "cex", "dcex", "prod", "inel"] 

titles = {"abs":"Pion Absorption",
          "cex":"Single Charge Exchange",
          "dcex":"Double Charge Exchange",
          "prod":"Pion Production",
          "inel":"Inelastic"}

if (cmd == "Draw" or cmd == "draw"):
  inFile = TFile(loc + "/" + args.f, "UPDATE") 

  for name in names:
    c = TCanvas("c"+name, "c"+name, 500, 400)
    nhist = inFile.Get(name) 
    nhist.SetFillColor(0)
    whist = inFile.Get("w"+name) 
    whist.SetFillColor(0)

    nhist.SetTitle(titles[name])
    whist.SetTitle(titles[name])

    nhist.SetXTitle("Pion Momentum (MeV)")
    whist.SetXTitle("Pion Momentum (MeV)")

    nhist.SetYTitle("Cross Section (mbarn)")
    whist.SetYTitle("Cross Section (mb)")

    nhist.SetMarkerStyle(20) 
    whist.SetMarkerStyle(21)
    nhist.SetMarkerColor(4) 
    whist.SetMarkerColor(2)
    
    leg = TLegend(.55,.75,.85,.85)
    leg.AddEntry(nhist, "Nominal", "lp")
    leg.AddEntry(whist, "Weighted", "lp")
   
    whist.SetLineColor(2)

    #Find max
    maxes = [whist.GetMaximum(), nhist.GetMaximum(), 75.]
    theMax = max(maxes)

    whist.SetMaximum( 1.25 * theMax )
    nhist.SetMaximum( 1.25 * theMax )
    whist.SetMinimum( 0. )
    nhist.SetMinimum( 0. )

    whist.Draw("pE hist")
    nhist.Draw("pE same")
    leg.Draw("same")

    c.Write()
    c.SaveAs(name+"_"+plot)



else:

  reac_cut = "(int == \"pi+Inelastic\")"
  abs_cut =  "(int == \"pi+Inelastic\" && (nPi0 + nPiPlus + nPiMinus) == 0)"
  inel_cut = "(int == \"pi+Inelastic\" && (nPi0 + nPiMinus) == 0 && (nPiPlus == 1))"
  cex_cut =  "(int == \"pi+Inelastic\" && (nPiPlus + nPiMinus) == 0 && (nPi0 == 1))"
  dcex_cut = "(int == \"pi+Inelastic\" && (nPiPlus + nPi0) == 0 && (nPiMinus == 1))"
  prod_cut = "(int == \"pi+Inelastic\" && (nPiPlus + nPi0 + nPiMinus) > 1)"


  cuts = {"abs":abs_cut,
    "inel":inel_cut,
    "cex":cex_cut,
    "dcex":dcex_cut,
    "prod":prod_cut
  }

  scale =1.E27 / (.5 * 2.266 * 6.022E23 / 12.01 )

  nhists = dict()
  whists = dict()

  outfile = TFile(loc+"/"+args.f,"RECREATE")
  fileName = loc + "/" + args.nom 

  nomFile = TFile(fileName,"READ")
  nomTree = nomFile.Get("tree")
  
  outfile.cd()
  

  nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>total(50,0,500)","","goff")
  total = gDirectory.Get("total")
  total.Sumw2()
  total.Write()

  nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>reac(50,0,500)",reac_cut,"goff")
  reac = gDirectory.Get("reac")
  reac.Sumw2() 
  reac.Divide( total )
  reac.Scale( scale )
  reac.Write() 

  nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>wreac(50,0,500)",reac_cut + "*finalStateWeight*weight","goff")
  wreac = gDirectory.Get("wreac")
  wreac.Sumw2() 
  wreac.Divide( total )
  wreac.Scale( scale )
  wreac.Write() 


  for name in names:
    cut = cuts[name]
    print name, cut
    nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>"+name+"(50,0,500)", cut,"goff")
  
    nhists[name] = gDirectory.Get(name) 
    nhists[name].Sumw2()
    nhists[name].Divide( total )
    nhists[name].Scale( scale )

    nomTree.Draw("sqrt(Energy*Energy - 139.57*139.57)>>w"+name+"(50,0,500)", cut + "*finalStateWeight*weight", "goff")
    whists[name] = gDirectory.Get("w"+name) 
    whists[name].Sumw2()
    whists[name].Divide( total )
    whists[name].Scale( scale )

    nhists[name].Write() 
    whists[name].Write()

  outfile.Close()


