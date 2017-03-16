__author__ = 'uber'
from nose.tools import *
import wntr.epanet.pyepanet as pyepanet
import pandas as pd
import wquantiles
import os

# uses pyepanet included with WNTR - https://github.com/USEPA/WNTR

# -- network water quality statistics over time, from the population of volume-weighted quality --
# this answers the question "what is the mean/median/x-percentile water quality delivered to customers,
# if you were actually measuring it for each liter (say) of water that runs through any customer connection."
# Results are put in a csv file, and simulation results are saved in hdf5 for later use.

# input file - either Epanet (inp) or HDF5 stored results (h5) depending on extension
inpFile = 'Net1.inp'
# quality statistics are computed every statStep (hours) for the entire network,
statStep = 1.0
# over a backward looking time window of statWindow (also hours)
statWindow = 1.0

# statistics/simulation output files
ext = os.path.splitext(inpFile)[1]
root = os.path.splitext(inpFile)[0]
outFile = root + '.csv'

if ext == '.inp':
    en = pyepanet.ENepanet()
    en.inpfile = inpFile
    assert_equal(0, en.isOpen())
    en.ENopen(en.inpfile,'tmp.rpt')
    assert_equal(1, en.isOpen())

    # store demands and quality results for each node in a simulation-time-indexed dataframe
    nNodes = en.ENgetcount(pyepanet.EN_NODECOUNT) - en.ENgetcount(pyepanet.EN_TANKCOUNT)
    demand = pd.DataFrame(columns=(range(1,nNodes+1)))
    quality = pd.DataFrame(columns=(range(1,nNodes+1)))
    step = []

    # simulation
    en.ENsolveH()
    en.ENopenQ()
    en.ENinitQ(pyepanet.EN_NOSAVE)
    tstep = 1
    while tstep > 0:
        t = en.ENrunQ()/3600.0
        q = []
        d = []
        for i in range(1,nNodes+1):
            q.append(en.ENgetnodevalue(i,pyepanet.EN_QUALITY))
            d.append(en.ENgetnodevalue(i,pyepanet.EN_DEMAND))
        demand.loc[t] = d
        quality.loc[t] = q
        tstep = en.ENnextQ()/3600.0
        step.append(tstep)
        print('simulation time =',t)
    en.ENcloseQ()

    # weight by volume, not demand
    volume = demand.multiply(step,axis=0)

    # store results for later use
    store = pd.HDFStore(root+'.h5')
    store['quality'] = quality
    store['volume'] = volume
    store.close()

elif ext == '.h5':
    store = pd.HDFStore(inpFile)
    quality = store['quality']
    volume = store['volume']
    store.close()

else:
    print('Input file must be Epanet or HDF5 format')
    exit(1)

# quality statistics over time
t = max(statStep,statWindow)
tEnd = max(volume.index)
qStat = pd.DataFrame(columns=['median','Q1','Q3'])
while t <= tEnd:
    v = volume[(volume.index >= t-statWindow) & (volume.index < t)].as_matrix().flatten()
    q = quality[(quality.index >= t-statWindow) & (quality.index < t)].as_matrix().flatten()

    # stats
    median = wquantiles.quantile_1D(q,v,0.5)
    q1 = wquantiles.quantile_1D(q,v,0.25)
    q3 = wquantiles.quantile_1D(q,v,0.75)
    qStat.loc[t] = [median, q1, q3]

    print('time=',t,', Q1=',q1,', Median=',median,', Q3=',q3)

    t += statStep

qStat.to_csv(outFile)

exit(0)
