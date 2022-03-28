import pandas as pd
import numpy as np
import sys

racesCompleted = ["BAHRAIN","SAUDI"]

driverData  = pd.read_csv('./driverData.csv')
driverList  = driverData["DRIVER"].values
driverTeam  = driverData["TEAM"].values
driverCosts = driverData["COST"].values
prdQualiPos = driverData["QUALIPOS"].values
prdRacePos  = driverData["RACEPOS"].values
raceStdDev  = driverData["RACESTDDEV"].values
pFinish     = driverData["PFINISH"].values
pDNF        = 1.-pFinish

""" Driver Qualifying - driver qualifies in the Top 10 for 5 qualifying sessions in a row           = +5  pts
    Driver Race - driver finishes in the Top 10 for 5 races in a row                                = +10 pts
    Constructor Qualifying - both drivers qualify in the Top 10 for 3 qualifying sessions in a row  = +5  pts
    Constructor Race - both drivers finish in the Top 10 for 3 races in a row                       = +10 pts """

prevQualis  = np.array([driverData[raceName+"QPOS"].values for raceName in racesCompleted])
prevRaces   = np.array([driverData[raceName+"RPOS"].values for raceName in racesCompleted])

currentTeam     = ["MER","LEC","SAI","NOR","BOT","MAG"]
currentBudget   = 100.
lwrBdgtLimit    = 70.
pointsThreshold = 200.

teamsList     = ["MER","RED","FER","MCL","ALP","REN","AST","ALF","WIL","HAA"]
# teamsList     = ["MER","RED","FER","ALP","REN","ALF","HAA"]
teamCostsDict = {"MER":34.5,"RED":32.5,"FER":25.0,"MCL":18.5,"ALP":10.5,"REN":14.0,"AST":11.5,"ALF":8.0,"WIL":7.0,"HAA":6.0}

""" Quali and race points, assumes that P1 gets fastest lap """
qualiPoints  = np.array([10,  9, 8, 7, 6, 5,4,3,2,1,0,0,0,0,0,0,0,0,0,0])
racePoints   = np.array([25,18+5,15,12,10,8,6,4,2,1,0,0,0,0,0,0,0,0,0,0])

""" Add Gaussian errors to positions """
def positionVariation(racePosition,raceStandardDeviation,driverNameList):
    """ Randomly distributes the positions with user specified std dev """
    randomPositions = [np.random.normal(rP,stdDev) for rP,stdDev in zip(racePosition,raceStandardDeviation)]
    sortedRandPos, sortedDrivers = zip(*sorted(zip(randomPositions,driverNameList)))
    sortedRandPos, sortedDrivers = np.array(sortedRandPos), np.array(sortedDrivers)
    sortedRandPos = np.arange(1,21,1)
    finalRacePos  = np.array([sortedRandPos[np.where(sortedDrivers==dL)[0][0]] for dL in driverNameList])
    return finalRacePos

""" Qualifying session points """
def knockOutSessionPoints(qualifyingPosition):
    """ Q1: 1 pnt, Q2: 2 pnts, Q3: 3 pnts """
    knockOutPnts = []
    for qP in qualifyingPosition:
        if(qP>15):
            knP = 1
        elif(qP<=15 and qP>10):
            knP = 2
        else:
            knP = 3
        knockOutPnts.append(knP)
    return knockOutPnts

""" Change in position points """
def changePositionPoints(qualifyingPosition,racePosition):
    """ +/-2 pnts per position change, max +/-10 """
    chngPosPnts = []
    for cPP in 2*np.array(qualifyingPosition-racePosition):
        if(cPP<0):   chngPosPnts.append(np.max([cPP,-10]))
        elif(cPP>=0):chngPosPnts.append(np.min([cPP, 10]))
    return chngPosPnts

