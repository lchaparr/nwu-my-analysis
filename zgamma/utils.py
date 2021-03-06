#! /usr/bin/env python
from optparse import OptionParser
import sys,os,datetime,re
from array import *
from ROOT import *
gROOT.SetBatch()

import ConfigParser as cp
conf = cp.ConfigParser()
conf.read('../zgamma/config.cfg')
lumi2012 = float(conf.get("lumi","lumi2012A")) + float(conf.get("lumi","lumi2012B"))+\
           float(conf.get("lumi","lumi2012C")) + float(conf.get("lumi","lumi2012D"))
lumi = lumi2012

def setSelection(sel):
    conf.set("selection","sel", sel)
def getSelection():
    conf.get("selection","sel")

def getCuts(cp, name="cuts-mu"):
    cuts = []
    for key, cut in sorted(cp.items(name)):
        cuts.append(cut)
    return cuts
    #print key, cut

def getLumi(period):
    if period=="2012":
        return lumi2012
    else:
        print "Sorry only 2012 is considered"
        return 0

def getCS(sample, useMCFM=False):
    sel = conf.get("selection", "sel")[0:2]
    if "ggH" in sample:
        cs = float(conf.get(sample, "cs-"+sel))      
        if useMCFM:
            cs = cs*2
    elif "vbfH" in sample:
        cs = float(conf.get(sample, "cs-"+sel))      
    else:
        cs = float(conf.get(sample, "cs"))      

    return cs

def handleOverflowBins(hist):
    if hist == None:
        return
    nBins   = hist.GetNbinsX()
    lastBin = hist.GetBinContent(nBins)
    ovflBin = hist.GetBinContent(nBins+1);
    lastBinErr = hist.GetBinError(nBins);
    ovflBinErr = hist.GetBinError(nBins+1);
    firstBin    = hist.GetBinContent(1);
    undflBin    = hist.GetBinContent(0);
    firstBinErr = hist.GetBinError(1);
    undflBinErr = hist.GetBinError(0);
    if hist.GetName()!="diLep_mass_low":
        hist.SetBinContent(nBins, lastBin+ovflBin);
    hist.SetBinError(nBins, sqrt(pow(lastBinErr,2) + pow(ovflBinErr,2)) );
    hist.SetBinContent(1, firstBin+undflBin);
    hist.SetBinError(1, sqrt(pow(firstBinErr,2) + pow(undflBinErr,2)) );
    hist.SetBinContent(0,0);
    hist.SetBinContent(nBins+1,0);

    #if sample!="data":
     #   if lumi!=0: #don't rescale, for the cases we don't want it
      #      hist.Scale(float(lumi*cs(sample))/Nev(sample))
            #hist.SetLineColor(xc[sample][0])
            #hist.SetFillStyle(xc[sample][1])
            #hist.SetFillColor(xc[sample][2])


def draw(h1, path):
    h = h1
    if h.InheritsFrom("TH2"):
        h.Draw("lego")
    else:
        h.Draw("hist")

    c1.SaveAs(path+h.GetName()+".png")

def blindIt(h):
    hbin =  h.FindBin(125)
    for b in xrange(hbin-10,hbin+10):
        h.SetBinContent(b,0)
    
def set_palette(name="palette", ncontours=999):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""

    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    elif name=="signal":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.90, 0.60, 0.40, 0.20]
        green = [0.00, 0.00, 0.00, 0.00, 0.00]
        blue  = [0.00, 0.00, 0.00, 0.00, 0.00]
    # elif name == "whatever":
        # (define more palettes)
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)

    npoints = len(s)
    TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    gStyle.SetNumberContours(ncontours)
    

def createDir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except OSError:
            if os.path.isdir(dir):
                pass
            else:
                raise

