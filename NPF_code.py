# This source code is licensed under the Affero General Public License (AGPL) for non-commercial use.
# For commercial use, please contact us for more information and to discuss licensing options.
# In this case, if there are any conflicting provisions between the individual agreement and AGPL,
# the former shall prevail.

import random, copy

# Input
N_label=["A","B","C","D","E","F"]
N=list(range(len(N_label)))     # A set of entities, N={0,...,n-1} 
x=[{0:1.0},{1:1.0},{2:1.0},{0:0.5,1:0.5},{0:0.1,2:0.45,3:0.45},{2:0.4,4:0.6}]  # a matrix of voting rights, x_{j,i} in [0,1], j:subsidiary, i:shareholder
v=[1,1,1,1,1,1]                 # a vector of values, v_j in R
T, q_j, d = 20000, 0.5, 1.0     # # of iterations, T in Z, a vector of quotas, q_j in [1/2,1], a damping factor, d in (0,1]
init_prob, burn_in=0.02, 15     # Initialization probability, Initial iteration threshold

NPI, NPF=len(N)*[0], len(N)*[0]
total_step=0
for t in range(T):
    if t==0 or random.random()<init_prob: # Initialize the labels for direct and indirect control (to break loops)
        t_initialize=t
        L_D,L_I=copy.deepcopy(N),copy.deepcopy(N)   
    else:
        for j in N:
            U_j={}
            N_j=[]
            for i in x[j]:
                if L_I[i] not in U_j:
                    U_j[L_I[i]]=random.random()                 # Create unions of i
                N_j.append([i,U_j[L_I[i]],random.random()])     # Save i whthin each union
            N_j=sorted(N_j, key=lambda x:(x[1], x[2]))          # After shuffling unions, shuffle i within each union
            x_j=0                               # Initialize the sum of voting shares
            for i,Random_1,Random_2 in N_j:
                x_j=x_j+x[j][i]
                if x_j>q_j:                     # Find a pivot and indirect owner
                    L_D[j]=i                    # Save the directed edges of a control network
                    L_I[j]=L_I[i]               # Sequential flow from upstream nodes
                    break
    if t-t_initialize>=burn_in:                 # Discard the “propagation” results from early iterations
        p=copy.deepcopy(v)
        p_next=len(N)*[0]
        for tau in range(50):                   # Calculte the downstream values
            for j in N:
                i=L_D[j]
                if j!=i:
                    p_next[i]=p_next[i]+d*p[j]
            p_next=[p_next[j]+v[j] for j in N]
            p=copy.deepcopy(p_next)
            p_next=len(N)*[0]
        total_step+=1
        for j in N:
            NPI[L_I[j]]+=v[j]
            NPF[j]+=p[j]
NPI,NPF=[n/total_step for n in NPI],[n/total_step for n in NPF]     # Calculate NPIs

rho = sum(v)/sum(NPF[j] for j in N if (j in x[j] and x[j][j]==1.0)) # an inflation factor, rho in (0,1]
NPF=[n*rho for n in NPF]                                            # Calculate NPFs
print("NPI=",NPI,"NPF=",NPF)



