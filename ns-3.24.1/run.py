import os

cs = open("run_commands.cfg").readlines()

for c in cs:
	c_ = c[:-1].split("|")
	if c_[0][0] == "#":
		continue
	c_[0] = "run_gen_" + c_[0]
	os.system("mkdir " + c_[0])
	print c_[1] + " > %s/out.txt 2>&1"%(c_[0])
	os.system(c_[1] + " > %s/out.txt 2>&1"%(c_[0]))
	os.system("cp *.txt " + c_[0] + "/")
	os.system("cp *.pcap " + c_[0] + "/")

