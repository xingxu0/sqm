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

fig = plt.figure()
ax = fig.add_subplot(111)

os.system("rm temp_plot -rf; mkdir temp_plot")

leg = []
max_x = -1
for f in glob.glob("*.pcap"):
	if int(get_id_from_pcap_name(f)) >= 20:
		continue
	os.system("captcp throughput -s 1 -i -f 1.1 -o temp_plot %s"%(f))
	ls = open("temp_plot/throughput.data").readlines()
	x, y = convert(ls)
	ax.plot(x, y)
	max_x = max(max_x, max(x))
	
	os.system("tshark -r %s -z conv,tcp -q | grep \"<->\" > temp_plot/overall_throughput.data"%(f))
	ls = open("temp_plot/overall_throughput.data").readlines()
	s_ = re.split(" +", ls[0])
	avg_thr = int(s_[6])*1.0/float(s_[10])
	leg.append(get_id_from_pcap_name(f) + ":" + str(int(avg_thr)))

#break

ax.set_xlim([0, max_x*1.8])
#ax.set_ylim([0, encoding[len(encoding)-1]*1.2])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
ax.legend(leg, 4, ncol=2)
savefig("plot_pcaps_throughput.png")
