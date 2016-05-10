import glob, re, os, commands
import numpy as np
from pylab import *

fs = glob.glob("*.out")
avg = {}
std = {}
xs = []
ys = []
t = 0
for f in fs:
	t += 1
	print t, "out of", len(fs)
	r = re.match("rate_ii(.*)_iii(.*).out", f)
	if r != None:
		mcs_ = float(r.group(1))
		req_ = float(r.group(2))
		s = str(mcs_) + " " + str(req_)
		commands.getstatusoutput("python analyze_mcs.py %s 0"%f)
		ls = open("temp.out").readlines()
		avg_ = float(ls[0].split(" ")[2])
		std_ = float(ls[1].split(" ")[2])
		avg[s] = avg_
		std[s] = std_
		if not mcs_ in xs:
			xs.append(mcs_)
		if not req_ in ys:
			ys.append(req_)
xs_sorted = sorted(xs)
ys_sorted = sorted(ys)

data = np.zeros((len(xs), len(ys)))
for a in std:
	a_ = a.split(" ")
	x_ = float(a_[0])
	y_ = float(a_[1])
	data[xs_sorted.index(x_), ys_sorted.index(y_)] = avg[a]

subplot(1, 1, 1)
pcolor(data)
colorbar()
xticks(np.array(range(len(ys))) + 0.5, ys_sorted)
xlabel("requirement interval")
ylabel("MCS interval")
#title("DL rate")
title("mean")
yticks(np.array(range(len(xs))) + 0.5, xs_sorted)
savefig("plot_interval.png")



