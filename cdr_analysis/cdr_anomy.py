import matplotlib
matplotlib.use('Agg')
import glob, os, sys, re, math, operator
import matplotlib.pyplot as plt
import numpy as np
import copy

def get_time(s):
	s_ = s.split("@")[1]
	s__ = s_.split(":")
	return 3600*int(s__[0])+60*int(s__[1])+int(s__[2][:-1])

ls_ = open("cvl00236_7a_1_Anonymized_2016-02-15.txt").readlines()

def plot_per_second(data):
	start = 0
	end = 3600*25

	c = []
	r = []
	for i in range(start, end+1):
		c.append(0)
		r.append(0)

	empty = 0
	for l in data:
		for x in data[l]:
			s = x
			e = s + data[l][x][0]
			
			r_ = round(data[l][x][1]*1.0/(e-s))
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

ls = []
for l in ls_:
	ls.append(l.split("|"))

data = {}
empty = 0
con = 0
for l in ls[1:]:
	s = get_time(l[0])
	d = int(float(l[1]))
	if d == 3600:
		con += 1
	if d == 0:
		empty += 1
		continue
		
	i = l[9]
	b = int(l[11])
	if not i in data:
		data[i] = {}
	data[i][s] = [d, b]

t_s = 0
o_s = 0
print "UE number:", len(data)
for i in data:
	s_ = sorted(data[i].items(), key=operator.itemgetter(0))
	t_s += len(s_)
	for x in range(len(s_) - 1):
		if s_[x+1][0] < s_[x][0] + s_[x][1][0]:
			o_s += 1

	over = False
	wrong_chop = False

	n = 0
	while n < len(s_) - 1:
		if s_[n][0] + s_[n][1][0] == s_[n + 1][0]:
			#print "b", s_[n], s_[n+1]
			s_[n][1][0] += s_[n + 1][1][0]
			s_[n][1][1] += s_[n + 1][1][1]
			del s_[n + 1]
			#print "a", s_[n]
		else:
			if int(s_[n][1][0] ) % 3600 == 0:
				#print i, s_[n][0], s_[n][1][0], s_[n+1][0],
				if s_[n+1][0] < s_[n][0] + s_[n][1][0]:
					over = True
				else:
					wrong_chop = True
			n += 1
	
	data[i] = {}
	for j in range(len(s_)):
		data[i][s_[j][0]] = s_[j][1]
	if over:
		print "overlap session", i, ":",
		for j in range(len(s_)):
			print "[", s_[j][0], ",", s_[j][0] + s_[j][1][0], "]",
		print ""
	if wrong_chop:
		print "wrong chopping ", i, ":",
		for j in range(len(s_)):
			print "[", s_[j][0], ",", s_[j][0] + s_[j][1][0], "(", s_[j][1][0],")","]",
		print ""

	

print o_s, t_s, o_s*1.0/t_s

con2 = 0
for i in data:
	for x in data[i]:
		if data[i][x][0] == 3600:
			con2 += 1

print con, con2

plot_per_second(data)

d = []
for l in data:
	for x in data[l]:
		d.append(data[l][x][0])
plot_cdf(d, "session duration (s)", 3699)

d = []
for l in data:
	for x in data[l]:
		d.append(data[l][x][1])
plot_cdf(d, "session volume (B)", 1e7)
print min(d)

d = []
for l in data:
	for x in data[l]:
		d.append(data[l][x][1]*1.0/data[l][x][0])
plot_cdf(d, "requirement (B per s)", 1e5)
