import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, re, math, operator
from pylab import *
import numpy as np

f = "t_slow_rate_0.4.out"
ls = open(f).readlines()

d = {}
for l in ls:
	# 1.251s 0x205f900 UE 69 LC 4 txqueue 229935 retxqueue 0 status 0 decrease 2196
	m = re.match("(.*)s 0x(.*) UE (.*) LC 3 txqueue (.*) retxqueue (.*) status (.*) decrease (.*)", l)
	if m != None:
		t = float(m.group(1))
		u = int(m.group(3))
		tx = int(m.group(4))
		if u in d:
			d[u].append((t, tx))
		else:
			d[u] = [(t, tx)]

fig = plt.figure()
ax = fig.add_subplot(111)

leg = []
print len(d)
ll = 0
for u in d:
	x = []
	y = []
	m_ = 0
	for xx in d[u]:
		x.append(xx[0])
		y.append(xx[1])
		if xx[1] > m_:
			m_ = xx[1]
	if m_ < 50000:
		ll += 1
		ax.plot(x, y)
		leg.append(str(u))
		
print "light users", ll
ax.set_xlabel("Time (s)")
ax.set_ylabel("TxQueue (B)")
ax.legend(leg)
savefig("plot_temp.png")
