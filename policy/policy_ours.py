import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
#import statistics
from policy_schemes import *

pid = os.getpid()

#signal range's default is 37%
#print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent] [signal range]"
print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [duration]"
print "\t schemes. 1: random location; 2: same location; 3: good and bad"

scheme = int(sys.argv[1])
n = int(sys.argv[2])
percentage = float(sys.argv[3])
normal_n = int(sys.argv[4])
time = int(sys.argv[5])

random.seed(0)
result_sqm = []
result_sqm2 = []
result_sqm3 = []
result_paris = []
result_now = []
bpp = {}
bpp_legend = []
randomness = 0.05
filename = ""

join_time = []

def get_same_location():
	global bpp_legend, filename
	filename = "same_signal"
	bpp_legend = []
	x = random.randint(bpp_min, bpp_max)
	for i in range(n):
		bpp[i] = x
		bpp_legend.append(str(bpp[i]))

def get_random_location():
	global bpp_legend, filename
	filename = "random_location"
	bpp_legend = []
	for i in range(n):
		bpp[i] = random.randint(bpp_min, bpp_max)
		bpp_legend.append(str(bpp[i]))

def get_two_types_users():
	global bpp_legend, filename
	filename = "good_bad_users"
	bpp_legend = []
	for i in range(n):
		if i % 2 == 0:
			bpp[i] = random.randint(int(bpp_max*0.9), bpp_max)
		else:
			bpp[i] = random.randint(bpp_min, int(bpp_min*1.1))
		bpp_legend.append(str(bpp[i]))
		
#generate join time

last = 0
for i in range(n):
	#join_time.append(last + random.randint(0, 10))
	join_time.append(0)
	last = join_time[-1]

#print join_time
if scheme == 1:
	get_random_location()
elif scheme == 2:
	get_same_location()
else:
	get_two_types_users()
u_sqm = [] # this is total utility
u_sqm2 = []
u_sqm3 = []
u_paris = []
u_now = []
u_a_sqm = [] # this is average utility
u_a_sqm2 = []
u_a_sqm3 = []
u_a_paris = []
u_a_now = []
last_r = []
last_r2 = []
last_r3 = []
admitted_sqm = [0] * n
admitted_sqm2 = [0] * n
admitted_sqm3 = [0] * n
admitted_paris = [0] * n
admitted_now = [0] * n
current_user = 0
new_user = 0
signal = [[] for i in range(n)]

scheme_label = ["sqm1", "sqm_minimum_support", "sqm_fairness", "paris", "now"]
for i in range(time):
	for j in range(n):
		if join_time[j] == i:
			new_user += 1
	for j in range(n):
		bpp[j] = bpp[j]*(1 + 2*(random.random() - 0.5)*randomness)
		signal[j].append(bpp[j])
	r1, r2, r3 = sqm(bpp, admitted_sqm, new_user, current_user, last_r, 1)
	u_sqm.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm.append(sum(r2)*1.0/count_admitted_user(admitted_sqm) if count_admitted_user(admitted_sqm) else 0 )
	result_sqm.append([r1, r2])
	last_r = copy.deepcopy(r3)
	
	r1, r2, r3 = sqm_minimum_support(bpp, admitted_sqm2, new_user, current_user, last_r2, 1, 0)
	u_sqm2.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm2.append(sum(r2)*1.0/count_admitted_user(admitted_sqm2) if count_admitted_user(admitted_sqm2) else 0 )
	result_sqm2.append([r1, r2])
	last_r2 = copy.deepcopy(r3)
	
	r1, r2, r3 = sqm_minimum_support(bpp, admitted_sqm3, new_user, current_user, last_r2, 1, 1)
	u_sqm3.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm3.append(sum(r2)*1.0/count_admitted_user(admitted_sqm3) if count_admitted_user(admitted_sqm3) else 0 )
	result_sqm3.append([r1, r2])
	last_r3 = copy.deepcopy(r3)
	
	r = paris(bpp, admitted_paris, new_user, current_user)
	u_paris.append(sum(r[1])*1.0)#/count_admitted_user(admitted_paris))
	u_a_paris.append(sum(r[1])*1.0/count_admitted_user(admitted_paris) if count_admitted_user(admitted_paris) else 0)
	result_paris.append(r)
	
	r = now(bpp, admitted_now, new_user, current_user)
	u_now.append(sum(r[1])*1.0)#/count_admitted_user(admitted_now))
	u_a_now.append(sum(r[1])*1.0/count_admitted_user(admitted_now) if count_admitted_user(admitted_now) else 0)
	result_now.append(r)
	current_user += new_user
	new_user = 0
	
	
