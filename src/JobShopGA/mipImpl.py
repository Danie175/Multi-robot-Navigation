# -*- coding: utf-8 -*-

from itertools import product
from mip import *
import matplotlib.pyplot as plt

try:
    model = Model('Lineless', solver_name="CBC")
    # model = Model('Lineless') # Gurobi
    
    # # Processing time
    # P_j = [[1, 3, 6, 7, 3, 6],
    #         [8, 5, 10, 10, 10, 4],
    #         [5, 4, 8, 9, 1, 7],
    #         [5, 5, 5, 3, 8, 9],
    #         [9, 3, 5, 4, 3, 1],
    #         [3, 3, 9, 10, 4, 1]]
    
    # # Machine ID of above operations
    # O_j = [[2, 0, 1, 3, 5, 4],
    #         [1, 2, 4, 5, 0, 3],
    #         [2, 3, 5, 0, 1, 4],
    #         [1, 0, 2, 3, 4, 5],
    #         [2, 1, 4, 5, 0, 3],
    #         [1, 3, 5, 0, 4, 2]]
    
    P_j = [[10, 8, 4],
            [8, 3, 5, 6],
            [4, 7, 3]]
    
    O_j = [[0, 1, 2],
            [1, 0, 3, 2],
            [0, 1, 3]]
    
    nJobs = len(P_j)
    print ("Number of Job = {0}".format(nJobs))
    
    mMachines = 6 #len(O_j[0])
    print ("Number of Machines = {0}".format(mMachines))
    
    # Large Positive Number
    H = 1000000
    
    MachineList = range(0, mMachines, 1)
    JobList = range (0, nJobs, 1)
    
    # »»»»»»»»»»»»»»»»»»»»»» set N «««««««««««««««««««««««
    #  N: Consists of all possible combination if operation/machine and job
    # print ("set N")
    N = {}
    tmpNCount = 0
    for jj in JobList:
        tmpCount = len(O_j[jj])
        for ii in range (tmpCount):
            # print ("({}, {})".format (O_j[jj][ii], jj))
            
            tmpNValue = []
            tmpNValue.append(O_j[jj][ii])
            tmpNValue.append(jj)
            N [tmpNCount] = tmpNValue
            tmpNCount += 1
    
    
    # »»»»»»»»»»»»»»»»»»»»»» set A «««««««««««««««««««««««
    # A: Consist of routing information of job j
    # Job perspective
    # print ("set A")
    A = {}
    tmpACount = 0
    for jj in JobList:
        tmpCount = len(O_j[jj])
        for ii in range (tmpCount-1):
            # print ("({}, {}) -> ({}, {})".format (O_j[jj][ii], jj, O_j[jj][ii+1], jj))
            
            tmpAValue = []
            tmpAValue.append(O_j[jj][ii])
            tmpAValue.append(jj)
            tmpAValue.append(O_j[jj][ii+1])
            tmpAValue.append(jj)
            A [tmpACount] = tmpAValue
            tmpACount += 1
    
    
    # »»»»»»»»»»»»»»»»»»»»»» set B «««««««««««««««««««««««
    # B: Consist of all possible Disjunctive Constraints
    # print ("set B")
    B = {}
    tmpBCount = 0
    for ii in MachineList:
        tmpB = {}
        tmpBCnt = 0
        for jj in JobList:
            tmpBList = []
            oo = O_j[jj]
            # print ("({}, {}, {})".format (ii, jj, oo))
            if ii in oo:
                # print ("({}, {})".format (ii, jj))
                tmpBList.append(ii)
                tmpBList.append(jj)
                tmpB[tmpBCnt] = tmpBList
                tmpBCnt += 1
        
        tmpBItemCnt = len (tmpB)
        for ky1 in range (tmpBItemCnt-1):
            val1 = tmpB [ky1]
            # print ("{} -> {}".format (ky1, val1))
            for ky2 in range (ky1+1, tmpBItemCnt, 1):
                val2 = tmpB [ky2]
                # print ("{} -> {}".format (val1, val2))
                
                tmpBValue = []
                tmpBValue.append(val1[0])
                tmpBValue.append(val1[1])
                tmpBValue.append(val2[0])
                tmpBValue.append(val2[1])
                
                B [tmpBCount] = tmpBValue
                tmpBCount += 1
    
    
    # »»»»»»»»»»»»»»»»»»»» PARAMETERS ««««««««««««««««««««
    # Makespan
    C_max = model.add_var(name="C_max")
    
    # Start time S_ij of job j on machine i
    S = [[model.add_var(name='S({},{})'.format(i, j)) for j in range(nJobs)] for i in range(mMachines)]
    
    # »»»»»»»»»» DECISION VARIABLES - x_ijk ««««««««««
    # x_ijk = 1 if job j precedes job k on machine i; otherwise 0
    x = [[[model.add_var(var_type=BINARY, name='x({},{},{})'.format(j, k, i))
                   for k in range(nJobs)] 
                      for j in range(nJobs)] 
                         for i in range(mMachines)]
    
    
    # CONSTRAINT 2: Ensure that processing is done as per the routing for each job
    for val in A.values():
        i1 = val[0]    # i as per book
        jj = val[1]    # j as per book
        i1Indx = O_j[jj].index (i1)
        i2 = val[2]    # k as per book
        # print ("({}, {}) -> {} -> {}".format (i1, jj, i1Indx, P_j[jj][i1Indx]))
        model += S[i2][jj] - S[i1][jj] >= P_j[jj][i1Indx]
        
    
    # CONSTRAINT 3: Ensure the computation of Cmax
    for val in N.values():
        ii = val[0]
        jj = val[1]
        iIndx = O_j[jj].index (ii)
        # print ("({}, {}) -> {}".format (jj, ii, P_j[jj][iIndx]))
        model += C_max - S[ii][jj] >= P_j[jj][iIndx]
    
    
    # CONSTRAINT 4: Ensures no to operation start at the same time on a machine
    constraintCnt = 0
    for val in B.values():
        ii = val[0]    # I as per book
        j1 = val[1]    # J as per book
        iIndx = O_j[j1].index (ii)
        j2 = val[3]    # L as per book
        model += H * (1 - x[ii][j2][j1]) + S[ii][j1] - S[ii][j2] >= P_j[j2][iIndx]
    
    
    # CONSTRAINT 5: Ensures no to operation start at the same time
    for val in B.values():
        ii = val[0]    # I as per book
        j1 = val[1]    # J as per book
        iIndx = O_j[j1].index (ii)
        j2 = val[3]    # L as per book
        model += H * x[ii][j2][j1] + S[ii][j2] - S[ii][j1] >= P_j[j1][iIndx]
    
    
    # CONSTRAINT 6: Ensures Precedence Constraints of jobs on same machine
    for val in B.values():
        ii = val[0]    # I as per book
        j1 = val[1]    # J as per book
        j2 = val[3]    # L as per book
        model += x[ii][j1][j2] + x[ii][j2][j1] <= 1
    
    
    # CONSTRAINT 7: Ensures starting time is greater than zero
    for val in N.values():
        ii = val[0]
        jj = val[1]
        iIndx = O_j[jj].index (ii)
        model += S[ii][jj] >= 0
    
    
    # CONSTRAINT 8: Ensures only those precedence sequence are enabled in either direction
    model.add_constr (xsum(x[val[0]][val[1]][val[3]] + x[val[0]][val[3]][val[1]] for val in B.values()) == len(B))

    model.objective = C_max
    
    model.write ("model_MIP.lp")
    
    print ("before optimize ...")
    status = model.optimize()
    print ("after optimize ...")
    
    model.write ("model_MIP.sol")
    
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        Cmax = C_max.x
        print("Makespan: ", Cmax)
        print ("++++++++++++++++++++++==========+++++++++++++++")
        
        # Figure and set of subplots
        fig, ax = plt.subplots()
        fig.set_figheight(12)
        fig.set_figwidth(18)
        ax.set_ylabel('Machine', fontweight ='bold', loc='top', color='magenta', fontsize=16)
        ax.set_ylim(-0.5, mMachines-0.5)
        ax.set_yticks(range(mMachines), minor=False)
        ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
        
        ax.set_xlabel('Time', fontweight ='bold', loc='right', color='red', fontsize=16)
        ax.set_xlim(0, Cmax+2)
        
        ax.tick_params(axis='x', labelcolor='red', labelsize=16)
        
        ax.grid(True)
        
        tmpTitle = 'Job Shop Scheduling (m={0}; n={1}; Utilization={2})'.format(mMachines, nJobs, Cmax)
        plt.title(tmpTitle, size=24, color='blue')
        
        colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta']
        
        for val in N.values():
            ii = val[0]
            jj = val[1]
            iIndx = O_j[jj].index (ii)
            
            ST = S[ii][jj].x
            Pj = P_j[jj][iIndx]
            CT = ST + Pj
                
            cIndx = 0
            cIndx = jj % len(colors)
            ax.broken_barh([(ST, Pj)], (-0.3+ii, 0.6), facecolor=colors[cIndx], linewidth=1, edgecolor='black')
            ax.text((ST + (Pj/2-0.3)), (ii+0.03), '{}'.format(jj), fontsize=18)
            
    else:
        print("Optimization was stopped!!!")
        
except AttributeError:
    print('Encountered an attribute error') 