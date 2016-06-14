import matplotlib, re
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator, random, commands
import numpy as np
sys.path.append("../")
from plot import *

def generate_file(f, r, t):
	randomness = 0.15
	fo = open(f, "w")
	data = []
	for i in range(t):
		random_ = 2*(random.random() - 0.5)*randomness
		data.append(r*(1+random_))
		fo.write(str(i*1000) + " " + str(max(1, r*(1+random_))) + "\n")
	#print np.mean(data), np.std(data)

duration = int(sys.argv[1])
x = []
y1 = []
y2 = []
r_s = 350
r_e = 6000
step = 50
for i in range(r_s, r_e, step):
	if i%100 == 0:
		print i
	generate_file("temp", i, duration)
	o = commands.getstatusoutput("python simulation.py temp")
	g = re.match("QoE: (.*) avg. bitrate: (.*) buf. ratio: (.*) numSwtiches: (.*) dominant BR: (.*) played (.*) out of (.*)", o[1])
	x.append(i)
	y1.append(float(g.group(2)))
	y2.append(float(g.group(5)))

fig = plt.figure()
ax = fig.add_subplot(111)
#ax2 = ax.twinx()

print y1
print y2


ax.plot(x, y1, "-b", linewidth = line_width)
#ax.plot([-1,-1],[-1,-1], "--r")
ax.plot(x, y2, "--k", linewidth = line_width)
xxx = [450, 1000, 1500, 3000, 5000]
xx = [350, 700, 1200, 2400, 4800]
for i in range(5):
	print xxx[i], xx[i]
	ax.annotate('Video Bitrate\nCandidates', xy=(xxx[i], xx[i]), xytext=(500, 3600), arrowprops=dict(facecolor='black', shrink=0.05), fontsize=legend_font_size)
	#ax.plot([0, 300], [x, x], ":r", linewidth = line_width)
ax.legend(["Average Bitrate", "Dominate Bitrate"], 4, fontsize=legend_font_size)
#ax2.legend(["maxQoE"], 4)
ax.grid()
ax.set_xlim([0, r_e])
ax.set_ylim([0, 5000])
#ax[i].legend(le[i],fontsize=legend_font_size)
#ax[i].set_ylabel("++", fontsize=label_font_size)
ax.set_ylabel("Video Bitrate (Kb/s)", fontsize=label_font_size)
#ax2.set_ylabel("")
ax.set_xlabel("Maintained Rate (Kb/s)", fontsize=label_font_size)

textstr = "bitrates candidate:\n350\n700\n1200\n2400\n4800"
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#ax.text(0.65, 0.4, textstr, transform=ax.transAxes, verticalalignment='top', fontsize=14, bbox=props)
set_ax(ax)
plt.tight_layout()
plt.savefig("r_to_br_%s.png"%(duration))
plt.savefig("r_to_br_%s.eps"%(duration))