#!/usr/bin/env python

import sys,os
import time
from ROOT import *
import utils as u
import makeHTML as ht
gROOT.SetBatch()


subdir = sys.argv[1]

outpath = '/uscms_data/d2/andreypz/html/zgamma/lhe/'
files={}

#files["one"] = ['/uscms_data/d2/andreypz/lhe_vbf_higgs/vbfh_eeg_m125.root']
#files["two"] = ['/uscms_data/d2/andreypz/lhe_vbf_higgs/vbfh_mumug_m125.root']
#files["one"] = ['/uscms_data/d2/andreypz/lhe_higgs_eegamma_dalitz/heeg_m120.root']
files["one"] = ['/uscms_data/d2/andreypz/lhe_vh_mumugamma/hmumug_m125.root']
files["two"] = ['/uscms_data/d2/andreypz/lhe_higgs_mumugamma_dalitz/hmumug_m125.root']
#files["one"] = ['/uscms_data/d2/andreypz/lhe_mcfm/lhe_mcfm_hzg_dalitz_lord_fixed_unweighted.lhe.root']

MH = 125
LEPID1 = 13
LEPID2 = 13

print files
#gSystem.Load("/home/andreypz/workspace/MadGraph5/ExRootAnalysis/lib/libExRootAnalysis.so")
gSystem.Load("/uscms/home/andreypz/work/MadGraph5/ExRootAnalysis/lib/libExRootAnalysis.so")
#gSystem.Load("../plugins/HistManager_cc.so")
gROOT.LoadMacro("../plugins/HistManager.cc+");
gROOT.LoadMacro("../plugins/ZGAngles.cc+");

oneFile = TFile(outpath+"out_one_"+subdir+".root","RECREATE")
oneFile.cd()
h1 = HistManager(oneFile)

twoFile = TFile(outpath+"out_two_"+subdir+".root","RECREATE")
twoFile.cd()
h2 = HistManager(twoFile)

testFile = TFile(outpath+"out_test_"+subdir+".root","RECREATE")
testFile.mkdir("eff")
testFile.cd()
h3 = HistManager(testFile)

ang = ZGAngles()

newDir = outpath 
print newDir
if not os.path.exists(newDir):
    os.makedirs(newDir)

