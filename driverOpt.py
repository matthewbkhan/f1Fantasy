import pandas as pd
import numpy as np
import sys

driverData  = pd.read_csv('./driverData.csv')
driverList  = driverData["DRIVER"].values
driverTeam  = driverData["TEAM"].values
driverCosts = driverData["COST"].values
qualiPos    = driverData["QUALIPOS"].values
racePos     = driverData["RACEPOS"].values
raceStdDev  = driverData["RACESTDDEV"].values
pFinish     = driverData["PFINISH"].values
pDNF        = 1.-pFinish

""" Randomly distributes the positions with user specified std dev """
randomPositions = [np.random.normal(rP,stdDev) for rP,stdDev in zip(racePos,raceStdDev)]
sortedRandPos, sortedDrivers = zip(*sorted(zip(randomPositions,driverList)))
sortedRandPos, sortedDrivers = np.array(sortedRandPos), np.array(sortedDrivers)
sortedRandPos = np.arange(1,21,1)
racePos       = np.array([sortedRandPos[np.where(sortedDrivers==dL)[0][0]] for dL in driverList])

currentTeam = ["MER","LEC","SAI","NOR","BOT","MAG"]

""" Quali and race points, assumes that P1 gets fastest lap """
qualiPoints  = np.array([10,  9, 8, 7, 6, 5,4,3,2,1,0,0,0,0,0,0,0,0,0,0])
racePoints   = np.array([25+5,18,15,12,10,8,6,4,2,1,0,0,0,0,0,0,0,0,0,0])

teamsList     = ["MER","RED","FER","MCL","ALP","REN","AST","ALF","WIL","HAA"]
teamCostsDict = {"MER":34.5,"RED":32.5,"FER":25.0,"MCL":18.5,"ALP":10.5,"REN":14.0,"AST":11.5,"ALF":8.0,"WIL":7.0,"HAA":6.0}

""" Q1: 1 pnt, Q2: 2 pnts, Q3: 3 pnts """
knockOutPnts = []
for qP in qualiPos:
    if(qP>15):
        knP = 1
    elif(qP<=15 and qP>10):
        knP = 2
    else:
        knP = 3
    knockOutPnts.append(knP)

""" +/-2 pnts per position change, max +/-10 """
chngPosPnts = []
for cPP in 2*np.array(qualiPos-racePos):
    if(cPP<0):   chngPosPnts.append(np.max([cPP,-10]))
    elif(cPP>=0):chngPosPnts.append(np.min([cPP, 10]))

""" 3 points for beating teammate in race """
teamMateRcePoints = []
for dI,dT,rP in zip(range(len(driverList)),driverTeam,racePos):
    teamMates = np.where(driverTeam==dT)[0]
    teamMate  = np.delete(teamMates,np.where(teamMates==dI)[0])[0]
    teamMtPos = racePos[teamMate]
    if(rP<teamMtPos):
        teamMateRcePoints.append(3)
    else:
        teamMateRcePoints.append(0)

""" 2 points for beating teammate in quali """
teamMateQualiPoints = []
for dI,dT,qP in zip(range(len(driverList)),driverTeam,qualiPos):
    teamMates = np.where(driverTeam==dT)[0]
    teamMate  = np.delete(teamMates,np.where(teamMates==dI)[0])[0]
    teamMtPos = qualiPos[teamMate]
    if(qP<teamMtPos):
        teamMateQualiPoints.append(2)
    else:
        teamMateQualiPoints.append(0)

""" Total driver points """
driverPoints = qualiPoints[qualiPos-1] + knockOutPnts + teamMateQualiPoints + pFinish*(racePoints[racePos-1] + chngPosPnts + teamMateRcePoints + 1) + pDNF*(-10.)

""" Order driver in points """
sortedPoints, sortedDrivers, sortedCosts = zip(*sorted(zip(driverPoints,driverList,driverCosts)))
sortedPoints, sortedDrivers, sortedCosts = np.array(sortedPoints)[::-1], np.array(sortedDrivers)[::-1], np.array(sortedCosts)[::-1]
print "DRVR, PNTS"
for sD,sP,sC in zip(sortedDrivers,sortedPoints,sortedCosts):
    if(sC<=20):
        print "%s*, %i"%(sD,sP)
    else:
        print "%s,  %i"%(sD,sP)

""" Order driver in value """
driverValue = driverPoints/driverCosts
sortedValue, sortedDrivers = zip(*sorted(zip(driverValue,driverList)))
sortedValue, sortedDrivers = np.array(sortedValue)[::-1], np.array(sortedDrivers)[::-1]
print "\n##########"
print "DRV, PNTS/$"
for sD,sV in zip(sortedDrivers,sortedValue):
    print "%s, %.3f"%(sD,sV)

""" Main loop, it ain't pretty """
maxPoints    = 0.
indexRange   = np.arange(len(driverList))
iterationInd = 0
print "\n##########"
for team in teamsList:
    for i1,d1,c1,p1,t1 in zip(indexRange,driverList,driverCosts,driverPoints,driverTeam):
        for i2,d2,c2,p2,t2 in zip(indexRange[i1+1:],driverList[i1+1:],driverCosts[i1+1:],driverPoints[i1+1:],driverTeam[i1+1:]):
            for i3,d3,c3,p3,t3 in zip(indexRange[i2+1:],driverList[i2+1:],driverCosts[i2+1:],driverPoints[i2+1:],driverTeam[i2+1:]):
                for i4,d4,c4,p4,t3 in zip(indexRange[i3+1:],driverList[i3+1:],driverCosts[i3+1:],driverPoints[i3+1:],driverTeam[i3+1:]):
                    for i5,d5,c5,p5,t4 in zip(indexRange[i4+1:],driverList[i4+1:],driverCosts[i4+1:],driverPoints[i4+1:],driverTeam[i4+1:]):
                        if(iterationInd%15500==0): print "%i%%"%(100.*iterationInd/155000.)
                        iterationInd += 1
                        totalCost = c1+c2+c3+c4+c5+teamCostsDict[team]
                        if(totalCost>100.):continue
                        teamPoints   = np.sum(driverPoints[np.where(driverTeam==team)])-3-2 #NB the -2 might be wrong for pFinish!=1
                        lineUpCosts  = np.array([c1,c2,c3,c4,c5])
                        driverLineUp = np.array([d1,d2,d3,d4,d5])
                        lineUpPoints = np.array([p1,p2,p3,p4,p5])
                        turboPoint   = np.max(lineUpPoints[lineUpCosts<=20.])
                        """ Points reduction for switching """
                        if(team in currentTeam):
                            numDiff = 0
                        else:
                            numDiff = 1
                        for dLU in driverLineUp:
                            if(dLU not in currentTeam):
                                numDiff += 1
                        switchCost   = np.min([0,-10.*(numDiff-3)])
                        totPoints    = np.sum(lineUpPoints)+teamPoints+turboPoint+switchCost
                        if totPoints>maxPoints:
                            bestDrivers = driverLineUp
                            bestTeam    = team
                            turboDrive  = driverLineUp[np.argmax(lineUpPoints*(lineUpCosts<=20.))]
                            maxPoints   = totPoints
                            bestCost    = totalCost

""" Results! """
print "Drivers List: ",bestDrivers
print "Constructors: ",bestTeam
print "Turbo Driver: ",turboDrive
print "Prdcted Pnts: ",maxPoints
print "Total Cost/$: ",bestCost
