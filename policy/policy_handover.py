import matplotlib, re, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands, copy
import numpy as np
#import statistics
import policy_schemes as common

pid = os.getpid()

#signal range's default is 37%
#print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent] [signal range]"
#print "python policy.py [scheme] [# premium users] [\% of premium resources] [# normal users] [silent] [trace name] [admission control]"
#print "\t schemes. 1: random location; 2: same location; 3: good and bad"

scheme = int(sys.argv[1])
common.n = int(sys.argv[2])
common.percentage = float(sys.argv[3])
common.normal_n = int(sys.argv[4])
# common.time = 
silent = int(sys.argv[5])
tracename  = sys.argv[6]
admission_control_scheme = int(sys.argv[7])
#if len(sys.argv) > 7:
#	time = int(sys.argv[7])
#if len(sys.argv) > 6:
#	r = float(sys.argv[6])
#	bpp_min = int(bpp_mid*(1-r))
#	bpp_max = int(bpp_mid*(1+r))

#random.seed(0)
random.seed()
result_sqm = []
result_sqm2 = []
result_sqm3 = []
result_paris = []
result_paris2 = []
result_paris3 = []
result_now = []
bpp = {}
bpp_legend = []
randomness = 0.02
filename = ""
issue = 0

join_time = []
leave_time = []

def get_same_location():
	global bpp_legend, filename
	filename = "same_signal"
	bpp_legend = []
	x = random.randint(common.bpp_min, common.bpp_max)
	for i in range(common.n):
		bpp[i] = x
		bpp_legend.append(str(bpp[i]))

def get_random_location():
	global bpp_legend, filename
	filename = "random_location"
	bpp_legend = []
	for i in range(common.n):
		bpp[i] = random.randint(common.bpp_min, common.bpp_max)
		bpp_legend.append(str(bpp[i]))

def get_two_types_users():
	global bpp_legend, filename
	filename = "good_bad_users"
	bpp_legend = []
	for i in range(common.n):
		if i % 2 == 0:
			bpp[i] = random.randint(int(common.bpp_max*0.9), common.bpp_max)
		else:
			bpp[i] = random.randint(common.bpp_min, int(common.bpp_min*1.1))
		bpp_legend.append(str(bpp[i]))

#generate join time

last = 0
for i in range(common.n):
	#join_time.append(last + random.randint(0, 10))
	#join_time.append(last + 60)
	join_time.append(last)
	leave_time.append(last + common.time)
	#join_time.append(0)
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
u_paris2 = []
u_paris3 = []
u_now = []
df_sqm = [0] * common.n # this is downgrade fraction
df_sqm2 = [0] * common.n
df_sqm3 = [0] * common.n
df_paris = [0] * common.n
df_paris2 = [0] * common.n
df_paris3 = [0] * common.n
df_now = [0] * common.n
pre_sqm, pre_sqm2, pre_sqm3, pre_paris, pre_paris2, pre_paris3, pre_now = -1, -1, -1, -1, -1, -1, -1
u_a_sqm = [] # this is average utility
u_a_sqm2 = []
u_a_sqm3 = []
u_a_paris = []
u_a_paris2 = []
u_a_paris3 = []
u_a_now = []
last_r = []
last_r2 = []
last_r3 = []
admitted_sqm = [0] * common.n
admitted_sqm2 = [0] * common.n
admitted_sqm3 = [0] * common.n   # with minimum support
admitted_paris = [0] * common.n
admitted_paris2 = [0] * common.n
admitted_paris3 = [0] * common.n
admitted_now = [0] * common.n
admitted = [admitted_sqm, admitted_sqm2, admitted_sqm3, admitted_paris, admitted_paris2, admitted_paris3, admitted_now]