def FillAllHists(files, h):
    # h is a hist manager instance here
    
    fChain = TChain("LHEF");
    for f in files:
        fChain.Add(f)
        #fChain.Print()
        print f
        
    dcount = 0
    for evt in fChain:

        g1 = TLorentzVector(0)
        g2 = TLorentzVector(0)
        g3 = TLorentzVector(0)
        l1 = TLorentzVector(0)
        l2 = TLorentzVector(0)
        j1 = TLorentzVector(0)
        j2 = TLorentzVector(0)
        gamma = TLorentzVector(0)
        diLep = TLorentzVector(0)
        trueHiggs = TLorentzVector(0)
        
        hasZ = 0
        hasWp = 0
        hasWm = 0
        hasGlu3=0
        hasGamma=0
        hi = 0
        qq = 0
        for p in evt.Particle:
            px = p.Px
            py = p.Py
            pz = p.Pz
            E  = p.E
            M  = p.M
        
            if (p.PID == 25):
                trueHiggs.SetPxPyPzE(px,py,pz,E)
                hi+=1

            if abs(p.PID) < 6 and p.Status==1:
                qq+=1
                if qq==1:
                    j1.SetPxPyPzE(px,py,pz,E)
                if qq==2:
                    j2.SetPxPyPzE(px,py,pz,E)
                
            if (p.PID == 22 and p.Status==1):
                gamma.SetPxPyPzE(px,py,pz,E)
                hasGamma=1

            if (p.PID == 22 and p.Status==1):
                gamma.SetPxPyPzE(px,py,pz,E)
                hasGamma=1
                
            if (p.PID == LEPID1 or p.PID==LEPID2):
                l1.SetPxPyPzE(px,py,pz,E)
            if (p.PID == -LEPID1 or p.PID==-LEPID2): 
                l2.SetPxPyPzE(px,py,pz,E)

            if p.PID==23:
                hasZ=1
            if p.PID==24:
                hasWp=1
            if p.PID==-24:
                hasWm=1

            if (p.PID==21 and p.Status==-1):
                g1.SetPxPyPzE(px,py,pz,E)
            if (p.PID==21 and p.Status==-1):
                g2.SetPxPyPzE(px,py,pz,E)
            if (p.PID==21 and p.Status==1):
                hasGlu3=1
                g3.SetPxPyPzE(px,py,pz,E)

    

        if l1.Pt()>l2.Pt():
            lPt1 = l1
            lPt2 = l2
        else:
            lPt1 = l2
            lPt2 = l1

    
        diLep = l1+l2
        if diLep.Pt()==0:
            #print "dLep.Pt = 0"
            continue

        # if qq!=2:
        #     print "Nope, there has to be two of them", qq
        #     sys.exit(0)
        
        #if not hasWm and not hasWp and not hasZ: continue
        #if not hasGamma: continue

        dcount += 1
        #if dcount >10000:
        #    continue

            
        tri = diLep + gamma
        
        if hi==0:
            #print dcount,"No higgs??? what's up with that??"
            h.fill1DHist(tri.M(),   "h_mass_noHiggs",";M(ll#gamma)",  200, 80,180,1, "")            
            h.fill1DHist(tri.M(),   "h_mass_zoom_noHiggs",";M(ll#gamma)",  200, 124,126,1, "")            
            h.fill1DHist(diLep.M(), "h_mumu_noHiggs",";M(ll)",        200, 80,180,1, "")            
            h.fill1DHist(gamma.Pt(),"gamma_pt_noHiggs","; pt_#gamma", 200, 00,180,1, "")            
        else:
            h.fill1DHist(trueHiggs.M(),   "h_mass_trueHiggs",";mH",   200, 124,126,1, "")            

            #exit(0)

        gammaCM = TLorentzVector(gamma)
        diLepCM = TLorentzVector(diLep)
        b1  = TVector3(-tri.BoostVector())
        gammaCM.Boost(b1)
        diLepCM.Boost(b1)

        c1=Double(0)
        c2=c3=phi=1.1
        ang.SetAngles(l2,l1,gamma)
        c1 = ang.GetCos1()
        c2 = ang.GetCos2()
        c3 = ang.GetCosTheta()
        phi = ang.GetPhi()
        
        #print dcount, c1, c2, phi, c3
        #if dcount>20: break
        
        h.fill1DHist(c1,  "ang_co1",";gen cos_lp",  100,-1,1, 1,"");
        h.fill1DHist(c2,  "ang_co2",";gen cos_lm",  100,-1,1, 1,"");
        h.fill1DHist(c3,  "ang_co3",";gen cosTheta",100,-1,1, 1,"");
        h.fill1DHist(phi, "ang_phi",";gen phi lp",  100, -TMath.Pi(), TMath.Pi(), 1,"");

                   
        h.fill1DHist(l1.M(),    "l1_mass",  ";l+ mass",    200, -2,2, 1, "")
        h.fill1DHist(l2.M(),    "l2_mass",  ";l- mass",    200, -2,2, 1, "")

        #h.fill1DHist(g1.M(),    "g1_M",  ";g1 M",    200, -2,2, 1, "")
        #h.fill1DHist(g2.M(),    "g2_M",  ";g2 M",    200, -2,2, 1, "")
        
        h.fill1DHist(diLep.M(),     "gen_Mll_0",";gen_Mll, GeV",100,0,15, 1,"");
        if gamma.Pt()>25 and fabs(gamma.Eta())<2.5:
            h.fill1DHist(diLep.M(),     "gen_Mll_1",";gen_Mll, GeV",100,0,15, 1,"")

            if lPt1.Pt()>23 and lPt2.Pt()>4 and fabs(lPt1.Eta())<2.4 and  fabs(lPt2.Eta())<2.4:
                h.fill1DHist(diLep.M(),     "gen_Mll_2",";gen_Mll, GeV",100,0,15, 1,"");            
                h.fill1DHist(diLep.M(),     "gen_Mll_3",";gen_Mll, GeV",100,0,15, 1,"");

        h.fill1DHist(gamma.M(),"gamma_mass",  ";gamma mass",    200, -2,2, 1, "")
        #h.fill1DHist(g1.Pt(),    "g1_pt",  ";g1 pt",    50, 0,100, 1, "")
        #h.fill1DHist(g2.Pt(),    "g2_pt",  ";g2 pt",    50, 0,100, 1, "")
        
        #h.fill1DHist(l1.Pt(),    "l1_pt",  ";l+ pt",    50, 0,100, 1, "")    
        #h.fill1DHist(l1.Eta(),   "l1_eta", ";l+ eta",   50, -3.5,3.5, 1, "")
        #h.fill1DHist(l1.Phi(),   "l1_phi", ";l+ phi",   50, -TMath.Pi(),TMath.Pi(), 1, "")
        #h.fill1DHist(l2.Pt(),    "l2_pt",  ";l- pt",    50, 0,100, 1, "")
        #h.fill1DHist(l2.Eta(),   "l2_eta", ";l- eta",   50, -3.5,3.5, 1, "")
        #h.fill1DHist(l2.Phi(),   "l2_phi", ";l- phi",   50, -TMath.Pi(),TMath.Pi(), 1, "")
        
        h.fill1DHist(diLep.M(),   "diLep_mass",     ";M(ll), GeV", 200, 0,60,  1, "")
        h.fill1DHist(diLep.M(),   "diLep_mass_full",";M(ll), GeV", 200, 0,130, 1, "")
        h.fill1DHist(diLep.M(),   "diLep_mass_low", ";M(ll), GeV", 200, 0,1,   1, "")
        h.fill1DHist(tri.M(),     "h_mass",";M(ll#gamma), GeV",    200, 80,180,1, "")
        h.fill1DHist(tri.M(),     "h_mass_zoom",";M(ll#gamma), GeV",  200, MH-1,MH+1,  1, "")
        h.fill1DHist(tri.M(),     "h_mass_zoom2",";M(ll#gamma), GeV", 200, MH-0.1,MH+0.1,  1, "")

        ## VBF Plots:
        if qq==2:
            h.fill1DHist((j1+j2).M(),   "diJet_mass",     ";M(j1,j2), GeV", 200, 0,600,  1, "")
            h.fill1DHist(fabs(j1.Eta()+j2.Eta()), "diJet_dEta",";|dEta(j1,j2)", 200, 0,6,  1, "")

        '''
        if not hasGlu3:
            h.fill1DHist(tri.Pt(),    "h_pt",";Pt of the Higgs",  200, 0,200,  1, "")
            h.fill1DHist(tri.Pz(),    "h_z", ";Pz of the Higgs",  200, -300,300,  1, "")
        else:
        h.fill1DHist(g3.Pt(),   "g3_pt",  ";glu3 pt",   50, 0,100, 1, "")
        h.fill1DHist(g3.Eta(),  "g3_eta", ";glu3 eta",  50, -5,5, 1, "")
        h.fill1DHist(g3.Phi(),  "g3_phi", ";glu3 phi",  50, -4,4, 1, "")

            h.fill1DHist(tri.Pt(),    "h_pt_2","Extra ISR glu;Pt of the Higgs",  200, 0,200,  1, "")
            h.fill1DHist(tri.Pz(),    "h_pz_2","Extra ISR glu;Pz of the Higgs",  200, -300,300,  1, "")
            h.fill1DHist((tri+g3).Pt(),    "h_pt_glu3","Extra ISR glu;Pt of the Higgs+gluon",  200, 0,200,  1, "")
            h.fill1DHist((tri+g3).Pz(),    "h_pz_glu3","Extra ISR glu;Pz of the Higgs+gluon",  200, -300,300,  1, "")
        '''
        
        h.fill1DHist(gammaCM.E(), "gamma_Ecom",";E_{#gamma} in CoM, GeV",  50, 0,200,  1, "")
        h.fill1DHist(diLepCM.E(), "diLep_Ecom",";Ecom(ll), GeV", 50, 0,100,  1, "")


        h.fill1DHist(diLep.Pt(),    "diLep_pt",  ";diLep_pt, GeV",    50, 0,100, 1, "")
        h.fill1DHist(diLep.Eta(),   "diLep_eta", ";diLep_eta",   50, -3.5,3.5, 1, "")
        h.fill1DHist(diLep.Phi(),   "diLep_phi", ";diLep_phi",   50, -TMath.Pi(),TMath.Pi(), 1, "")
        h.fill1DHist(gamma.E(),  "gamma_E",  ";gamma_E, GeV",   50, 0,200, 1, "")
        h.fill1DHist(gamma.Pt(), "gamma_pt", ";gamma_pt",  50, 0,100, 1, "")
        h.fill1DHist(gamma.Eta(),"gamma_eta",";gamma_eta", 50, -3.5,3.5, 1, "")
        h.fill1DHist(gamma.Phi(),"gamma_phi",";gamma_phi", 50, -TMath.Pi(),TMath.Pi(), 1, "")
        
        h.fill1DHist(lPt1.Pt(),    "lPt1_pt",  ";Leading lepton pt",    50, 0,100, 1, "")
        h.fill1DHist(lPt1.Eta(),   "lPt1_eta", ";Leading lepton eta",   50, -3.5,3.5, 1, "")
        h.fill1DHist(lPt1.Phi(),   "lPt1_phi", ";Leading lepton phi",   50, -TMath.Pi(),TMath.Pi(), 1, "")
        h.fill1DHist(lPt2.Pt(),    "lPt2_pt",  ";Trailing lepton pt",    50, 0,100, 1, "")
        h.fill1DHist(lPt2.Eta(),   "lPt2_eta", ";Trailing lepton  eta",  50, -3.5,3.5, 1, "")
        h.fill1DHist(lPt2.Phi(),   "lPt2_phi", ";Trailing lepton  phi",  50, -TMath.Pi(),TMath.Pi(), 1, "")
        
        h.fill2DHist(lPt1.Pt(), lPt2.Pt(), "h2D_Pt1_vs_Pt2", ";Leading lepton pt; Trailing lepton pt",    100, 0,80, 100,0,50, 1, "")
        h.fill2DHist(l1.Pt(),   l2.Pt(),   "h2D_l1_vs_l2",   ";l+ pt; l- pt",    50, 0,100, 50,0,100, 1, "")
        h.fill2DHist(diLep.Pt(),  gamma.Pt(),"h2D_diLep_vs_gamma",     ";Pt of ll system; pt of gamma",   50, 0,100, 50,0,100, 1, "")
        h.fill2DHist(gammaCM.E(), gamma.Pt(),"h2D_gamma_Ecom_vs_Pt",   ";E_{#gamma} in CoM; Photon Pt",   50, 0,100, 50,0,100, 1, "")
        h.fill2DHist(gammaCM.E(), tri.M(),   "h2D_gamma_Ecom_vs_triM", ";E_{#gamma} in CoM; M(ll#gamma)", 50, 0,100, 50,0,200, 1, "")
        
        h.fill2DHist(gamma.Pt(), diLep.Eta()-gamma.Eta(),"h2D_gammaPt_vs_deltaEta", ";Pt_{#gamma}; #Delta#eta(ll, #gamma)",    50, 0,100, 50,-5,5, 1, "")
        
        
        h.fill1DHist(diLep.DeltaR(gamma),               "dR_diLep_gamma", ";dR(ll, #gamma)",         50, 0,10, 1, "")
        h.fill1DHist(fabs(diLep.Eta() - gamma.Eta()),   "dEta_diLep_gamma", ";|dEta(ll, #gamma)|",   50, 0,10, 1, "")
        h.fill1DHist((diLep.Vect()+gamma.Vect()).Pt(),  "diff_diLep_gamma_pt", ";four vector sum (diLep+#gamma).Pt()", 50, -20,20, 1, "")

        h.fill1DHist(TVector2.Phi_mpi_pi(diLep.Phi()-gamma.Phi()), "dPhi_diLep_gamma", ";dPhi(ll, #gamma)",            50, -10,10, 1, "")
        
        h.fill1DHist(l1.DeltaR(l2),     "dR_l1_l2",     ";dR(l+, l-)",      50, 0,5, 1, "")
        h.fill1DHist(diLep.DeltaR(l1),  "dR_diLep_l1",  ";dR(diLep, l+)",   50, 0,5, 1, "")
        h.fill1DHist(diLep.DeltaR(l2),  "dR_diLep_l2",  ";dR(diLep, l-)",   50, 0,5, 1, "")

        
    print "Total events = ", dcount
    
