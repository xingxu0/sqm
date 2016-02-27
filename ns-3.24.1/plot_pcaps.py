import os, sys, glob
import matplotlib.pyplot as plt
from pylab import *

def convert(ls):
	x = []
	y = []
	for l in ls:
		l_ = l.split(" ")
		x.append(float(l_[0]))
		y.append(float(l_[1]))
	return x, y

fig = plt.figure()
ax = fig.add_subplot(111)

os.system("rm temp_plot -rf; mkdir temp_plot")

leg = []
for f in glob.glob("*.pcap"):
	os.system("captcp throughput -s 1 -i -f 1.1 -o temp_plot %s"%(f))
	ls = open("temp_plot/throughput.data").readlines()
	x, y = convert(ls)
	leg.append(f)
	ax.plot(x, y)
	#break

#ax.set_xlim([0, 2300000])
#ax.set_ylim([0, encoding[len(encoding)-1]*1.2])
ax.set_xlabel("Time (s)")
ax.grid()
ax.set_ylabel("Throughput (B/s)")
#ax.legend(leg, 4)
savefig("plot_pcaps_throughput.png")
