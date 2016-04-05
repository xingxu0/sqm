import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re
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
	x = []
	y = []
	last = 0
	for a in i:
		t = a[0]
		thr = a[1]
		x.append(t)
		y.append(thr*t - last*(t-1))
		last = thr
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

f = sys.argv[1]
ls = open(f).readlines()

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
	
	m = re.match("Duration([ \t]*): (.*)", l)
	if m != None:
		time = float(m.group(2))
		continue
	
	m = re.match("Throughput([ \t]*): (.*) B/s", l)
	if m != None:
		thr = float(m.group(2))
		if flow == -1:
			continue
		if not flow in data:
			data[flow] = []
		data[flow].append((time, thr))

	
fig = plt.figure()
ax = fig.add_subplot(111)

leg = []
max_x = -1
for i in data:
	if i >=10:
		continue
	print i
	print data[i][:20]
	x, y = convert_to_second_throughput(data[i])
	max_x = max(max_x, max(x))
	ax.plot(x, y)
	leg.append(str(i))
	
max_x = -1
for f in glob.glob("*.pcap"):
	if int(get_id_from_pcap_name(f)) >= 10:
		continue
	os.system("captcp throughput --mode network-layer -s 1 -i -f 1.1 -o temp_plot %s"%(f))
	ls = open("temp_plot/throughput.data").readlines()
	x, y = convert(ls)
	ax.plot(x, y, "--")
	max_x = max(max_x, max(x))
	
	os.system("tshark -r %s -z conv,tcp -q | grep \"<->\" > temp_plot/overall_throughput.data"%(f))
	ls = open("temp_plot/overall_throughput.data").readlines()
	s_ = re.split(" +", ls[0])
	avg_thr = int(s_[6])*1.0/float(s_[10])
	leg.append(get_id_from_pcap_name(f) + ":" + str(int(avg_thr)))

ax.set_xlim([0, max_x*1.3])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
ax.legend(leg, 1, ncol=1)
savefig("plot_flow_mon.png")