if __name__ == "__main__":
    gROOT.ProcessLine(".L ~/tdrstyle.C")
    setTDRStyle()
    TH1.SetDefaultSumw2(kTRUE)
    #gStyle.SetOptStat(1)
    
    pathBase = outpath
    path = pathBase+subdir
    if not os.path.exists(path):
        os.makedirs(path)

    FillAllHists(files["one"],  h1)
    FillAllHists(files["two"],  h2)


    oneFile.cd()
    oneFile.Write()
    twoFile.cd()
    twoFile.Write()
    testFile.cd()
    testFile.Write()
    print "Saved files: \n",testFile.GetName(), "\n", oneFile.GetName(), "\n", twoFile.GetName()


    blah = []

    u.drawAllInFile(oneFile, "MAD ele", twoFile, "MAD mu",None,"","", path, None,"norm", isLog=True)
    #u.drawAllInFile(oneFile, "MCFM ele", twoFile, "Madgraph mu",None,"","", path, None,"norm")
    #u.drawAllInFile(oneFile, "vbf ele", twoFile, "vbf mu",None,"","", path, None,"norm", isLog=True)
    #u.drawAllInFile(twoFile, "MAD-125",None,"", None,"","", path, None,"norm")

    u.createDir(path+"/eff")

    h0 = oneFile.Get("gen_Mll_0")
    h1 = oneFile.Get("gen_Mll_1")
    h2 = oneFile.Get("gen_Mll_2")
    r1 = h1.Clone()
    r1.Divide(h0)
    r2 = h2.Clone()
    r2.Divide(h0)

    r1.Draw("hist")
    r2.Draw("hist same")
    r1.SetMinimum(0)
    r1.SetMaximum(1)
    r1.SetTitle(";Mll gen at LHE; acc")
    r1.SetLineColor(kRed+1)
    r2.SetLineColor(kGreen+1)
    leg = TLegend(0.20,0.2,0.90,0.30);
    leg.AddEntry(r1,"photon pt>25, eta<2.5", "l")
    leg.AddEntry(r2,"photon pt>25 and p_{T}(l1)>23, p_{T}(l2)>4", "l")
    leg.SetTextSize(0.04)
    leg.SetFillColor(kWhite)
    leg.Draw()
    #c1.SaveAs(path+"/eff/acceptance_Mll_LHE.png")

            
    plot_types =[]
    list = os.listdir(pathBase)
    for d in list:
        if os.path.isdir(pathBase+"/"+d):
            plot_types.append(d)

    ht.makeHTML("Plots from an lhe file",pathBase, plot_types, blah, subdir)

    testFile.Close()
    oneFile.Close()
    twoFile.Close()


    print "\n\t\t finita la comedia \n"

