import glob, commands, os, operator, pickle, re, copy
import matplotlib.pyplot as plt

def convert(l):
	for i in range(len(l)):
		l[i] = l[i]*8.0/59/1000/1000

def get_slowrate(s):
	s_ = s.split("_")
	return float(s_[3]), int(s_[4].split(".")[0])

def get_rate(s):
	s_ = re.split(" +", s)
	return int(s_[6])

	
ue_1 = [{}, {}]
ue_2 = [{}, {}]

fs = glob.glob("*.out")
for f in fs:
	slowrate, premium = get_slowrate(f)
	ls = open(f).readlines()
	ue_1[premium][slowrate] = get_rate(ls[0])
	ue_2[premium][slowrate] = get_rate(ls[1])
	
sorted_x = sorted(ue_1[0].items(), key=operator.itemgetter(0), reverse=True)
slowrate = []
ue_1_n = []
for x in sorted_x:
	slowrate.append(x[0])
	ue_1_n.append(x[1])
print slowrate	

sorted_x = sorted(ue_1[1].items(), key=operator.itemgetter(0), reverse=True)
slowrate = []
ue_1_p = []
for x in sorted_x:
	slowrate.append(x[0])
	ue_1_p.append(x[1])
print slowrate	

sorted_x = sorted(ue_2[0].items(), key=operator.itemgetter(0), reverse=True)
slowrate = []
ue_2_n = []
for x in sorted_x:
	slowrate.append(x[0])
	ue_2_n.append(x[1])
print slowrate

sorted_x = sorted(ue_2[1].items(), key=operator.itemgetter(0), reverse=True)
slowrate = []
ue_2_p = []
for x in sorted_x:
	slowrate.append(x[0])
	ue_2_p.append(x[1])
print slowrate

convert(ue_1_n)
convert(ue_2_n)
convert(ue_1_p)
convert(ue_2_p)

sum_n = []
sum_p = []
for i in range(len(slowrate)):
	sum_n.append(ue_1_n[i] + ue_2_n[i]*9)
	sum_p.append(ue_1_p[i] + ue_2_p[i]*9)

ax = plt.subplot()
ax.plot(slowrate, ue_1_n, "-rx", ms=10)
ax.plot(slowrate, ue_1_p, ":r", ms=10)
ax.plot(slowrate, ue_2_n, "-gx", ms=10)
ax.plot(slowrate, ue_2_p, ":g", ms=10)
ax.plot(slowrate, sum_n, "-kx", ms=10)
ax.plot(slowrate, sum_p, ":k", ms=10)


print "xxx"
print slowrate
print ue_2_n

#ax.plot([slowrate[0], slowrate[len(slowrate)-1]], [slowrate[0], slowrate[len(slowrate)-1]], "--k")
ax.set_xlabel("bottleneck (Mb/s)", fontsize=24)
ax.set_ylabel("rate (Mb/s)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)

ax.legend(["UE1 (N)", "UE1 (P)", "UE3 (N)", "UE3 (P)", "Sum (N)", "Sum (P)"], 1)
plt.tight_layout()
plt.savefig('rate_vs_bottleneck.png')

plt.clf()

for i in range(len(slowrate)):
	print "portion", ue_1_n[i]/(ue_1_n[i] + 9*ue_2_n[i])
	print "\tno premium", ue_1_n[i]+ue_2_n[i]*9
	print "\tpremium", ue_1_p[i]+ue_2_p[i]*9
	print "\tratio", ue_1_p[i]*1.0/ue_1_n[i]
	print ""	
	
x = []
y = []
y_ = []

for i in range(len(slowrate)):
	por = ue_1_n[i]/(ue_1_n[i] + 9*ue_2_n[i])
	ratio = ue_1_p[i]*1.0/ue_1_n[i]
	x.append(por)
	y.append(ratio)
	y_.append(3*1.0/(1+2*por))
ax = plt.subplot()
ax.plot(x, y, "-+b", ms=10)
ax.plot(x, y_, "--k", ms=10)
#x.text(0.15, 2.32, "y = 3 * 1/(1+2*x)",  fontsize=24)

#for i in range(len(p_u_2) - 1):
#	s = int(p_u_2[i]*100/p_u_1[i])/100.0
#	ax.text(distance[i]+500, p_u_2[i], str(s))

ax.set_xlabel("share (1)", fontsize=24)
ax.set_ylabel("rate improvement", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)

#ax.legend(["Non premium", "Premium"], 1)
plt.tight_layout()
plt.savefig('impro_vs_share.png')
	
	
