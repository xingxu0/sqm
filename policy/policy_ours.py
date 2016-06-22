import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
#import statistics

pid = os.getpid()

n = 6
normal_n = 30 #number of normal user
bpp_mid = int((135+292)*0.8/2)
bpp_min = int(135*0.8) # bpp is bytes per prb
bpp_max = int(292*0.8)  # this value maps to 712bits/s as TBS
total_prb = 12000*4
percentage = .3
lock_parameter = 0 #0.3
time = 600

br = [350, 700, 1200, 2400, 4800]
#br = [350, 700, 1200, 2400]
br_with_zero = [0] + br
label = ["N","R1", "R2", "R3", "R4", "R5"]

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

def count_admitted_user(a): # user with 1 is admitted, -1 is rejected, 0 is not seen
	c = 0
	for x in a:
		if x == 1:
			c += 1
	return c

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
		
def sqm_admission(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += br_with_zero[1]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm rejected user ", x
		
def sqm_admission2(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += 2000*1000.0/(bpp[i]*8)#br_with_zero[-2]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm2 rejected user ", x

def sqm_admission3(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb +=1000*1000.0/(bpp[i]*8) # br_with_zero[len(br_with_zero)/2-1]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm3 rejected user ", x
		
def paris_admission(admitted, x, bpp):
	admitted_ = 0 # number of admitted user
	admitted[x] = 1
	admitted_ = count_admitted_user(admitted)
	if total_prb*1.0*percentage/admitted_ > total_prb*(1.0-percentage)/normal_n:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "paris rejected user ", x, total_prb*1.0*percentage/admitted_, total_prb*(1.0-percentage)/normal_n

def sqm(bpp, admitted, new_user, current_premium_user, last, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				else:
					sqm_admission3(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	used = 0
	ret_prb = {}
	ret_rate = {}
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1), reverse=True)
	for i in range(len(sorted_bpp)):
		ret_prb[sorted_bpp[i][0]] = 0
		ret_rate[sorted_bpp[i][0]] = 0
		if admitted[sorted_bpp[i][0]] != 1:
			continue
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
	if last != []:
		if last[1] != ret_rate_:
			diff = 0
			for i in range(len(last[1])):
				diff += abs(br_with_zero.index(int(last[1][i])) - br_with_zero.index(ret_rate_[i]))
				if abs(br_with_zero.index(last[1][i]) - br_with_zero.index(ret_rate_[i])) >= len(br_with_zero)/2:
					diff += n
			if diff >= n - 1:
				# check last solution is still feasible or not
				t_prb = 0
				for i in range(len(last[1])):
					t_prb += last[1][i]*1.0/(bpp[i]*8)
				if t_prb <= available and abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_)) <lock_parameter:
					#print "\tusing last",diff, last[1], ret_rate_, abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_))
					ret_prb_ = copy.deepcopy(last[0])
					ret_rate_ = copy.deepcopy(last[1])
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]
	#return ret_prb_, ret_rate_, premium_allocation
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
				ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000
	return ret_prb_, ret_rate_, premium_allocation


def paris(bpp, admitted, new_user, current_premium_user):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	ret_prb = {}
	ret_rate = {}
	admitted_ = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			admitted_ += 1
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = available/admitted_
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
		ret_rate[i] = temp_rate
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	return ret_prb_, ret_rate_

def now(bpp, admitted, new_user, current_premium_user):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				admitted[i] = 1
				new_user -= 1
	ret_prb = {}
	ret_rate = {}
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = total_prb/(normal_n + current_premium_user)
		#print total_prb, normal_n, current_premium_user, total_prb/(normal_n + current_premium_user)
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
		ret_rate[i] = temp_rate
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	return ret_prb_, ret_rate_

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

scheme_label = ["sqm1", "sqm2", "sqm3", "paris", "now"]
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
	
	r1, r2, r3 = sqm(bpp, admitted_sqm2, new_user, current_user, last_r2, 2)
	u_sqm2.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm2.append(sum(r2)*1.0/count_admitted_user(admitted_sqm2) if count_admitted_user(admitted_sqm2) else 0 )
	result_sqm2.append([r1, r2])
	last_r2 = copy.deepcopy(r3)
	
	r1, r2, r3 = sqm(bpp, admitted_sqm3, new_user, current_user, last_r2, 3)
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
			#y1.append(results[i][k][0][j]) # prb
			y1.append(results[i][k][1][j]) # rate
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