def generate_file(f, r, j):
	randomness = 0 #.05
	fo = open(f, "w")
	for i in range(len(r)):
		random_ = 2*(random.random() - 0.5)*randomness
		fo.write(str(i*1000) + " " + str(max(1, r[i][1][j]*(1+random_))) + "\n")

results = [result_sqm, result_sqm2, result_sqm3, result_paris, result_now]
#axes = [(ax, ax2), (bx, bx2), (cx, cx2), (dx, dx2), (ex, ex2)]
#axesu = [axu, bxu, cxu, dxu, exu]
#results_u = [u_sqm, u_sqm2, u_sqm3, u_paris, u_now]
#max_u = max(max(u_sqm), max(u_paris), max(u_now), max(u_sqm2), max(u_sqm3))

#qoe_total = [0] * len(results)
#qoe_avg = [0] * len(results)
ad = [admitted_sqm, admitted_sqm2, admitted_sqm3, admitted_paris, admitted_now]


for i in range(len(results)):
	fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(8,6*n))
	r = results[i]
	for j in range(n):
		ax = axes[j]
		ax2 = ax.twinx()
		generate_file("temp_trace_%d"%(pid), r, j)
		o = commands.getstatusoutput("python ABRSim/simulation.py temp_trace_%d"%(pid))
		#print o
		
		
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

		g = re.match("QoE: (.*) avg. bitrate: (.*) buf. ratio: (.*) numSwtiches: (.*) dominant BR: (.*) played (.*) out of (.*)", o[1])
		#metric = 2
		if g != None:
			ab = float(g.group(2))
			bu = float(g.group(3))
			sw = float(g.group(4))
		text = "admitted: " + ("Yes" if ad[i][j] == 1 else "No") + "\navg bitrate: " + str(ab) + "\nrebuffer: " + str(bu) + "\nswitches: " + str(sw)
		ax.text(0.01, 1.03, text, transform=ax.transAxes, verticalalignment='top', fontsize=14, bbox=props)
	#qoe_avg[i] = qoe_total[i]*1.0/count_admitted_user(ad[i]) if count_admitted_user(ad[i]) else 0
	#os.system("rm temp_trace_%d"%(pid))
	
		x = []
		y1 = []
		y2 = []
		for k in range(len(results[i])):
			x.append(k)
			y1.append(results[i][k][0][j]) # prb
			#y1.append(results[i][k][1][j]) # rate
			y2.append(br_with_zero.index(results[i][k][1][j]) if results[i][k][1][j] in br_with_zero else 0) # quality level
		#print bpp[j], len(bpp[j])
		ax.plot(x, y2)
		ax2.plot(x, y1, ":k")
		ax.set_ylim([-1, len(br_with_zero)*1.3])	
		ax2.set_ylabel("Rate (Kbits/s)")
		ax.set_ylabel("Rate (Quality level)")
		ax.set_xlabel("Time (s)")
	plt.savefig("policy_%s_%s_np%d_nt%d_p%.2f_lock%.2f.png"%(scheme_label[i], filename, n, normal_n, percentage, lock_parameter))
	plt.tight_layout()
	plt.close()