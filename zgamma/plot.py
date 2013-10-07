#! /usr/bin/env python
from optparse import OptionParser
import sys,os,datetime
from array import *
from ROOT import *
import makeHTML as ht
import utils as u
gROOT.SetBatch()

parser = OptionParser(usage="usage: %prog ver [options -c, -e, -p, -m]")
parser.add_option("-c","--cut",    dest="cut", type="int", default=4,    help="Plots after a certain cut")
parser.add_option("-m", "--merge", dest="merge",action="store_true", default=False, help="Do merging?")
parser.add_option("-e", "--ele",   dest="ele",  action="store_true", default=False, help="Use electron selection")
parser.add_option("-p", "--period",dest="period", default="2012",  help="Year period; 2011 or 2012")
parser.add_option("--bkg", dest="bkg",  action="store_true", default=False, help="Make plots from bkg sample")

(options, args) = parser.parse_args()

import ConfigParser as cp
conf = cp.ConfigParser()
conf.read('config.cfg')
lumi2012 = float(conf.get("lumi","lumi2012A")) + float(conf.get("lumi","lumi2012B"))+\
           float(conf.get("lumi","lumi2012C")) + float(conf.get("lumi","lumi2012D"))
lumi = lumi2012
#sel = ["electron"]
#sel = ["mugamma"]
sel = ["mugamma","electron"]
#sel = []

cuts = []
for key, cut in sorted(conf.items("cuts2")):
    cuts.append(cut)
    #print key, cut

cs = {}
for sample, c in conf.items("cs"):
    print sample,c
    cs[sample] = float(c)
cs["h"]=2*cs["h"]

def effPlots(f1, dir, path):
    print "Now making efficiency plots"
    #f1.cd(dir)

    for var in ["Mll","dR"]:
    
        h0 = f1.Get("eff/gen_"+var+"_0")
        h1 = f1.Get("eff/gen_"+var+"_acc_gamma")
        h2 = f1.Get("eff/gen_"+var+"_acc_lept")
        h3 = f1.Get("eff/gen_"+var+"_reco_gamma_iso")
        h4 = f1.Get("eff/gen_"+var+"_one_ele_reco_ID")
        h5 = f1.Get("eff/gen_"+var+"_two_ele_reco")
        h6 = f1.Get("eff/gen_"+var+"_two_ele_reco_ID")
        h7 = f1.Get("eff/gen_"+var+"_one_ele_reco")
        
        '''
        h0.Draw("hist")
        h1.Draw("hist same")
        h2.Draw("hist same")
        h3.Draw("hist same")
        c1.SaveAs(path+h1.GetName()+".png")
        '''
        #for acceptance
        r1 = h1.Clone()
        r1.Divide(h0)
        r2 = h2.Clone()
        r2.Divide(h0)
        #for reco eff
        r3 = h3.Clone()
        r3.Divide(h2)
        r4 = h4.Clone()
        r4.Divide(h2)
        r5 = h5.Clone()
        r5.Divide(h2)
        r6 = h6.Clone()
        r6.Divide(h2)
        r7 = h7.Clone()
        r7.Divide(h2)

        
        if var=="Mll":
            xname = ";M(l1,l2)"
        if var=="dR":
            xname = ";dR(l1,l2)"

        r1.Draw("hist")
        r2.Draw("hist same")
        r1.SetMinimum(0)
        r1.SetMaximum(1)
        r1.SetTitle(xname+" gen; acc")
        r1.SetLineColor(kRed+1)
        r2.SetLineColor(kGreen+1)
        leg = TLegend(0.20,0.2,0.90,0.30);
        leg.AddEntry(r1,"photon pt>38, eta<2.5", "l")
        leg.AddEntry(r2,"photon pt>38 and  pt(e1,e2) > (23,7)", "l")
        leg.SetTextSize(0.04)
        leg.SetFillColor(kWhite)
        leg.Draw()
        c1.SaveAs(path+"acceptance_"+var+".png")
        
        r3.Draw("hist")
        r3.SetMinimum(0)
        r3.SetMaximum(1)
        r3.SetTitle(xname+" gen; reco eff")    
        r4.Draw("hist same")
        r5.Draw("hist same")
        r6.Draw("hist same")
        r7.Draw("hist same")
    
        r3.SetLineColor(kBlack)
        r4.SetLineColor(kOrange+1)
        r5.SetLineColor(kGreen+1)
        r6.SetLineColor(kRed+1)
        leg = TLegend(0.35,0.15,0.98,0.30);
        leg.AddEntry(r3,"Reco photon pt>38, tight ID", "l")
        leg.AddEntry(r5,"Photon + 2 electrons NO ID pt(e1,e2) > (23,7)", "l")
        leg.AddEntry(r6,"Photon + 2 electrons ELE ID pt(e1,e2) > (23,7)", "l")
        leg.AddEntry(r7,"Photon + ONE electron pt(e) > 30, No ID", "l")
        leg.AddEntry(r4,"Photon + ONE electron pt(e) > 30, ID", "l")
        leg.SetTextSize(0.025)
        leg.SetFillColor(kWhite)
        leg.Draw()
        c1.SaveAs(path+"eff_"+var+".png")
    

