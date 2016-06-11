import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands
import numpy as np

n = 6
bpp_min = 20 # bpp is bytes per prb
bpp_max = 250
total_prb = 12000
percentage = .3

br = [350, 700, 1200, 2400, 4800]
br = [350, 700, 1200, 2400]
label = ["N","R1", "R2", "R3", "R4"]

random.seed(0)		
time = 120
result_sqm = []
result_paris = []
bpp = {}
bpp_legend = []
randomness = 0.05

def get_same_location():
	global bpp_legend
	bpp_legend = []
	x = random.randint(bpp_min, bpp_max)
	for i in range(n):
		bpp[i] = x
		bpp_legend.append(str(bpp[i]))

def get_random_location():
	global bpp_legend
	bpp_legend = []
	for i in range(n):
		bpp[i] = random.randint(bpp_min, bpp_max)
		bpp_legend.append(str(bpp[i]))

def get_two_types_users():
	global bpp_legend
	bpp_legend = []
	for i in range(n):
		if i % 2 == 0:
			bpp[i] = random.randint(bpp_max*0.9, bpp_max)
		else:
			bpp[i] = random.randint(bpp_min, bpp_min*1.1)
		bpp_legend.append(str(bpp[i]))

def sqm(bpp):
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

get_random_location()
get_two_types_users()
get_same_location()
print bpp_legend
for i in range(time):
	for j in range(n):
		bpp[j] = bpp[j]*(1 + 2*(random.random() - 0.5)*randomness)
	result_sqm.append(sqm(bpp))
	result_paris.append(paris(bpp))

# plotting
fig = plt.figure()
ax = fig.add_subplot(211)
bx = fig.add_subplot(212)
ax2 = ax.twinx()
bx2 = bx.twinx()

results = [result_sqm, result_paris]
axes = [(ax, ax2), (bx, bx2)]
br_with_zero = [0] + br
for ii in range(len(results)): # for each scheme
	rate_count = [0] * (len(br_with_zero) + 1)
	for i in range(n): # for each premium user
		x = []
		y1 = []
		y2 = []
		for j in range(len(results[ii])): # for each second
			x.append(j)
			y1.append(results[ii][j][0][i])
			y2.append(results[ii][j][1][i])
			rate_count[br_with_zero.index(results[ii][j][1][i])] += 1
		axes[ii][1].plot(x, y1, ":", linewidth=2)
		axes[ii][0].plot(x, y2, "-", linewidth=2)
	axes[ii][1].legend(["PRB"], 4)
	axes[ii][0].legend(bpp_legend, 3)
	axes[ii][0].grid()
	#ax.set_xlim([r_s, r_e])
	#ax.set_ylim([0, 4800])
	#ax[i].legend(le[i],fontsize=legend_font_size)
	#ax[i].set_ylabel("++", fontsize=label_font_size)
	axes[ii][1].set_ylabel("PRB")
	axes[ii][0].set_ylabel("Rate (b/s)")
	axes[ii][0].set_xlabel("Time (s)")
	text = ""
	for i in range(len(br_with_zero)):
		text = str(label[i]) + ":" + str("%.2f"%(rate_count[i]*1.0/len(results[ii]))) + ", " + text
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	axes[ii][0].text(0.01, 1.08, text, transform=axes[ii][0].transAxes, verticalalignment='top', fontsize=14, bbox=props)
plt.tight_layout()
plt.savefig("policy.png")