""" Points for beating teammate in race """
def beatTeammateRace(driverTeamList,racePosition):
    """ 3 points for beating teammate in race """
    teamMateRcePoints = []
    for dI,dT,rP in zip(range(len(driverTeamList)),driverTeamList,racePosition):
        teamMates = np.where(driverTeamList==dT)[0]
        teamMate  = np.delete(teamMates,np.where(teamMates==dI)[0])[0]
        teamMtPos = racePos[teamMate]
        if(rP<teamMtPos):
            teamMateRcePoints.append(3)
        else:
            teamMateRcePoints.append(0)
    return teamMateRcePoints

""" Points for beating teammate in qualifying """
def beatTeammateQuali(driverTeamList,qualifyingPosition):
    """ 2 points for beating teammate in quali """
    teamMateQualiPoints = []
    for dI,dT,qP in zip(range(len(driverTeamList)),driverTeamList,qualifyingPosition):
        teamMates = np.where(driverTeamList==dT)[0]
        teamMate  = np.delete(teamMates,np.where(teamMates==dI)[0])[0]
        teamMtPos = qualiPos[teamMate]
        if(qP<teamMtPos):
            teamMateQualiPoints.append(2)
        else:
            teamMateQualiPoints.append(0)
    return teamMateQualiPoints

""" Calulate Total Points """
def calcTotPoints(qualiPos,knockOutPnts,teamMateQualiPoints,racePos,chngPosPnts,teamMateRcePoints):
    """ Total driver points """
    driverPointsList = qualiPoints[qualiPos-1] + knockOutPnts + teamMateQualiPoints + pFinish*(racePoints[racePos-1] + chngPosPnts + teamMateRcePoints + 1) + pDNF*(-10.)
    return driverPointsList

""" Printing Stuff """
def printDriverInfo(driverPoints,driverList,racePos,driverCosts):
    """ Order driver in points """
    sortedPoints, sortedDrivers, sortedRacePos, sortedCost = zip(*sorted(zip(driverPoints,driverList,racePos,driverCosts)))
    sortedPoints, sortedDrivers, sortedRacePos, sortedCost = np.array(sortedPoints)[::-1], np.array(sortedDrivers)[::-1], np.array(sortedRacePos)[::-1], np.array(sortedCost)[::-1]
    print "DRVR, POS, PNTS"
    for sD,sP,sRP,sC in zip(sortedDrivers,sortedPoints,sortedRacePos,sortedCost):
        if(sC<=20):
            print "%s*, %i,   %i"%(sD,sRP,sP)
        else:
            print "%s,  %i,   %i"%(sD,sRP,sP)
    """ Order driver in value """
    driverValue = driverPoints/driverCosts
    sortedValue, sortedDrivers = zip(*sorted(zip(driverValue,driverList)))
    sortedValue, sortedDrivers = np.array(sortedValue)[::-1], np.array(sortedDrivers)[::-1]
    print "\n##########"
    print "DRV, PNTS/$"
    for sD,sV in zip(sortedDrivers,sortedValue):
        print "%s, %.3f"%(sD,sV)
    return

