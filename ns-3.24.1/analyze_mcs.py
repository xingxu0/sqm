import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator
from pylab import *
import numpy as np

def convert(ls):
	x = []
	y = []
	for l in ls:
		l_ = l.split(" ")
		x.append(float(l_[0]))
		y.append(float(l_[1]))
	return x, y

def get_data_from_pcap(f):
	os.system("captcp throughput -s 1 -i -f 1.1 -o temp_plot %s"%(f))
	ls = open("temp_plot/throughput.data").readlines()
	return convert(ls)

def convert_to_second_throughput(i):
	global t_y
	x = []
	y = []
	last = 0 
	last_t = -0.0000000000001
	for a in i:
		t = a[0]
		thr = a[1]
		global_t = a[2]
		real_t = int(round(global_t - 1))
		x.append(real_t)
		if t-last_t == 0 and thr-last != 0:
			print i, thr, last, t, last_t
		if t-last_t == 0:
			r = 0
		else:
			r = (thr - last)*1.0/(t-last_t)
		y.append(r)
		last = thr
		last_t = t
		if not real_t in t_y:
			t_y[real_t] = r
		else:
			t_y[real_t] += r
	return x, y

def get_id_from_pcap_name(f):
	m = re.match("(.*)_([0-9]*)\.pcap", f)
	return m.group(2)

def get_data_from_pcap(f):
	os.system("captcp throughput -s 1 -i -f 1.1 -o temp_plot %s"%(f))
	ls = open("temp_plot/throughput.data").readlines()
	return convert(ls)

def get_ratio(x1, y1, x2, y2):
	global max_x
	x = []
	y = []
	for i in range(len(x1)):
		x.append(x1[i])
		y.append(y1[i]*1.0/y2[i])
	max_x = max(max_x, max(x))
	return x,y

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

f = sys.argv[1]
ls = open(f).readlines()
o = sys.argv[2] # read pcap files?

# Flow ID			: 38 ; 7.0.0.2 -----> 1.0.0.2
flow = -1
thr = -1
time = -1
data = {}
prbs = []
selected_prbs = []
weight = []
mcs = []
temp_mcs = []
temp_weight = []
for i in range(len(ls)):
	l = ls[i]
	if l.find("Flow ID") != -1:
		m = re.match("Flow ID(.*)1\.0\.(.*)\.2 -----> (.*)", l)
		if m != None:
			flow = int(m.group(2))
		else:
			flow = -1
		continue
	
	m = re.match("Rx Bytes = (.*)", l)
	if m != None:
		r_b = float(m.group(1))
		continue
	
	m = re.match("Duration([ \t]*): (.*)", l)
	if m != None:
		time = float(m.group(2))
		continue
	
	result = re.match("0, mcs:(.*), count:(.*)\((.*)\) selected mcs:(.*), selected count:(.*)\((.*)\), prb:(.*), w:(.*), estimated:(.*)", l)
	if result != None:
		temp_mcs.append(float(result.group(9)))
		continue
	
	w_result = re.match("new weight:(.*)total_prb:(.*)", l)
	if w_result != None:
		temp_weight.append(max(float(w_result.group(1)), 1))
	
	m = re.match("Last Received Packet([ \t]*): (.*) Seconds", l)
	if m != None:
		global_t = float(m.group(2))
		if flow == -1:
			continue
		if not flow in data:
			data[flow] = [] #[(-1, 0, global_t)]
		data[flow].append((time, r_b, global_t))
		for ind in range(i-15, i-7):
			result = re.match("0, mcs:(.*), count:(.*)\((.*)\) selected mcs:(.*), selected count:(.*)\((.*)\), prb:(.*), w:(.*), estimated:(.*)", ls[ind])
			if result != None:
				prbs.append((global_t + 1, float(result.group(9))))
				selected_prbs.append((global_t, float(result.group(6))))
				w_result = re.match("new weight:(.*)total_prb:(.*)", ls[ind + 1])
				tt = float(w_result.group(1))
				weight.append((global_t, max(tt, 1)))
				break
	'''
	m = re.match("Throughput([ \t]*): (.*) B/s", l)
	if m != None:
		thr = float(m.group(2))
		thr = max(0, thr)
		if math.isinf(thr):
			thr = 0
		
		if flow == -1:
			continue
		if not flow in data:
			data[flow] = []
		data[flow].append((time, thr))
	'''
	
fig = plt.figure()
ax = fig.add_subplot(111)
ax2 = ax.twinx()

leg = []
t_y = {}
max_x = -1
max_y = -1
u0_mean = 0
u0_std = 0
w_mean = 0
mcs_mean = 0
for i in data:
	if i >=30:
		continue
	print i
	print data[i][:20]
	x, y = convert_to_second_throughput(data[i])
	if i == 0:
		u0_mean = np.mean(y)
		u0_std = np.std(y)
	max_x = max(max_x, max(x))
	max_y = max(max_y, max(y))
	print max_x
	ax.plot(x, y)
	leg.append(str(i))
	
if o == "3":
	for f in glob.glob("*.pcap"):
		os.system("captcp throughput --mode network-layer -s 1 -i -f 1.1 -o temp_plot %s"%(f))
		ls = open("temp_plot/throughput.data").readlines()
		x, y = convert(ls)
		ax.plot(x, y, "--")
		max_x = max(max_x, max(x))
		
		avg_thr = "0"
		os.system("tshark -r %s -z conv,tcp -q | grep \"<->\" > temp_plot/overall_throughput.data"%(f))
		ls = open("temp_plot/overall_throughput.data").readlines()
		s_ = re.split(" +", ls[0])
		avg_thr = int(s_[6])*1.0/float(s_[10])
		leg.append(get_id_from_pcap_name(f) + ":" + str(int(avg_thr)))

#sorted_x = sorted(prbs.items(), key=operator.itemgetter(0))
if o == "1":
	x_t = []
	y_t = []
	print prbs
	for x in prbs:
		x_t.append(x[0])
		y_t.append(x[1])
	ax2.plot(x_t, y_t, "-+k", markevery=10)
	x_t = []
	y_t = []
	for x in selected_prbs:
		x_t.append(x[0])
		y_t.append(x[1])
	ax2.plot(x_t, y_t, ":xk", markevery=12)
	ax2.set_ylabel("MCS")
	ax2.legend(['estimated', 'avg. selected'], 1, ncol=1)

if o == "2":
	x_t = []
	y_t = []
	for x in weight:
		x_t.append(x[0])
		y_t.append(x[1])
	ax2.plot(x_t, y_t, ":xk", markevery=12)
	ax2.set_ylabel("Weight")

x_t = []
y_t = []
for x in weight:
	x_t.append(x[0])
	y_t.append(x[1])
w_mean = np.mean(y_t)

w_mean = np.mean(temp_weight)

x_t = []
y_t = []
for x in prbs:
	x_t.append(x[0])
	y_t.append(x[1])
mcs_mean = np.mean(y_t)

mcs_mean = np.mean(temp_mcs)

	
ax.set_xlim([0, max_x*1.3])
ax.set_ylim([0, max_y*1.1])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")

textstr = "u0 mean %.2f"%u0_mean + "\nu0 std %.2f"%u0_std + "\nW mean %.2f"%w_mean + "\nmcs mean %.2f"%mcs_mean
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

savefig("plot_" + f + "_mcs" + o +".png")
f = open("temp.out", "w")
f.write(textstr)
f.close()
