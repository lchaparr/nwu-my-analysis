#!/usr/bin/env python
import sys
from ROOT import *
gROOT.SetBatch()
from rooFitBuilder import *
sys.path.append("../zgamma")
import utils as u
import ConfigParser as cp
gROOT.ProcessLine(".L ~/tdrstyle.C")
setTDRStyle()

print len(sys.argv), sys.argv

cf = cp.ConfigParser()
cf.read('config.cfg')
subdir = cf.get("fits","ver")  
yearList   = [a.strip() for a in (cf.get("fits","yearList")).split(',')]
leptonList = [a.strip() for a in (cf.get("fits","leptonList")).split(',')]
catList    = [a.strip() for a in (cf.get("fits","catList")).split(',')]
    
plotBase = "/uscms_data/d2/andreypz/html/zgamma/dalitz/fits-"+subdir
u.createDir(plotBase)
rooWsFile = TFile(subdir+'/testRooFitOut_Dalitz.root')
myWs    = rooWsFile.Get('ws')
card_ws = RooWorkspace('ws_card')
card_ws.autoImportClassCode(True)

c = TCanvas("c","c",0,0,500,400)
c.cd()
mzg = myWs.var('CMS_hzg_mass')
mzg.setRange('signal',120,130)

bkgModel = 'Bern5'

# #######################################
# prep the background and data card    #
# we're going to the extend the bg pdf #
# and rename the parameters to work    #
# with the higgs combination tool      #
# #######################################

#myWs.Print()

for year in yearList:
  for lepton in leptonList:
    for cat in catList:
      dataName = '_'.join(['data',lepton,year,'cat'+cat])
      suffix   = '_'.join([year,lepton,'cat'+cat])
      print dataName, suffix

      fitName  = '_'.join([bkgModel,year,lepton,'cat'+cat])
      normName = 'norm'+bkgModel+'_'+suffix      
    
      print fitName, dataName
      data = myWs.data(dataName)
      fit  = myWs.pdf(fitName)

      ###### Extend the fit (give it a normalization parameter)
      print dataName
      sumEntriesBkg = data.sumEntries()
      sumEntriesSig = data.sumEntries('1','signal')
      print sumEntriesBkg, sumEntriesSig

      raw_input()

      dataYieldName = '_'.join(['data','yield',lepton,year,'cat'+cat])
      dataYield     = RooRealVar(dataYieldName,dataYieldName,sumEntriesBkg)
      norm          = RooRealVar(normName,normName,sumEntriesBkg,sumEntriesBkg*0.25,sumEntriesBkg*1.75)

      fitExtName    = '_'.join(['bkgTmp',lepton,year,'cat'+cat])
      fit_ext       = RooExtendPdf(fitExtName,fitExtName, fit,norm)

      fit_ext.fitTo(data,RooFit.Range('dalitzRegion'))

      testFrame = mzg.frame(RooFit.Range('dalitzRegion'))
      data.plotOn(testFrame, RooFit.Binning(50))
      fit_ext.plotOn(testFrame, RooFit.Name(bkgModel),  RooFit.LineColor(kBlue))

      #sigName = '_'.join(['ds_sig','gg',lepton,year,'cat'+cat,'M125'])
      sigName = 'pdf_sig_mu_2012_cat0_M125'
      myWs.Print()
      #sigP  = myWs.data(sigName)
      sigP  = myWs.pdf(sigName)
      #sigHist = sigP.createHistogram()
      #sigHist.Scale(50)
      #sigP  = myWs.pdf(sigName)
      #sigP.plotOn(testFrame, RooFit.LineColor(kRed+2),RooFit.Normalization(0.0))
      sigP.plotOn(testFrame,  RooFit.Name('signal'), RooFit.LineColor(kRed+2), RooFit.Normalization(3.4 *50*7.4e-05))

      leg  = TLegend(0.65,0.7,0.87,0.87)
      leg.SetFillColor(0)
      leg.SetShadowColor(0)
      leg.SetBorderSize(1)
      leg.AddEntry(testFrame.findObject(bkgModel),bkgModel,'l')
      leg.AddEntry(testFrame.findObject('signal'),'50x ggH','l')
      
      testFrame.SetTitle(";m_{H} (GeV);Events/2 GeV")
      testFrame.Draw()
      leg.Draw()
      c.SaveAs(plotBase+'/'+'_'.join(['best_fit',year,lepton,'cat'+cat])+'.png')

      ###### Import the fit and data, and rename them to the card convention
      dataNameNew = '_'.join(['data','obs',lepton,year,'cat'+cat])

      getattr(card_ws,'import')(data,RooFit.Rename(dataNameNew))
      getattr(card_ws,'import')(fit_ext)
      getattr(card_ws,'import')(dataYield)
      card_ws.commitTransaction()
      fit_ext.Print()
      card_ws.Print()

      print normName
      BackgroundNameFixer(fitName, year,lepton,cat,card_ws)
            
      print "\n * The end * \n"

card_ws.writeToFile(subdir+'/testCardBackground_Dalitz.root')
