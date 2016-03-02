import matplotlib
matplotlib.use('Agg')
import glob, os, sys, re, math, operator
import matplotlib.pyplot as plt
import numpy as np

def get_time(s):
	s_ = s.split("@")[1]
	s__ = s_.split(":")
	return 3600*int(s__[0])+60*int(s__[1])+int(s__[2][:-1])

ls_ = open("cvl00236_7a_1_NoIMSI_2016-02-16.txt").readlines()

def plot_per_second():
	start = 0
	end = 3600*25

	c = []
	r = []
	for i in range(start, end+1):
		c.append(0)
		r.append(0)

	empty = 0
	for l in ls[1:]:
		s = get_time(l[0])
		e = s + int(float(l[1]))
		
		if int(float(l[1])) == 0:
			empty += 1
			continue

		r_ = round(int(l[9])*1.0/float(l[1]))
		for i in range(s, min(e, end) + 1):
			c[i] += 1
			r[i] += r_/1000000.0
			
	fig = plt.figure()
	ax1 = fig.add_subplot(111)    # The big subplot
	ax2 = ax1.twinx()
	print len(range(start, end+1)), len(c)
	ax1.plot(range(start, end+1), c, "b")
	ax2.plot(range(start, end+1), r, "r")
	ax1.set_xlabel("Time (s)")
	ax1.set_ylabel("# of UE")
	ax2.set_ylabel("DL bytes (MB)")
	#ax.set_ylim([-1, max_y*1.5])
	#ax.set_xlim([0, x_max*1.0/60])
	#x_tick = range(0, max(25, (x_max+60)/60), 24)
	ax1.legend(["# of UEs"], 1)
	ax2.legend(["DL bytes"], 2)
	#ax.set_xlabel("Timestamp", fontsize=20)
	fig.savefig("cdr.png")

ls = []
for l in ls_:
	ls.append(l.split("|"))
	
def plot_cdf(data, s, r = -1):
	num_bins = 10000
	counts, bin_edges = np.histogram(data, bins=num_bins)

	# Now find the cdf
	cdf = np.cumsum(counts)
	print counts
	print cdf
	print bin_edges

	# And finally plot the cdf
	fig = plt.figure()
	ax1 = fig.add_subplot(111)    # The big subplot
	y = []
	for i in range(len(cdf)):
		y.append(cdf[i]*1.0/len(data))
	ax1.plot(bin_edges[1:], y)
	if r > 0:
		ax1.set_xlim([0, r])
	
	ax1.set_xlabel(s)
	ax1.set_ylabel("CDF (1)")
	fig.savefig("cdf_%s.png"%(s))
	
plot_per_second()

d = []
for l in ls[1:]:
	if int(float(l[1])) == 0:
		continue
	d.append(int(float(l[1])))
plot_cdf(d, "session duration", 3699)

d = []
for l in ls[1:]:
	if int(float(l[1])) == 0:
		continue
	d.append(int(float(l[9])/float(l[1])))
print d
plot_cdf(d, "session-avg-req(B per s)")