def drawAllInFile(f1, name1, f2, name2, f3, name3, dir,path, N, howToScale="none", isLog=False, doRatio=False):
    f1.cd(dir)
    dirList = gDirectory.GetListOfKeys()
    #dirList.Print()
    createDir(path)
    scale2 = scale3 = 1
    split = os.path.split(path)
    print "Split lit lit", split[0], split[1]

    doOverflow = 0
    if doRatio:
        c1 = TCanvas("c2","big canvas",600,700);
    else:
        c1 = TCanvas("c3","small canvas",600,600);
    c1.SetLogy(isLog)
    c1.cd()

    if f2!=None and howToScale=="lumi": # only assume signal MC for now
        Nev = f2.Get("Counts/evt_byCut_raw").GetBinContent(1)
        cro = getCS("dy")
        scale2 = float(1000*lumi*cro)/Nev
        print Nev, lumi, cro, scale2
        
        
    if f3!=None and howToScale=="lumi": # only assume signal MC for now
        Nev = f3.Get("Counts/evt_byCut_raw").GetBinContent(1)
        cro = getCS("ggH-125")
        scale3 = float(lumi*cro)/Nev
        print Nev, lumi, cro, scale3


    for k1 in dirList:
        if k1.GetName() in ["eff"]: continue
        if N!=None:
            if not("cut"+N) in k1.GetName(): continue
        h1 = k1.ReadObj()

        h2 = TH1F()
        h3 = TH1F()

        hmaxs = []
        
        if f2!=None:
            #f2.Print()
            if dir!="":
                h2 = f2.Get(dir+"/"+k1.GetName()) #assumes that the histograms in signal file have the same names  
            else:
                print k1.GetName()
                h2 = f2.Get(k1.GetName())
            if h2==None: continue
            
            h2.Scale(float(scale2))

        if f3!=None:
            if dir!="":
                h3 = f3.Get(dir+"/"+k1.GetName())
            else:
                h3 = f3.Get(k1.GetName())
            if h3==None: continue
            
            h3.Scale(float(scale3))


        print "drawing", h1.GetName()

        if h1.InheritsFrom("TH2"):
            createDir(split[0]+"/TH2_"+split[1])
            h1.Draw("col")
            prename = split[0]+"/TH2_"+split[1]+"/"+h1.GetName()
            c1.SaveAs(prename+"_data.png")
            if f3!=None and h3!=None:
                h3.Draw("col")
                c1.SaveAs(prename+"_sig.png")

            continue
        
            #set_palette("gray")
            #h1.Draw("col same")
            #if "h2D_tri_vs_diLep_mass" in h1.GetName():
            #    c1.SetLogy()
                
        else:
            pad1 = TPad("pad1","pad1",0,0.3,1,1);
            pad2 = TPad("pad2","pad2",0,0,1,0.3);

            if doRatio:
                pad1.SetBottomMargin(0);
                pad1.Draw();
                pad1.cd();
                pad1.SetLogy(isLog)
                
            
            if doOverflow:
                handleOverflowBins(h1)

            h1.Draw("hist")
            #h1.GetRange
            #h1.SetMarkerStyle(20)
            h1.SetLineColor(kBlack)
            h1.UseCurrentStyle()
            
            #if "tri_mass" in k1.GetName() and name1 not in ["madgra","mcfm"]:
            #    blindIt(h1)
            if "h_mass" in k1.GetName():
                print "\n *** H-mass RMS:",  h1.GetRMS(), h2.GetRMS()
                print "\n *** H-mass Mean:", h1.GetMean(),h2.GetMean()
                 
            leg = TLegend(0.70,0.8,0.90,0.90);
            leg.AddEntry(h1,name1, "l")
            leg.SetTextSize(0.03)

            #if "phi" in h1.GetName():
            #    h1.SetMinimum(0)
            #    if howToScale=="norm":
            #        h1.SetMaximum(0.035)

            norm1 = h1.Integral()
            if howToScale =="norm" and  norm1!=0:
                h1.Scale(1./norm1)
                hmaxs.append(h1.GetMaximum())
                         
            if f2!=None and h2!=None:
                if doOverflow:
                    handleOverflowBins(h2)
                h2.Draw("same hist")
                h2.SetLineColor(kBlue+1)
                norm2 = h2.Integral()
                if howToScale =="norm" and  norm2!=0:
                    h2.Scale(1./norm2)
                    hmaxs.append(h2.GetMaximum())

                leg.AddEntry(h2,name2, "l")
                

            if f3!=None and h3!=None:
                if doOverflow:
                    handleOverflowBins(h3)
                h3.Draw("sames hist")
                h3.SetLineColor(kRed+1)
                extract_from_name = re.findall(r'\d+', name3)
                #print extract_from_name
                if len(extract_from_name) == 1:
                    h3.Scale(int(extract_from_name[0]))
                norm3 = h3.Integral()
                if howToScale =="norm" and  norm3!=0:
                    h3.Scale(1./norm3)
                    hmaxs.append(h3.GetMaximum())
                leg.AddEntry(h3,name3, "l")
                
                if doRatio:
                    c1.cd()
                    pad2.SetBottomMargin(0.25);
                    pad2.SetTopMargin(0);
                    pad2.Draw();
                    pad2.cd();
                    
                    r = h1.Clone("")                                        
                    r.Divide(h3);
                    r.GetYaxis().SetTitle("Data/MC");
                    r.SetMaximum(2);
                    r.SetMinimum(0);
                    r.GetYaxis().SetNdivisions(206);
                    r.GetYaxis().SetTitleOffset(0.4);
                    r.SetTitleSize(0.1,"XYZ");
                    r.SetLabelSize(0.1,"XY");
                    
                    r.Draw("e1p");
                    
                    pad1.cd();
            
            #prelim = TLatex(0.15,0.95, "CMS Preliminary %s #it{L_{int}} = %0.1f fb^{-1}" % (8, 19.6))
            #prelim.SetNDC();
            #prelim.SetTextSize(0.03);
            #prelim.Draw();
            if howToScale =="norm":
                #print "HMAXS=",hmaxs
                if len(hmaxs)>0:
                    m = max(hmaxs)
                    h1.SetMaximum(1.1*m)
                h1.GetYaxis().SetTitle("a.u.")

            # Here we consider particular cases (histograms) that need special care
            if "tri_mass_longTail" in h1.GetName() and howToScale=="lumi":
                h1.SetMaximum(750)

            if "diLep_mass_low" in h1.GetName() and howToScale=="norm" and f2!=None:
                s1 = h1.Integral(90,200)
                s2 = h2.Integral(90,200)
                h2.Scale(float(s1)/s2)
                
            c1.cd()
            leg.SetFillColor(kWhite)
            leg.Draw()

            c1.SetLogy(int(isLog))

            c1.SaveAs(path+"/"+h1.GetName()+".png")
        c1.SetLogy(0)
        
