import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
#import statistics

# print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent]"
# print "\t schemes. 1: random location; 2: same location; 3: good and bad"
x = []
y_total = [[], [], [], [], []]
y_avg = [[], [], [], [], []]
times = 10
for i in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]:
	x.append(i)
	tt = 0
	t_total = [0] * len(y_total)
	t_avg = [0] * len(y_total)
	for j in range(times):
		os.system("python policy_dynamic.py 1 10 0.10 90 %d %f"%(1 if j>0 else 0, i))
		ls = open("temp").readlines()
		
		t = ls[0].split(" ")
		for ii in range(len(t)):
			t_total[ii] += float(t[ii])
		
		t = ls[1].split(" ")
		for ii in range(len(t)):
			t_avg[ii] += float(t[ii])
	for ii in range(len(t_total)):
		y_total[ii].append(t_total[ii]*1.0/times)
		y_avg[ii].append(t_avg[ii]*1.0/times)

fig = plt.figure(figsize=(16,6))
ax = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
max_u1 = 0
max_u2 = 0
for i in range(len(y_total)):
	ax.plot(x, y_total[i], "-x")
	ax2.plot(x, y_avg[i], "--o")
	max_u1 = max(max_u1, max(y_total[i]))
	max_u2 = max(max_u2, max(y_avg[i]))
ax.set_ylim([0, max_u1*1.4])
ax2.set_ylim([0, max_u2*1.4])
ax.legend(["sqm", "sqm2", "sqm3", "paris", "now"], 1, ncol=3)
ax2.legend(["sqm (avg)", "sqm2 (avg)", "sqm3 (avg)", "paris (avg)", "now (avg)"], 1, ncol=3)
ax.grid()
ax.set_ylabel("Total Objective Function")
ax2.set_ylabel("Average Objective Function")
ax2.set_xlabel("Signal range (1)")
ax.set_xlabel("Signal range (1)")
plt.tight_layout()
plt.savefig("vary_signal_range.png")