current_user = 0
new_user = 0
leave_user = 0
for i in range(max(leave_time)): #common.time):
	for j in range(common.n):
		if join_time[j] == i:
			new_user += 1
	for j in range(common.n):
		if leave_time[j] == i:
			leave_user -= 1
			for ad in admitted:
				ad[j] = 2 # 2 means already leave
	for j in range(common.n):
		bpp[j] = bpp[j]*(1 + 2*(random.random() - 0.5)*randomness)
	r1, r2, r3 = common.sqm(bpp, admitted_sqm, new_user, current_user, last_r, admission_control_scheme)
	u_sqm.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm.append(sum(r2)*1.0/common.count_admitted_user(admitted_sqm) if common.count_admitted_user(admitted_sqm) else 0 )
	result_sqm.append([r1, r2])
	last_r = copy.deepcopy(r3)
	common.get_downgrade_fraction([r1, r2], admitted_sqm, df_sqm)
	
	r1, r2, r3 = common.sqm_minimum_support(bpp, admitted_sqm2, new_user, current_user, last_r2, admission_control_scheme, 0)
	u_sqm2.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm2.append(sum(r2)*1.0/common.count_admitted_user(admitted_sqm2) if common.count_admitted_user(admitted_sqm2) else 0 )
	result_sqm2.append([r1, r2])
	last_r2 = copy.deepcopy(r3)
	common.get_downgrade_fraction([r1, r2], admitted_sqm2, df_sqm2)
	
	r1, r2, r3 = common.sqm_minimum_support(bpp, admitted_sqm3, new_user, current_user, last_r2, admission_control_scheme, 1)
	u_sqm3.append(sum(r2)*1.0)#/count_admitted_user(admitted_sqm))
	u_a_sqm3.append(sum(r2)*1.0/common.count_admitted_user(admitted_sqm3) if common.count_admitted_user(admitted_sqm3) else 0 )
	result_sqm3.append([r1, r2])
	last_r3 = copy.deepcopy(r3)
	common.get_downgrade_fraction([r1, r2], admitted_sqm3, df_sqm3)
	
	r = common.paris(bpp, admitted_paris, new_user, current_user, admission_control_scheme)
	u_paris.append(sum(r[1])*1.0)#/count_admitted_user(admitted_paris))
	u_a_paris.append(sum(r[1])*1.0/common.count_admitted_user(admitted_paris) if common.count_admitted_user(admitted_paris) else 0)
	result_paris.append(r)
	common.get_downgrade_fraction(r, admitted_paris, df_paris)
	
	r = common.paris2(bpp, admitted_paris2, new_user, current_user, admission_control_scheme)
	u_paris2.append(sum(r[1])*1.0)#/count_admitted_user(admitted_paris))
	u_a_paris2.append(sum(r[1])*1.0/common.count_admitted_user(admitted_paris2) if common.count_admitted_user(admitted_paris2) else 0)
	result_paris2.append(r)
	common.get_downgrade_fraction(r, admitted_paris2, df_paris2)
	
	r = common.paris3(bpp, admitted_paris3, new_user, current_user, admission_control_scheme)
	u_paris3.append(sum(r[1])*1.0)#/count_admitted_user(admitted_paris))
	u_a_paris3.append(sum(r[1])*1.0/common.count_admitted_user(admitted_paris3) if common.count_admitted_user(admitted_paris3) else 0)
	result_paris3.append(r)
	common.get_downgrade_fraction(r, admitted_paris3, df_paris3)
	
	r = common.now(bpp, admitted_now, new_user, current_user, admission_control_scheme)
	u_now.append(sum(r[1])*1.0)#/count_admitted_user(admitted_now))
	u_a_now.append(sum(r[1])*1.0/common.count_admitted_user(admitted_now) if common.count_admitted_user(admitted_now) else 0)
	result_now.append(r)
	common.get_downgrade_fraction(r, admitted_now, df_now)
	
	current_user = current_user + new_user - leave_user
	new_user = 0
	leave_user = 0
		
#f = open("temp", "w")
#f.write(str(np.mean(u_sqm)) +" " + str(np.mean(u_sqm2)) +" " + str(np.mean(u_sqm3)) +" " + str(np.mean(u_paris)) + " " + str( np.mean(u_now)) + "\n")
#f.write(str(np.mean(u_a_sqm)) +" "+ str(np.mean(u_a_sqm2)) +" " + str(np.mean(u_a_sqm3)) +" " +str(np.mean(u_a_paris)) + " " + str( np.mean(u_a_now)) + "\n")

