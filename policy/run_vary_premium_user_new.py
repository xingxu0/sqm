import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
import policy_schemes as common
#import statistics

#stair = int(sys.argv[1])

# print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent]"
# print "\t schemes. 1: random location; 2: same location; 3: good and bad"
pid = os.getpid()
x = []
times = 10
qoe_overall = []
n_scheme = 7

times = int(sys.argv[1])
adm = int(sys.argv[2])
for i in range(5, 21, 3):
	x.append(i)
	tt = 0
	print "!!!", i
	
	n_user = i
	qoe = [[0 for z in range(6)] for x_ in range(n_scheme)]
	for j in range(times):
		#os.system("python policy_output.py 1 %d 0.10 90 1 %d.trace"%(i, pid))
		os.system("python policy_different_join_time.py 1 %d 0.10 90 0 %d.trace %d"%(i, pid, adm))
		ls = open("%d.trace"%(pid)).readlines()
		os.system("rm %d.trace"%(pid))
		
		xx = -1
		for ii in range(n_scheme):
			admission = 0
			for jj in range(6):
				xx += 1
				t_ = ls[xx].split(" ")
				if jj == 0:
					admission = t_
				for kk in range(n_user):
					#print ii, jj, kk, t_
					#qoe[ii][jj][kk] += float(t_[kk])
					if admission == 0 or int(admission[kk]) >= 1:
						qoe[ii][jj] += float(t_[kk])
	for ii in range(n_scheme):
		for jj in range(1, 6):
			qoe[ii][jj] = (qoe[ii][jj]*1.0/qoe[ii][0] if qoe[ii][0] else 0)
			if not qoe[ii][0]:
				print "0 user issue", pid
	qoe_overall.append(qoe)
		
fig = plt.figure(figsize=(24,12))
ax1 = fig.add_subplot(231)
ax2 = fig.add_subplot(232)
ax3 = fig.add_subplot(233)
ax4 = fig.add_subplot(234)
ax5 = fig.add_subplot(235)
ax = [ax1, ax2, ax3, ax4, ax5]
ylabel = ["Average Bitrate", "Rebuffer", "Qoe: # of Switches", "Rate selection: # of switches", "Downgrade Fraction"]
for i in range(5):
	for s in range(n_scheme):
		y = []
		y_min = []
		y_max = []
		for j in range(len(qoe_overall)):
			#y.append(np.mean(qoe_overall[j][s][i]))
			#print qoe_overall[j][s][3]
			y.append(qoe_overall[j][s][i+1])
			#y_min.append(np.median(qoe_overall[j][s][i]) - min(qoe_overall[j][s][i]))
			#y_max.append(-np.median(qoe_overall[j][s][i]) + max(qoe_overall[j][s][i]))
		#ax[i].errorbar(x, y, yerr=[y_min, y_max])
		ax[i].plot(x, y, "-x")
	ax[i].set_xlabel("Number of Premium Users")
	ax[i].set_ylabel(ylabel[i])
	if i == 0:
		ax[i].legend(["sqm", "sqm2", "sqm3", "paris", "paris2", "paris3", "now"], 1, ncol=3)
	ax[i].grid()
plt.tight_layout()
plt.savefig("vary_premium_user_%d.png"%(adm))

fout = open("vary_premium_user.txt", "w")
fout.write(str(qoe_overall) + "\n")
fout.close()
