e = 4922482

t = e*10
for x in range(0, 90, 5):
	o = x*e*1.0/85
	m = t - o*9
	print x, m*1.0/t
	