results = [result_sqm, result_sqm2, result_sqm3, result_paris, result_paris2, result_paris3, result_now]

def generate_file(f, r, j, s, e):
	randomness = 0.05
	switches = 0
	with open(f, "w") as fo:
		for i in range(s, e):
			random_ = 2*(random.random() - 0.5)*randomness
			fo.write(str(i*1000) + " " + str(max(1, r[i][1][j]*(1+random_))) + "\n")
			if i and r[i][1][j] in common.br and r[i - 1][1][j] in common.br and r[i][1][j] != r[i - 1][1][j]:
				switches += 1
		fo.close()
	return switches

qoe_total = [0] * len(results)
qoe_avg = [0] * len(results)
qoe = [[[0,0,0,0,0,0] for y in range(common.n)] for x in range(len(results))] # average bitrate, rebuffer, switches, admitted
ad = [admitted_sqm, admitted_sqm2, admitted_sqm3, admitted_paris, admitted_paris2, admitted_paris3, admitted_now]
df = [df_sqm,df_sqm2,df_sqm3,df_paris,df_paris2,df_paris3,df_now]
for i in range(len(results)):
	r = results[i]
	for j in range(common.n):
		switches = generate_file("temp_trace_%d"%(pid), r, j, join_time[j], leave_time[j])
		o = commands.getstatusoutput("python ABRSim/ABRSimNew/simulation.py temp_trace_%d"%(pid))
		#print o
		g = re.match("QoE: (.*) avg. bitrate: (.*) buf. ratio: (.*) numSwtiches: (.*) dominant BR: (.*) played (.*) out of (.*)", o[1])
		metric = 2
		if g != None and float(g.group(metric)) > 0:
			qoe_total[i] += float(g.group(metric))
			qoe[i][j][0] = float(g.group(2))
			qoe[i][j][1] = float(g.group(3))
			qoe[i][j][2] = float(g.group(4))
			qoe[i][j][3] = min(1, ad[i][j]) # 2 for admitted but ended, so need to upper bound by 1
			qoe[i][j][4] = switches
			qoe[i][j][5] = df[i][j]
		else:
			qoe_total[i] += 0
			print "***", i, j
			os.system("cp temp_trace_%d issue_%d_%d_%d_%d"%(pid, pid, i,j,issue))
			issue += 1
	qoe_avg[i] = qoe_total[i]*1.0/common.count_admitted_user(ad[i]) if common.count_admitted_user(ad[i]) else 0
	os.system("rm temp_trace_%d"%(pid))

with open(tracename, "w") as f:			
	for i in range(len(results)):
		r = results[i]
		ind = [3, 0, 1, 2, 4, 5]
		for kk in range(6):
			k = ind[kk]
			text = ""
			for j in range(common.n):
				text += str(qoe[i][j][k]) + " "
			f.write(text[:-1] + "\n")
	f.close()

# plotting
fig = plt.figure(figsize=(35,10))
ax = fig.add_subplot(271)
bx = fig.add_subplot(272)
cx = fig.add_subplot(273)
dx = fig.add_subplot(274)
ex = fig.add_subplot(275)
fx = fig.add_subplot(276)
gx = fig.add_subplot(277)
axu = fig.add_subplot(278)
bxu = fig.add_subplot(279)
cxu = fig.add_subplot(2,7,10)
dxu = fig.add_subplot(2, 7, 11)
exu = fig.add_subplot(2, 7, 12)
fxu = fig.add_subplot(2, 7, 13)
gxu = fig.add_subplot(2, 7, 14)
ax2 = ax.twinx()
bx2 = bx.twinx()
cx2 = cx.twinx()
dx2 = dx.twinx()
ex2 = ex.twinx()
fx2 = fx.twinx()
gx2 = gx.twinx()

