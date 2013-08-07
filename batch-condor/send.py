#!/usr/bin/env python

import BatchMaster as b
import sys
cfg = b.JobConfig

from optparse import OptionParser
parser = OptionParser(usage="usage: %prog [options -e], -m, --data, --bg, --mc], -p 2011] version")
parser.add_option("-e", "--ele", dest="electron", action="store_true", default=False, help="Use electron selection (by default it will run muon selection)")
parser.add_option("--mugamma", dest="mugamma", action="store_true", default=False, help="Use Mu+Photon trigger (for running on MuEG path)")
parser.add_option("-c", "--clean", dest="clean", action="store_true", default=False, help="Clean the directory with histogram output.")
parser.add_option("--data", dest="data", action="store_true", default=False, help="Run over the data sample")
parser.add_option("--test", dest="test", action="store_true", default=False, help="Run over the test sample")

(options, args) = parser.parse_args()


if len(args) < 1:
    parser.print_usage()
    exit(1)
    
''' Specify parameters '''
dCache      = '/pnfs/cms/WAX/11/store/user' 
EOS         = '/eos/uscms/store/user'
outputPath  = EOS+'/andreypz/batch_output/zgamma/8TeV'
executable  = 'batchJob.csh'

selection = 'muon'
if options.electron:
    selection="electron"
if options.mugamma:
    selection="mugamma"
    if options.electron:
        print "Warning! We can't run both selections simultaneously.."
        exit(1)
                                            
    
version    = args[0]
period    = '2012'
doTest    = options.test
doData    = options.data
doBG      = 0
doSignal  = 0

''' 
    Set job configurations.  The order of arguments is:
    (Dataset, path to data, number of jobs, arguments to pass to executable, output directory name)
'''

test = []
data = []

test.extend([
    cfg('MuEG_Run2012A',        dCache+'/andreypz/nuTuples_v6_8TeV/MuEG/Run2012A-22Jan2013',         5, 'DATA mugamma 2012'),
])


