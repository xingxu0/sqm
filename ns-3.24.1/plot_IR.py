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

fig = plt.figure()
ax = fig.add_subplot(111)

os.system("rm temp_plot -rf; mkdir temp_plot")

leg = []
max_x = -1

x = []
y = []
x1,y1 = get_data_from_pcap("static/dynamic_weight_0.pcap")
x2,y2 = get_data_from_pcap("dynamic/dynamic_weight_0.pcap")
x3,y3 = get_data_from_pcap("original/dynamic_weight_0.pcap")
x = [x1, x2, x3]
y = [y1, y2, y3]

for i in range(3):
	ax.plot(x[i], y[i])

ax2 = ax.twinx()

x4,y4 = get_ratio(x1,y1,x3,y3)
x5,y5 = get_ratio(x2,y2,x3,y3)
ax2.plot(x4,y4, "-k")
ax2.plot(x5,y5, ":k")

ax.set_xlim([0, max_x*1.8])
#ax.set_ylim([0, encoding[len(encoding)-1]*1.2])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
ax2.set_ylabel("Improvement Ratio")
ax.legend(leg, 1, ncol=2)
savefig("plot_ir.png")