""" Single Race """
if(1):
    qualiPos            = prevQualis[-1]#prdQualiPos
    racePos             = prevRaces[-1]#prdRacePos
    knockOutPnts        = knockOutSessionPoints(qualiPos)
    chngPosPnts         = changePositionPoints(qualiPos,racePos)
    teamMateRcePoints   = beatTeammateRace(driverTeam,racePos)
    teamMateQualiPoints = beatTeammateQuali(driverTeam,qualiPos)
    driverPoints        = calcTotPoints(qualiPos,knockOutPnts,teamMateQualiPoints,racePos,chngPosPnts,teamMateRcePoints)
    printDriverInfo(driverPoints,driverList,racePos,driverCosts)

    comboPoints = []
    comboNames  = []

    maxPoints    = 0.
    indexRange   = np.arange(len(driverList))
    iterationInd = 0
    for team in teamsList:
        for i1,d1,c1,p1,t1 in zip(indexRange,driverList,driverCosts,driverPoints,driverTeam):
            for i2,d2,c2,p2,t2 in zip(indexRange[i1+1:],driverList[i1+1:],driverCosts[i1+1:],driverPoints[i1+1:],driverTeam[i1+1:]):
                for i3,d3,c3,p3,t3 in zip(indexRange[i2+1:],driverList[i2+1:],driverCosts[i2+1:],driverPoints[i2+1:],driverTeam[i2+1:]):
                    for i4,d4,c4,p4,t4 in zip(indexRange[i3+1:],driverList[i3+1:],driverCosts[i3+1:],driverPoints[i3+1:],driverTeam[i3+1:]):
                        for i5,d5,c5,p5,t5 in zip(indexRange[i4+1:],driverList[i4+1:],driverCosts[i4+1:],driverPoints[i4+1:],driverTeam[i4+1:]):
                            if(iterationInd%15500==0): print "%i%%"%(100.*iterationInd/155000.)
                            iterationInd += 1
                            totalCost = c1+c2+c3+c4+c5+teamCostsDict[team]
                            if(totalCost>currentBudget):continue
                            teamPoints   = np.sum(driverPoints[np.where(driverTeam==team)])-3-2
                            lineUpCosts  = np.array([c1,c2,c3,c4,c5])
                            driverLineUp = np.array([d1,d2,d3,d4,d5])
                            lineUpPoints = np.array([p1,p2,p3,p4,p5])
                            turboPoint   = np.max(lineUpPoints[lineUpCosts<=20.])
                            """ Points reduction for switching """
                            if(0):
                                if(team in currentTeam):
                                    numDiff = 0
                                else:
                                    numDiff = 1
                                for dLU in driverLineUp:
                                    if(dLU not in currentTeam):
                                        numDiff += 1
                            else:
                                numDiff = 0
                            switchCost   = np.min([0,-10.*(numDiff-3)])
                            totPoints    = np.sum(lineUpPoints)+teamPoints+turboPoint+switchCost
                            if(totPoints>200.):
                                comboPoints.append(totPoints)
                                comboNames.append(team+" "+d1+" "+d2+" "+d3+" "+d4+" "+d5+" "+str(totalCost))
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
if(1):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    comboPoints    = np.array(comboPoints)
    comboNames     = np.array(comboNames)
    for pT in np.arange(200,300,5):
        numAbove = np.sum((comboPoints>pT))
        if(numAbove<=40):
            pointsThreshold = pT
            break
    topComboPoints = comboPoints[(comboPoints>pointsThreshold)]
    topComboNames  = comboNames[(comboPoints>pointsThreshold)]
    topComboPoints, topComboNames = zip(*sorted(zip(topComboPoints, topComboNames)))
    for cP,cN in zip(topComboPoints[::-1],topComboNames[::-1]):
        print cP,cN
    mpl.rcParams['font.size']=18
    plt.figure(1,figsize=(16,9))
    plt.plot(topComboNames[::-1],topComboPoints[::-1],marker="x",linestyle="--",mew=4,ms=10,color="tab:red")
    plt.ylabel("Combination Points")
    plt.xticks(rotation='vertical',fontsize=14)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("comboPoints.png")
    plt.show()
sys.exit()