axes = [(ax, ax2), (bx, bx2), (cx, cx2), (dx, dx2), (ex, ex2), (fx, fx2), (gx, gx2)]
axesu = [axu, bxu, cxu, dxu, exu, fxu, gxu]
results_u = [u_sqm, u_sqm2, u_sqm3, u_paris, u_paris2, u_paris3, u_now]
max_u = max(max(u_sqm), max(u_paris), max(u_paris2), max(u_now), max(u_sqm2), max(u_sqm3), max(u_paris3))
for ii in range(len(results)): # for each scheme
	
	rate_count = [0] * (len(common.br_with_zero) + 1)
	x = []
	for i in range(common.n): # for each premium user
		x = []
		y1 = []
		y2 = []
		for j in range(len(results[ii])): # for each second
			x.append(j)
			y1.append(results[ii][j][0][i])
			# plot rate between rate level
			value = 0
			if results[ii][j][1][i] in common.br_with_zero:
				value = common.br_with_zero.index(results[ii][j][1][i])
			else:
				for k in range(len(common.br_with_zero)):
					if common.br_with_zero[k] > results[ii][j][1][i]:
						break
				value = k - 1 + (results[ii][j][1][i] - common.br_with_zero[k - 1])/(common.br_with_zero[k] - common.br_with_zero[k - 1])
			y2.append(value)
			#y2.append(common.br_with_zero.index(results[ii][j][1][i]) if results[ii][j][1][i] in common.br_with_zero else 0)
			rate_count[common.br_with_zero.index(results[ii][j][1][i]) if results[ii][j][1][i] in common.br_with_zero else 0] += 1
		axes[ii][1].plot(x, y1, ":", linewidth=2)
		axes[ii][0].plot(x, y2, "-", linewidth=2)
	#axes[ii][1].legend(["PRB"], 1, ncol=6)
	axes[ii][0].legend(bpp_legend, 1, ncol=3)
	axes[ii][0].grid()
	#ax.set_xlim([r_s, r_e])
	#ax.set_ylim([0, 4800])
	#ax[i].legend(le[i],fontsize=legend_font_size)
	#ax[i].set_ylabel("++", fontsize=label_font_size)
	axes[ii][1].set_ylabel("PRB")
	axes[ii][0].set_ylabel("Rate (Quality level)")
	axes[ii][0].set_xlabel("Time (s)")
	text = ""
	for i in range(len(common.br_with_zero)):
		text = str(common.label[i]) + ":" + str("%.2f"%(rate_count[i]*1.0/len(results[ii]))) + ", " + text
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
	axes[ii][0].text(0.01, 1.03, text, transform=axes[ii][0].transAxes, verticalalignment='top', fontsize=14, bbox=props)
	axes[ii][0].set_ylim([-1, len(common.br_with_zero)*1.3])
	
	total = [0,0,0,0,0]
	for i in range(common.n):
		text = "AD: %s A: %.0f R: %.4f S: %d BRS: %d"%("Y" if qoe[ii][i][3] >= 1 else "N", qoe[ii][i][0], qoe[ii][i][1], qoe[ii][i][2], qoe[ii][i][4])
		axesu[ii].text(0.01, 0.9 - i*(1.0/(common.n+1)), text, transform=axesu[ii].transAxes, verticalalignment='top', fontsize=14, bbox=props)
		total[0] += qoe[ii][i][0]
		total[1] += qoe[ii][i][1]
		total[2] += qoe[ii][i][2]
		total[4] += qoe[ii][i][4]
		if qoe[ii][i][3] != -1:
			total[3] += 1
	
	text = "Total: DF: %d\nAD: %d A: %.0f R: %.4f S: %d BRS: %d"%(df[ii][0], total[3], total[0], total[1], total[2], total[4])
	axesu[ii].text(0.01, 0.9 - common.n*(1.0/(common.n+1)), text, transform=axesu[ii].transAxes, verticalalignment='top', fontsize=15, bbox=props)
	
	axesu[ii].plot(x, results_u[ii])
	axesu[ii].set_ylim([0, max_u*1.1])
	axesu[ii].set_ylabel("objective function")
	axesu[ii].set_xlabel("time")
plt.tight_layout()
if not silent:
	plt.savefig("policy_dynamic_%s_np%d_nt%d_p%.2f.png"%(filename, common.n, common.normal_n, common.percentage))