if period =="2012":
    
    if selection == 'muon':
        data.extend([
            cfg('DoubleMu_Run2012A',        dCache+'/andreypz/nuTuples_v6_8TeV/DoubleMuParked/Run2012A-22Jan2013',         5, 'DATA muon 2012'),
            cfg('DoubleMu_Run2012B',        dCache+'/andreypz/nuTuples_v6_8TeV/DoubleMuParked/Run2012B-22Jan2013',        10, 'DATA muon 2012'),
            cfg('DoubleMu_Run2012C',        dCache+'/andreypz/nuTuples_v6_8TeV/DoubleMuParked/Run2012C-22Jan2013',        10, 'DATA muon 2012'),
            cfg('DoubleMu_Run2012D',        dCache+'/andreypz/nuTuples_v6_8TeV/DoubleMuParked/Run2012D-22Jan2013',        10, 'DATA muon 2012'),
            ])

    if selection == 'mugamma':
        data.extend([
            cfg('MuEG_Run2012A',        dCache+'/andreypz/nuTuples_v6_8TeV/MuEG/Run2012A-22Jan2013',         5, 'DATA mugamma 2012'),
            cfg('MuEG_Run2012B',        dCache+'/andreypz/nuTuples_v6_8TeV/MuEG/Run2012B-22Jan2013',        10, 'DATA mugamma 2012'),
            cfg('MuEG_Run2012C',        dCache+'/andreypz/nuTuples_v6_8TeV/MuEG/Run2012C-22Jan2013',        10, 'DATA mugamma 2012'),
            cfg('MuEG_Run2012D',        dCache+'/andreypz/nuTuples_v6_8TeV/MuEG/Run2012D-22Jan2013',        10, 'DATA mugamma 2012'),

            ])

    if selection == 'electron':
        data.extend([
            cfg('DoublePhoton_Run2012A',        dCache+'/andreypz/nuTuples_v6_8TeV/Photon/Run2012A-22Jan2013',         10, 'DATA electron 2012'),
            cfg('DoublePhoton_Run2012B',        dCache+'/andreypz/nuTuples_v6_8TeV/DoublePhoton/Run2012B-22Jan2013',         10, 'DATA electron 2012'),
            cfg('DoublePhoton_Run2012C',        dCache+'/andreypz/nuTuples_v6_8TeV/DoublePhoton/Run2012C-22Jan2013',         10, 'DATA electron 2012'),
            cfg('DoublePhoton_Run2012D',        dCache+'/andreypz/nuTuples_v6_8TeV/DoublePhoton/Run2012D-22Jan2013',         10, 'DATA electron 2012'),
            ])
        
        
    bg = []
    bg.extend([
        cfg('WZJetsTo3LNu',  dCache+'/andreypz/nuTuples_v5_8TeV/WZJetsTo3LNu',  1, 'WZ '+selection+' '+period),
        cfg('WWJetsTo2L2Nu', dCache+'/andreypz/nuTuples_v5_8TeV/WWJetsTo2L2Nu', 1, 'WW '+selection+' '+period),
        cfg('ZZJetsTo2L2Nu', dCache+'/andreypz/nuTuples_v5_8TeV/ZZJetsTo2L2Nu', 1, 'ZZ '+selection+' '+period),
        cfg('ttbar',         dCache+'/andreypz/nuTuples_v5_8TeV/TTJets',       10, 'ttbar '+selection+' '+period),
        cfg('tW',            dCache+'/andreypz/nuTuples_v5_8TeV/tW',            1, 'tW '+selection+' '+period),
        cfg('tbarW',         dCache+'/andreypz/nuTuples_v5_8TeV/tbarW',         1, 'tbarW '+selection+' '+period),
        cfg('DYjets',        dCache+'/andreypz/nuTuples_v5_8TeV/DYjets',       30, 'DYjets '+selection+' '+period),
        cfg('DYjets10',      dCache+'/naodell/nuTuples_v5_8TeV/DYJetsToLL_M-10To50', 20, 'DYjets10 '+selection+' '+period),
        cfg('vbfZ',          dCache+'/andreypz/nuTuples_v5_8TeV/Zvbf',          1, 'vbfZ '+selection+' '+period),
        
        cfg('WJetsToLNu',    dCache+'/naodell/nuTuples_v5_8TeV/WJetsToLNu',     5, 'WJetsToLNu '+selection+' '+period),
        cfg('WZJetsTo2L2Q',  dCache+'/naodell/nuTuples_v5_8TeV/WZJetsTo2L2Q',   1, 'WZJetsTo2L2Q '+selection+' '+period),
        cfg('ZZJetsTo2L2Q',  dCache+'/naodell/nuTuples_v5_8TeV/ZZJetsTo2L2Q',   1, 'ZZJetsTo2L2Q '+selection+' '+period),
        ])


    signal = []
    
    signal.extend([
        cfg('ggHZZ125', dCache+'/andreypz/nuTuples_v5_8TeV/ggH130', 1, 'ggHZZ125 '+selection+' '+period),
        #cfg('ggHWW125', dCache+'/andreypz/nuTuples_v5_8TeV/ggHWW130', 1, 'ggHWW125 '+selection+' '+period),
        cfg('VBFHZZ125', dCache+'/andreypz/nuTuples_v5_8TeV/VBFHZZ130', 1, 'VBFHZZ125 '+selection+' '+period),
        ])

else:
    print "Only 2012! Other periods are not supported"

inputSamples = []

if doTest:
    inputSamples.extend(test)
if doData:
    inputSamples.extend(data)
if doBG:
    inputSamples.extend(bg)
if doSignal:
    inputSamples.extend(signal)

if len(inputSamples) is not 0:
    batcher = b.BatchMaster(inputSamples, outputPath, shortQueue = False, stageDir = '../StageBatch', executable = executable, selection = version + '/' + selection +"_"+ period)
    print "Submitting to batch?"
    batcher.submit_to_batch()
            