""" Monte Carlo Loop """
if(0):
    comboPoints = np.zeros(92892)#21346) # NB these numbers will need changing if the threshold values are changed
    comboNames  = [[] for i in range(92892)]#21346)]
    nmbrRndInt  = 50
    totalDriverPoints = np.array([np.array([0 for x in range(20)]) for y in range(nmbrRndInt)])
    # np.random.seed(0)
    for randomIndex in range(nmbrRndInt):
        print "Iteration Index %i: %i%% complete"%(randomIndex,100.*(float(randomIndex)/float(nmbrRndInt)))

        """ Random """
        # qualiPos            = positionVariation(prdQualiPos,raceStdDev,driverList)
        racePos             = positionVariation(prdRacePos,raceStdDev,driverList)
        """ Predicted """
        qualiPos            = prdQualiPos
        # racePos             = prdRacePos
        knockOutPnts        = knockOutSessionPoints(qualiPos)
        chngPosPnts         = changePositionPoints(qualiPos,racePos)
        teamMateRcePoints   = beatTeammateRace(driverTeam,racePos)
        teamMateQualiPoints = beatTeammateQuali(driverTeam,qualiPos)
        driverPoints        = calcTotPoints(qualiPos,knockOutPnts,teamMateQualiPoints,racePos,chngPosPnts,teamMateRcePoints)
        totalDriverPoints[randomIndex,:] = driverPoints[:]
        # continue
        # printDriverInfo(driverPoints,driverList,racePos,driverCosts)

        maxPoints    = 0.
        indexRange   = np.arange(len(driverList))
        iterationInd = 0
        numUnderCost = 0
        # print "\n##########"
        for team in teamsList:
            for i1,d1,c1,p1,t1 in zip(indexRange,driverList,driverCosts,driverPoints,driverTeam):
                for i2,d2,c2,p2,t2 in zip(indexRange[i1+1:],driverList[i1+1:],driverCosts[i1+1:],driverPoints[i1+1:],driverTeam[i1+1:]):
                    for i3,d3,c3,p3,t3 in zip(indexRange[i2+1:],driverList[i2+1:],driverCosts[i2+1:],driverPoints[i2+1:],driverTeam[i2+1:]):
                        for i4,d4,c4,p4,t4 in zip(indexRange[i3+1:],driverList[i3+1:],driverCosts[i3+1:],driverPoints[i3+1:],driverTeam[i3+1:]):
                            for i5,d5,c5,p5,t5 in zip(indexRange[i4+1:],driverList[i4+1:],driverCosts[i4+1:],driverPoints[i4+1:],driverTeam[i4+1:]):
                                # if(iterationInd%15500==0): print "%i%%"%(100.*iterationInd/155000.)
                                iterationInd += 1
                                totalCost = c1+c2+c3+c4+c5+teamCostsDict[team]
                                if(totalCost>currentBudget or totalCost<lwrBdgtLimit):continue
                                teamPoints   = np.sum(driverPoints[np.where(driverTeam==team)])-3-2
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
                                comboPoints[numUnderCost] += totPoints
                                if(randomIndex==0):
                                    comboNames[numUnderCost] = team+" "+d1+" "+d2+" "+d3+" "+d4+" "+d5
                                if totPoints>maxPoints:
                                    bestDrivers = driverLineUp
                                    bestTeam    = team
                                    turboDrive  = driverLineUp[np.argmax(lineUpPoints*(lineUpCosts<=20.))]
                                    maxPoints   = totPoints
                                    bestCost    = totalCost
                                numUnderCost += 1

    # import matplotlib.pyplot as plt
    # print totalDriverPoints
    # driverPointsMean = np.mean(totalDriverPoints,axis=0)#/driverCosts
    # driverPointsStd  = np.std(totalDriverPoints,axis=0)#/driverCosts
    # driverPointsMean, driverNames, driverPointsStd = zip(*sorted(zip(driverPointsMean, driverList, driverPointsStd)))
    # plt.errorbar(driverNames,driverPointsMean,yerr=driverPointsStd,linestyle="",marker="x",ms=10,mew=4)
    # # plt.xticks(rotation='vertical')
    # plt.show()
    # print stdDev
    # print mean
    # sys.exit()
    # print numUnderCost,iterationInd
    # # sys.exit()
    if(1):
        import matplotlib.pyplot as plt
        comboPoints    = np.array(comboPoints)/nmbrRndInt
        comboNames     = np.array(comboNames)
        for pT in np.arange(200,300,5):
            numAbove = np.sum((comboPoints>pT))
            if(numAbove<=40):
                pointsThreshold = pT
                break
        topComboPoints = comboPoints[(comboPoints>pointsThreshold)]
        topComboNames  = comboNames[(comboPoints>pointsThreshold)]
        topComboPoints, topComboNames = zip(*sorted(zip(topComboPoints, topComboNames)))
        for cP,cN in zip(topComboPoints[::-1],topComboNames[::-1]):
            print cP,cN
        plt.figure(1,figsize=(16,9))
        plt.plot(topComboNames[::-1],topComboPoints[::-1])
        plt.ylabel("Mean Points")
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        plt.show()