def yieldsTable(yi, sel, num=True):
    print sel
    t = []
    if len(sel)==0:
        return t
    
    cuts =  getCuts(conf, "cuts-"+sel[0][0:2])


    l1 = ["Cut/trigger"]
    if num:
        l1.insert(0,"")
    l1.extend([a for a in sel])
    print l1
    t.append(l1)
    for line in xrange(len(cuts)):
        l=[]
        if num:
            l.append(str((line-1)))
        l.append(cuts[line])
        for thissel in sel:
            l.append(yi[thissel][line])
            #print l
        t.append(l)
        
    return t
                                                        
def makeTable(table, name, opt="tex"):
    print "Making sure that the list is alright"
    n_row = len(table)
    if n_row==0: return
    n_col = len(table[0])
    for l in table:
        if len(l)!=n_col:
            print "No good, the number of columns is messed up"
            
            
    myTable = ''
    if opt=="tex":
        beginTable = '\\begin{tabular}{|'+n_col*"l|"+'} \n \\hline \n'
        endTable   = '\\end{tabular} \n'

        beginLine  = ''
        endLine    = ' \\\\ \\hline \n'
        separator  = ' & '


    if opt=="html":
        beginTable = '<table border = "10"    cellpadding="5">'
        endTable = '</table>'

        beginLine  = '\n<tr>\n<td>'
        endLine    = '</td>\n</tr>'
        separator  = '</td><td>'

    if opt=="twiki":
        beginTable = ''
        endTable   = ''

        beginLine  = '| '
        endLine    = ' |\n'
        separator  = ' |  '


    myTable +=beginTable
    for l in range(n_row):
        #print l, table[l]
        myTable+=beginLine
        for c in range(n_col):
            val = table[l][c]
            if not isinstance(val,str):
                myTable+="%.2f" % (table[l][c])
            else:
                myTable+=val
            if c!=n_col-1:
                myTable+=separator
        myTable+=endLine

    myTable +=endTable
    
    ifile = open("yields_"+name+"."+opt,"w")
    ifile.write(myTable)
    ifile.close()
    
    if opt in ["twiki","tex"]:
        print myTable

def getYields(f, doLumiScale=False):
    ev = f.Get("Counts/evt_byCut")
    sel = conf.get("selection", "sel")[0:2]
    cuts =  getCuts(conf, "cuts-"+sel)
    y = []
    scale=1
    if doLumiScale: # only assume signal MC for now
        Nev = ev.GetBinContent(1)
        cro = getCS("ggH-125")
        #cro = getCS("vbfH-125")
        scale = float(lumi*cro)/Nev
        print "Lumi scale for sel=",sel, "Nev=",Nev, "cro=",cro, "scale=",scale

    for a in xrange(len(cuts)):
        y.append(scale*ev.GetBinContent(a+1)) # well, that's how the histogram is set up
    return y


if __name__ == "__main__":
    print "This is utils.py script"
