import glob, commands, os, operator, pickle, re
import matplotlib.pyplot as plt

ls = open("DlMacStats.txt").readlines()[1:]

x = []
y = []
d = {}
d2 = {}
for l in ls:
	s = re.split(" +|\t+", l)
	loc = int(s[2])*500 + 3000 - 500
	mcs = int(s[6])
	size = int(s[7])
	d[loc] = mcs
	d2[loc] = size

sorted_x = sorted(d.items(), key=operator.itemgetter(0), reverse=True)
for xx in sorted_x:
	x.append(xx[0])
	y.append(xx[1])

print x
print y

ax = plt.subplot()

ax.plot(x, y, "-+")
ax.legend(["MCS"], 2)
ax.set_ylim([0, 35])

x = []
y = []
sorted_x = sorted(d2.items(), key=operator.itemgetter(0), reverse=True)
for xx in sorted_x:
	x.append(xx[0])
	y.append(xx[1])
	
print x
print y
	
ax2 = ax.twinx()	
ax2.plot(x, y, "-+r")
ax2.legend(["TBS"], 1)
ax.set_xlabel("distance (m)")
ax.set_ylabel("MCS")
ax2.set_ylabel("TBS")
plt.tight_layout()
plt.savefig('plot.png')
	
	
