# PEP
import httplib, os, string, random, time, socket, subprocess, itertools, numpy as np
from multiprocessing import Process
import matplotlib.pyplot as plt

def request(ip="", hostname="", fileobject="", saveto="temp", extra_headers=None):
	if extra_headers == None:
		extra_headers = {}
	web = httplib.HTTPSConnection(ip)
	headers = extra_headers
	if len(hostname) > 0:
		headers["Host"] = hostname
	#headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 4.2; Nexus 7 Build/JOP40C) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19"
	web.request("GET", "/" + fileobject, headers=headers)
	response = web.getresponse()
  # save to file |saveto|
	f = open(saveto, "w")
	f.write(response.read())

def get_field(l, f):
	f += "="
	s = l.find("\u0026" + f) + len("\u0026" + f)
	if s == -1 + len("\u0026" + f):
		s = l.find(f) + len(f)
	e = l.find("\u0026", s)
	return l[s:e if e != -1 else None]

def get_bitrate(f):
	r = []
	for l in open(f).readlines():
		if l.find("bitrate") == -1:
			continue
		xs = l.split(",")
		for x in xs:
			if x.find("bitrate") != -1:
				t = get_field(x, "type")
				if t.find("video") != -1 and t.find("mp4") != -1:
					r.append(int(get_field(x, "bitrate"))*1.0/1000)
	return r

def test():
	urls = {}
	request(ip="www.youtube.com")
	lines = open("temp").readlines()
	for l in lines:
		s = l.find("watch?")
		if s != -1:
			e = l.find("\"", s + 1)
			urls[l[s:e]] = 0

	if len(urls) == 0:
		print "Youtube is not responding, please retry"
		exit()
	ips = {}
	f = 0
	r = []
	for url in urls:
		print url,
		request(ip="www.youtube.com", fileobject=url)
		r_ = get_bitrate("temp")
		print r_, "!!!!!!" if max(r_) > 22000 else ""
		r += r_
	return r

if __name__ == "__main__":
	random.seed()
	r = test()
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	print len(r)
	data = r
	num_bins = 1000
	counts, bin_edges = np.histogram(data, bins=num_bins)
	x = []
	for i in range(len(counts)):
		print counts[i],
		x.append(counts[i]*1.0/len(r))
	cdf = np.cumsum(x)
	#print cdf
	#print counts
	#print bin_edges
	ax.plot(bin_edges[1:], cdf)
	ax.set_xlabel("Bitrate (Kbps)")
	ax.grid()
	ax.set_ylabel("CDF (1)")
	#ax.set_xscale("log")
	plt.tight_layout()
	plt.savefig("bitrates.png")
