import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, operator
from pylab import *

t_y = {}
def convert(ls):
	global t_x, t_y
	x = []
	y = []
	for l in ls:
		l_ = l.split(" ")
		x.append(float(l_[0]))
		y.append(float(l_[1]))
		if not float(l_[0]) in t_y:
			t_y[float(l_[0])] = float(l_[1])
		else:
			t_y[float(l_[0])] += float(l_[1])
	return x, y

def get_id_from_pcap_name(f):
	m = re.match("(.*)_([0-9]*)\.pcap", f)
	return m.group(2)

fig = plt.figure()
ax = fig.add_subplot(111)
ax2 = ax.twinx()

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

sorted_x = sorted(t_y.items(), key=operator.itemgetter(0))
x_t = []
y_t = []
for x in sorted_x:
	x_t.append(x[0])
	y_t.append(x[1])

ax2.plot(x_t, y_t, ":k")
ax.set_xlim([0, max_x])
#ax.set_ylim([0, encoding[len(encoding)-1]*1.2])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
ax2.set_ylabel("Total Throughput (B/s)")
#ax.legend(leg, 1, ncol=2)
savefig("plot_pcaps_throughput.png")