if __name__ == "__main__":
    timer = TStopwatch()
    timer.Start()
    
    if len(args) < 1:
        parser.print_usage()
        exit(1)
        
    ver    = sys.argv[1]
    #subdir = sys.argv[3]        
    cut=str(options.cut)
    doMerge = options.merge
    period  = options.period
    doBkg   = options.bkg
    
    gROOT.ProcessLine(".L ~/tdrstyle.C")
    setTDRStyle()
    TH1.SetDefaultSumw2(kTRUE)
    
    
    pathBase = "/uscms_data/d2/andreypz/html/zgamma/dalitz/"+ver+"_cut"+cut
    hPath = "/eos/uscms/store/user/andreypz/batch_output/zgamma/8TeV/"+ver
    #hPath = "/uscms_data/d2/andreypz/zgamma/"+ver


    if doMerge:
        os.system("rm "+hPath+"/m_*.root") #removing the old merged files
    yields_data = {}
    yields_bkg  = {}
    yields_sig  = {}

    tri_hists = {}
    dataFile  = {}
    for thissel in sel:
    #for thissel in ["muon","mugamma","single-mu"]:
        if doMerge:
            os.system("hadd "+hPath+"/m_Data_"    +thissel+"_"+period+".root "+hPath+"/"+thissel+"_"+period+"/hhhh_*Run20*.root")

        subdir = thissel
        path = pathBase+"/"+subdir+"/"
        if doBkg:
            path = pathBase+"/bkg_"+subdir+"/"
        u.createDir(path)
        u.createDir(pathBase+"/Muons")
        u.createDir(pathBase+"/eff")

        sigFile = TFile(hPath+"/"+thissel+"_"+period+"/hhhh_h-dalitz_1.root", "OPEN")
        #bkgFile = TFile(hPath+"/"+thissel+"_"+period+"/hhhh_DY-mg5_1.root",   "OPEN")
        dataFile[thissel] = TFile(hPath+"/m_Data_"+thissel+"_"+period+".root","OPEN")

        yields_data[thissel] = u.getYields(dataFile[thissel])
        yields_sig[thissel]  = u.getYields(sigFile,True)
        #yields_bkg[thissel]  = getYields(bkgFile)

        if int(cut) >2:
            tri_hists[thissel]   = dataFile[thissel].Get("tri_mass_cut"+cut).Clone()
        

        u.drawAllInFile(dataFile[thissel], "data", sigFile,"100x h #rightarrow ll#gamma",  "",path, cut, "lumi")
        if thissel =="mugamma":
            u.drawAllInFile(dataFile[thissel], "data",sigFile,"signal",  "Muons",pathBase+"/Muons/", None,"norm")
            u.drawAllInFile(dataFile[thissel], "data",sigFile,"signal",  "Photon",pathBase+"/Pho-1/", None,"norm")
        elif thissel =="electron":
            u.drawAllInFile(dataFile[thissel], "data",sigFile,"signal",  "Photon",pathBase+"/Pho-2/", None,"norm")
            u.drawAllInFile(dataFile[thissel], "data",sigFile,"signal",  "Electrons",pathBase+"/Ele/", None,"norm")
            
        
        #dataFile.Close()
    #print yields_data

    sigFile = TFile("hhhh_sig.root", "OPEN")
    effPlots(sigFile, "eff", pathBase+"/eff/")

    prof = sigFile.Get("eff/gen_Mll_vs_dR")
    prof.Draw("")
    c1.SaveAs(pathBase+"/eff/gen_Mll_vs_dR.png")
    
    plot_types =[]
    list = os.listdir(pathBase)
    for d in list:
        if os.path.isdir(pathBase+"/"+d):
            plot_types.append(d)

    '''
    if int(cut) >2:
        print tri_hists
        tri_hists["mugamma"].Draw("hist")
        tri_hists["muon"].Draw("same hist")
        #tri_hists["single-mu"].Draw("same hist")
        tri_hists["mugamma"].SetLineColor(kRed+3)
        #tri_hists["single-mu"].SetLineColor(kGreen+2)
        leg = TLegend(0.60,0.73,0.90,0.90);
        leg.AddEntry(tri_hists["mugamma"], "Mu22_Pho22","f")
        leg.AddEntry(tri_hists["muon"],    "Mu17_Mu8",  "f")
        #leg.AddEntry(tri_hists["single-mu"],"IsoMu24",  "f")
        leg.SetTextSize(0.04)
        leg.SetFillColor(kWhite)
        leg.Draw()
    
        c1.SaveAs("tri_plot.png")
    '''


    table_sig  = u.yieldsTable(yields_sig, sel)
    table_data = u.yieldsTable(yields_data, sel)

    #u.makeTable(table_data,"html")
    #u.makeTable(table_sig,"html")
    #u.makeTable(table_data,"twiki")
    u.makeTable(table_sig,"twiki")

    comments = ["These plots are made for ...",
                "Blah"]
    
    ht.makeHTML("h &rarr; dalitz decay plots",pathBase, plot_types, comments, "mugamma")

    print "\n\t\t finita la comedia \n"
