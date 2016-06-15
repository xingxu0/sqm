import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
#import statistics

n = 6
total_n = 30
bpp_min = 82 # bpp is bytes per prb
bpp_max = 292  # this value maps to 712bits/s as TBS
total_prb = 12000
percentage = .3

br = [350, 700, 1200, 2400, 4800]
#br = [350, 700, 1200, 2400]
br_with_zero = [0] + br
label = ["N","R1", "R2", "R3", "R4", "R5"]

print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] "
print "\t schemes. 1: random location; 2: same location; 3: good and bad"

scheme = int(sys.argv[1])
n = int(sys.argv[2])
percentage = float(sys.argv[3])
total_n = int(sys.argv[4]) + n

random.seed(0)
time = 120
result_sqm = []
result_paris = []
result_now = []
bpp = {}
bpp_legend = []
randomness = 0.05
filename = ""

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

def sqm(bpp, last):
	available = total_prb*percentage
	used = 0
	ret_prb = {}
	ret_rate = {}
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1), reverse=True)
	for i in range(len(sorted_bpp)):
		ret_prb[sorted_bpp[i][0]] = 0
		ret_rate[sorted_bpp[i][0]] = 0
		for j in range(len(br) - 1, -1, -1):
			need = br[j]*1000.0/(sorted_bpp[i][1]*8)
			if used + need < available:
				ret_prb[sorted_bpp[i][0]] = need
				ret_rate[sorted_bpp[i][0]] = br[j]
				used += need
				break
	
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	# to lock it a bit to avoid fluctruation
	if False:
		diff = 0
		for i in range(len(last[1])):
			diff += abs(br_with_zero.index(last[1][i]) - br_with_zero.index(ret_rate_[i]))
			if abs(br_with_zero.index(last[1][i]) - br_with_zero.index(ret_rate_[i])) >= len(br_with_zero)/2:
				diff += n
		if diff >= n - 1:
			# check last solution is still feasible or not
			t_prb = 0
			for i in range(len(last[1])):
				t_prb += last[1][i]*1.0/(bpp[i]*8)
			if t_prb <= available and abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_)) <0.1:
				print "using last",diff, last[1], ret_rate_, abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_))
				return last
	return ret_prb_, ret_rate_

def paris(bpp):
	available = total_prb*percentage
	ret_prb = {}
	ret_rate = {}
	for i in range(len(bpp)):
		ret_prb[i] = available/len(bpp)
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		j = 0
		while br[j] <= temp_rate and j < len(br):
			j += 1
		ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	return ret_prb_, ret_rate_

def now(bpp):
	ret_prb = {}
	ret_rate = {}
	for i in range(len(bpp)):
		ret_prb[i] = total_prb/total_n
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		j = 0
		while br[j] <= temp_rate and j < len(br):
			j += 1
		ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	return ret_prb_, ret_rate_

if scheme == 1:
	get_random_location()
elif scheme == 2:
	get_same_location()
else:
	get_two_types_users()
u_sqm = []
u_paris = []
u_now = []
last_r = []
for i in range(time):
	for j in range(n):
		bpp[j] = bpp[j]*(1 + 2*(random.random() - 0.5)*randomness)
	r = sqm(bpp, last_r)
	u_sqm.append(np.mean(r[1]))
	result_sqm.append(r)
	last_r = copy.deepcopy(r)
	
	r = paris(bpp)
	u_paris.append(np.mean(r[1]))
	result_paris.append(r)
	
	r = now(bpp)
	u_now.append(np.mean(r[1]))
	result_now.append(r)

# plotting
fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(231)
bx = fig.add_subplot(232)
cx = fig.add_subplot(233)
axu = fig.add_subplot(234)
bxu = fig.add_subplot(235)
cxu = fig.add_subplot(236)
ax2 = ax.twinx()
bx2 = bx.twinx()
cx2 = cx.twinx()

results = [result_sqm, result_paris, result_now]
axes = [(ax, ax2), (bx, bx2), (cx, cx2)]
axesu = [axu, bxu, cxu]
results_u = [u_sqm, u_paris, u_now]
max_u = max(max(u_sqm), max(u_paris), max(u_now))
for ii in range(len(results)): # for each scheme
	
	rate_count = [0] * (len(br_with_zero) + 1)
	x = []
	for i in range(n): # for each premium user
		x = []
		y1 = []
		y2 = []
		for j in range(len(results[ii])): # for each second
			x.append(j)
			y1.append(results[ii][j][0][i])
			y2.append(br_with_zero.index(results[ii][j][1][i]))
			rate_count[br_with_zero.index(results[ii][j][1][i])] += 1
		axes[ii][1].plot(x, y1, ":", linewidth=2)
		axes[ii][0].plot(x, y2, "-", linewidth=2)
	#axes[ii][1].legend(["PRB"], 1, ncol=6)
	axes[ii][0].legend(bpp_legend, 1, ncol=4)
	axes[ii][0].grid()
	#ax.set_xlim([r_s, r_e])
	#ax.set_ylim([0, 4800])
	#ax[i].legend(le[i],fontsize=legend_font_size)
	#ax[i].set_ylabel("++", fontsize=label_font_size)
	axes[ii][1].set_ylabel("PRB")
	axes[ii][0].set_ylabel("Rate (Quality level)")
	axes[ii][0].set_xlabel("Time (s)")
	text = ""
	for i in range(len(br_with_zero)):
		text = str(label[i]) + ":" + str("%.2f"%(rate_count[i]*1.0/len(results[ii]))) + ", " + text
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	axes[ii][0].text(0.01, 1.03, text, transform=axes[ii][0].transAxes, verticalalignment='top', fontsize=14, bbox=props)
	axes[ii][0].set_ylim([-1, len(br_with_zero)*1.3])
	axesu[ii].plot(x, results_u[ii])
	axesu[ii].set_ylim([0, max_u*1.1])
	axesu[ii].set_ylabel("objective function")
	axesu[ii].set_xlabel("time")
plt.tight_layout()
plt.savefig("policy_%s_np%d_nt%d_p%.2f.png"%(filename, n, total_n, percentage))