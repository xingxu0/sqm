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
	web.request("GET", "/" + fileobject, headers=headers)
	response = web.getresponse()
  # save to file |saveto|
	f = open(saveto, "w")
	f.write(response.read())
	
def request_mobile(ip="", hostname="", fileobject="", saveto="temp", extra_headers=None):
	if extra_headers == None:
		extra_headers = {}
	web = httplib.HTTPSConnection(ip)
	headers = extra_headers
	if len(hostname) > 0:
		headers["Host"] = hostname
	headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36"
	headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
	headers["accept-language"] = "en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4"
	headers["cookie"] = "GPS=1; YSC=QRncVfQ7VII; VISITOR_INFO1_LIVE=U5gxjnY8XzI; PREF=f5=30"
	#headers["accept-encoding"] = "gzip, deflate, sdch"
	headers["upgrade-insecure-requests"] = "1"
	web.request("GET", "/" + fileobject, headers=headers)
	response = web.getresponse()
  # save to file |saveto|
	#print response.msg
	print response.status
	f = open(saveto, "w")
	f.write(response.read())

def get_field(l, f):
	f += "="
	s = l.find(r"\\u0026" + f) + len(r"\\u0026" + f)
	if s == -1 + len(r"\\u0026" + f):
		s = l.find(f) + len(f)
	e = l.find(r"\\u0026", s)
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
		request_mobile(ip="m.youtube.com", fileobject=url)
		r_ = get_bitrate("temp")
		print r_
		r += r_
	return r

if __name__ == "__main__":
	random.seed()
	r = test()
	
	fig = plt.figure(figsize=(16,6))
	ax = fig.add_subplot(121)
	ax_ = fig.add_subplot(122)
	data = r
	num_bins = 1000
	counts, bin_edges = np.histogram(data, bins=num_bins)
	x = []
	for i in range(len(counts)):
		x.append(counts[i]*1.0/len(r))
	cdf = np.cumsum(x)
	ax.plot(bin_edges[1:], cdf)
	ax.set_xlabel("Bitrate (Kbps)")
	ax.grid()
	ax.set_ylabel("CDF (1)")
	ax_.plot(bin_edges[1:], cdf)
	ax_.set_xlabel("Bitrate (Kbps)")
	ax_.grid()
	ax_.set_ylabel("CDF (1)")
	ax.set_xscale("log")
	plt.tight_layout()
	plt.savefig("bitrates_mobile.png")