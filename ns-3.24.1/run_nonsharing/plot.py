import glob, commands, os, operator, pickle, re
import matplotlib.pyplot as plt

fs = glob.glob("*.out")

d = {}
for f in fs:
	rate = float(re.match("(.*)trace_log_(.*).out", f).group(2))
	ls = open(f).readlines()
	for l in ls:
		s = re.split(" +", l)
		i = s[2].split(":")[0]
		r = int(s[6])
		if i in d:
			d[i][rate] = r*8.0/59/1000000
		else:
			d[i] = {}

leg = []
ax = plt.subplot()
for x in d:
	sorted_x = sorted(d[x].items(), key=operator.itemgetter(0))
	xx = []
	yy = []
	for p in sorted_x:
		xx.append(p[0])
		yy.append(p[1])
	ax.plot(xx, yy, "-+")
	leg.append(str(x))
	
ax.set_xlim([0, 2.0])
ax.set_ylim([0, 0.8])
ax.set_xlabel("bottleneck rate (Mb/s)")
ax.set_ylabel("downlink rate (Mb/s)")
plt.savefig('plot.png')
	
	
