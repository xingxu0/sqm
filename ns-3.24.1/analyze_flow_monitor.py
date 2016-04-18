import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator
from pylab import *

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
		if t-last_t == 0:
			print i, thr, last, t, last_t
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
for l in ls:
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
	
	m = re.match("Last Received Packet([ \t]*): (.*) Seconds", l)
	if m != None:
		global_t = float(m.group(2))
		if flow == -1:
			continue
		if not flow in data:
			data[flow] = [] #[(-1, 0, global_t)]
		data[flow].append((time, r_b, global_t))
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
for i in data:
	#if i <=14:
	#	continue
	print i
	print data[i][:20]
	x, y = convert_to_second_throughput(data[i])
	max_x = max(max_x, max(x))
	print max_x
	ax.plot(x, y)
	leg.append(str(i))
	
if o == "1":
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

sorted_x = sorted(t_y.items(), key=operator.itemgetter(0))
x_t = []
y_t = []
for x in sorted_x:
	x_t.append(x[0])
	y_t.append(x[1])		

ax.set_xlim([0, max_x*1.3])
ax2.plot(x_t, y_t, ":k")
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
ax2.set_ylabel("Total Throughput (B/s)")
ax.legend(leg, 1, ncol=1)
savefig("plot_flow_mon.png")
