import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
import policy_schemes as common
#import statistics

pid = os.getpid()
# print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent]"
# print "\t schemes. 1: random location; 2: same location; 3: good and bad"
x = []
times = 1
qoe_overall = []
n_scheme = 6
n_user = 10

times = int(sys.argv[1])
for i in [0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]:
	x.append(i)
	tt = 0

	qoe = [[0 for z in range(5)] for x_ in range(n_scheme)]
	for j in range(times):
		os.system("python policy_different_join_time.py 1 10 %f 90 0 %d.trace"%(i, pid))
		ls = open("%d.trace"%(pid)).readlines()
		#os.system("rm %d.trace"%(pid))
		
		xx = -1
		for ii in range(n_scheme):
			admission = 0
			for jj in range(5):
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
		for jj in range(1, 5):
			qoe[ii][jj] = qoe[ii][jj]*1.0/qoe[ii][0]
	qoe_overall.append(qoe)

fig = plt.figure(figsize=(16,12))
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)
ax = [ax1, ax2, ax3, ax4]
ylabel = ["Average Bitrate", "Rebuffer", "Qoe: # of Switches", "Rate selection: # of switches"]
for i in range(4):
	for s in range(n_scheme):
		y = []
		y_min = []
		y_max = []
		for j in range(len(qoe_overall)):
			#y.append(np.mean(qoe_overall[j][s][i]))
			#print qoe_overall[j][s][3]
			y.append(qoe_overall[j][s][i + 1])
			#y_min.append(np.median(qoe_overall[j][s][i]) - min(qoe_overall[j][s][i]))
			#y_max.append(-np.median(qoe_overall[j][s][i]) + max(qoe_overall[j][s][i]))
		#ax[i].errorbar(x, y, yerr=[y_min, y_max])
		ax[i].plot(x, y, "-x")
	ax[i].set_xlabel("Premium Resources (1)")
	ax[i].set_ylabel(ylabel[i])
	if i == 0:
		ax[i].legend(["sqm", "sqm2", "sqm3", "paris", "paris2", "now"], 1, ncol=3)
	ax[i].grid()
plt.tight_layout()
plt.savefig("vary_premium_resource.png")

fout = open("vary_premium_resource.txt", "w")
fout.write(str(qoe_overall) + "\n")
fout.close()