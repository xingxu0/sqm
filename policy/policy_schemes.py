import operator, copy, numpy as np, sys, math
from scipy.optimize import minimize, rosen, rosen_der

n = 6
normal_n = 30 #number of normal user
min_v = 80
bpp_mid = int((min_v+292)*0.8/2)
bpp_min = int(min_v*0.8) # bpp is bytes per prb
#bpp_max = int(292*0.8)  # this value maps to 712bits/s as TBS
bpp_max = int(500*0.8)  # this value maps to 712bits/s as TBS
total_prb = 12000*4
percentage = .3
lock_parameter = 0.10
time = 600

label = ["N","R1", "R2", "R3", "R4", "R5"]

br = [350, 700, 1200, 2400, 4800]
br_with_zero = [0] + br

handover_trigger = 0 # 120
handover_trace = [100, 90, 60, 1, 1, 150]

def get_downgrade_fraction(r, admitted_now, df_now):
	for i in range(len(admitted_now)):
		if not r[1][i] in br:
			df_now[i] += 1

def count_admitted_user(a): # user with 1 is admitted, -1 is rejected, 0 is not seen
	c = 0
	for x in a:
		if x == 1:
			c += 1
	return c

def sqm_admission(admitted, x, bpp):
	#print "sqm admission", 
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += br_with_zero[1]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
		#print "accept", x
	else:
		admitted[x] = -1
		print "sqm REJECT", x
		
def sqm_admission2(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			#t_prb += 2000*1000.0/(bpp[i]*8)#br_with_zero[-2]*1000.0/(bpp[i]*8)
			t_prb += br_with_zero[2]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm2 rejected user ", x

def sqm_admission3(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += br_with_zero[3]*1000.0/(bpp[i]*8) # br_with_zero[len(br_with_zero)/2-1]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm3 rejected user ", x
		
def paris_admission(admitted, x, bpp):
	admitted_ = 0 # number of admitted user
	admitted[x] = 1
	admitted_ = count_admitted_user(admitted)
	if total_prb*1.0*percentage/admitted_ > total_prb*(1.0-percentage)/normal_n:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "paris rejected user ", x, total_prb*1.0*percentage/admitted_, total_prb*(1.0-percentage)/normal_n

def sqm(bpp, admitted, new_user, current_premium_user, last, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	used = 0
	ret_prb = {}
	ret_rate = {}
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1), reverse=True)
	for i in range(len(sorted_bpp)):
		ret_prb[sorted_bpp[i][0]] = 0
		ret_rate[sorted_bpp[i][0]] = 0
		if admitted[sorted_bpp[i][0]] != 1:
			continue
		for j in range(len(br) - 1, -1, -1):
			need = br[j]*1000.0/(sorted_bpp[i][1]*8)
			if need <= ret_prb[sorted_bpp[i][0]]:
				break
			if used + need < available:
				ret_prb[sorted_bpp[i][0]] = need
				ret_rate[sorted_bpp[i][0]] = br[j]
				used += need
				break
	
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	# to lock it a bit to avoid fluctruation
	if False and last != []:
		if last[1] != ret_rate_:
			diff = 0
			for i in range(len(last[1])):
				diff += abs(br_with_zero.index(int(last[1][i])) - br_with_zero.index(ret_rate_[i]))
				if abs(br_with_zero.index(last[1][i]) - br_with_zero.index(ret_rate_[i])) >= len(br_with_zero)/2:
					diff += n
			if diff >= n - 1:
				# check last solution is still feasible or not
				t_prb = 0
				for i in range(len(last[1])):
					t_prb += last[1][i]*1.0/(bpp[i]*8)
				if t_prb <= available and abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_)) <lock_parameter:
					#print "\tusing last",diff, last[1], ret_rate_, abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_))
					ret_prb_ = copy.deepcopy(last[0])
					ret_rate_ = copy.deepcopy(last[1])
	print "sqm1", ret_rate
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]
	#return ret_prb_, ret_rate_, premium_allocation
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000
	return ret_prb_, ret_rate_, premium_allocation

def sqm_minimum_support(bpp, admitted, new_user, current_premium_user, last, admssion_scheme, maximum_fair):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	used = 0
	ret_prb = {}
	ret_rate = {}
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1), reverse=True)
	fairness_rate = 0
	maximum_fair_support = len(br) - 1 if maximum_fair else 0
	maximum_fair_support = 1 if maximum_fair else 0
	for j in range(maximum_fair_support, -1, -1):
		doable = True
		used = 0
		for i in range(len(sorted_bpp)):
			if admitted[sorted_bpp[i][0]] != 1:
				continue
			need = br[j]*1000.0/(sorted_bpp[i][1]*8)
			if used + need < available:
				used += need
			else:
				doable = False
		if doable == True:
			fairness_rate = j
			break
	# assign fairness_rate to everyone
	used = 0
	for i in range(len(sorted_bpp)):
		ret_prb[sorted_bpp[i][0]] = 0
		ret_rate[sorted_bpp[i][0]] = 0
		if admitted[sorted_bpp[i][0]] != 1:
			continue
		need = br[fairness_rate]*1000.0/(sorted_bpp[i][1]*8)
		if used + need < available:
			used += need
			ret_prb[sorted_bpp[i][0]] = need
			ret_rate[sorted_bpp[i][0]] = br[fairness_rate]
		else:
			ret_prb[sorted_bpp[i][0]] = 0
			ret_rate[sorted_bpp[i][0]] = 0
	# assign the rest of PRBs according to previous method
	new_available = available - used
	used = 0
	for i in range(len(sorted_bpp)):
		if admitted[sorted_bpp[i][0]] != 1:
			continue
		for j in range(len(br) - 1, -1, -1):
			need = br[j]*1000.0/(sorted_bpp[i][1]*8)
			if need <= ret_prb[sorted_bpp[i][0]]:
				break
			if used + need - ret_prb[sorted_bpp[i][0]] < new_available:
				used += need - ret_prb[sorted_bpp[i][0]]
				ret_prb[sorted_bpp[i][0]] = need
				ret_rate[sorted_bpp[i][0]] = br[j]
				break
	
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	# to lock it a bit to avoid fluctruation
	if last != []:
		if last[1] != ret_rate_:
			diff = 0
			for i in range(len(last[1])):
				diff += abs(br_with_zero.index(int(last[1][i])) - br_with_zero.index(ret_rate_[i]))
				if abs(br_with_zero.index(last[1][i]) - br_with_zero.index(ret_rate_[i])) >= len(br_with_zero)/2:
					diff += n
			if diff >= n - 1:
				# check last solution is still feasible or not
				t_prb = 0
				for i in range(len(last[1])):
					t_prb += last[1][i]*1.0/(bpp[i]*8)
				if t_prb <= available and abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_)) <lock_parameter:
					#print "\tusing last",diff, last[1], ret_rate_, abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_))
					ret_prb_ = copy.deepcopy(last[0])
					ret_rate_ = copy.deepcopy(last[1])
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]
	#return ret_prb_, ret_rate_, premium_allocation
	non_premium = 0
	allocated_prb = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			allocated_prb += ret_prb_[i]
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	# give extra to any premium user
	extra = available - allocated_prb
	#print "sqm3 wasted", extra, "out of ", available, "total resources"
	#extra = 0 # don't use extra
	if extra > 0: #*1.0/available > 0.05:
		min_rate, min_user = sys.maxint, 0
		for i in range(len(admitted)):
			if admitted[i] == 1:
				if ret_rate_[i] != 0 and ret_rate_[i] < min_rate:
					min_rate = ret_rate_[i]
					min_user = i
		ret_prb_[min_user] += extra
		ret_rate_[min_user] = ret_prb_[min_user]*bpp[min_user]*8/1000
				
	#print extra, available, non_premium
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000
	return ret_prb_, ret_rate_, premium_allocation

def paris(bpp, admitted, new_user, current_premium_user, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	ret_prb = {}
	ret_rate = {}
	admitted_ = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			admitted_ += 1
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = available/admitted_
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
		ret_rate[i] = temp_rate
	
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000		
	return ret_prb_, ret_rate_
""" original paris2, where I allocate resources, but when I don't have enough (diff is positive), I don't do anything.
def paris2(bpp, admitted, new_user, current_premium_user, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	ret_prb = {}
	ret_rate = {}
	admitted_ = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			admitted_ += 1
	diff = 0 # extra PRBs used
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = available/admitted_
		#need = br[j]*1000.0/(sorted_bpp[i][1]*8)
		close_j, close_v = 0, sys.maxint
		for j in range(len(br_with_zero)):
			t_prb = br_with_zero[j]*1000.0/(bpp[i]*8)
			if abs(t_prb - ret_prb[i]) < close_v:
				close_v = abs(t_prb - ret_prb[i])
				close_j = j
		diff += br_with_zero[close_j]*1000.0/(bpp[i]*8) - ret_prb[i]
		ret_prb[i] = br_with_zero[close_j]*1000.0/(bpp[i]*8)
		ret_rate[i] = br_with_zero[close_j]
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
	if int(diff) > 0:
		print "paris2 diff %d out of %d"%(diff, available)
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000		
	return ret_prb_, ret_rate_
"""

alpha = 0.1
def utility(a, b, c):
	return (math.log(a) if a > 0 else 0) - alpha*abs(a/1000.0-b/1000.0)*c

c = []
r = []
s = []
ava = 0
def f(xs):
	global r
	ret = 0
	for i in range(len(xs)):
		x = xs[i]
		ret += (math.log(x) if x > 1 else 0) - 0.1*(math.sqrt(pow(x - r[i], 2)) + 1)*s[i]
	return -ret

def con_fun(xs):
	global c, ava
	ret = 0
	for i in range(len(xs)):
		ret += xs[i]*1000.0/(c[i]*8)
	return ava - ret

def get_low(x):
	for i in range(len(br_with_zero)):
		if br_with_zero[i] > x: break
	return max(0, i - 1)

def paris3(bpp, admitted, new_user, current_premium_user, last, admssion_scheme, result):
	global s, r, c, ava
	#print "paris3 round starts"
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
		
	available = int(round(total_prb*percentage))
	ava = available
	
	c[:] = []
	r[:] = []
	rr = []
	bnds = []
	s[:] = []
	for i in range(len(admitted)):
		if admitted[i] == 1:
			c.append(bpp[i])
			rr.append(4800)
			if len(result):
				r.append(result[-1][1][i])
			else:
				r.append(4800)
			bnds.append((br_with_zero[0], br_with_zero[-1]))
			switch = 0
			temp = 0
			for ii in range(len(result) - 2, -1, -1):
				temp += 1
				if result[ii][1][i] != result[ii + 1][1][i]:
					switch += 1
				if temp == 30: break
			s.append(switch)
	cons = ({'type': 'ineq', 'fun': con_fun})
	#print r, bnds, cons
	res = minimize(f, rr, args=(), method="SLSQP", bounds=bnds, constraints=cons)#, tol=1e-6, options={'disp': True ,'ftol':1e-6, 'eps' : 0.001})
	print "paris3 0", r
	ttt = []
	for xx in res["x"]: ttt.append(int(xx))
	print "paris3 0", ttt
	print " "
	
	ret_prb = {}
	ret_rate = {}
	t = 0
	s = []
	used = 0
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		low = get_low(res["x"][t])
		t += 1
		ret_rate[i] = br_with_zero[low]
		ret_prb[i] = ret_rate[i]*1000.0/(bpp[i]*8)
		used += ret_prb[i]
		ext = ((br_with_zero[low + 1] if low + 1 < len(br_with_zero) else sys.maxint)- br_with_zero[low])*1000.0/(bpp[i]*8)
		s.append((ext, i))
		
	#print "paris3 1", ret_rate, used, available
	s_ = sorted(s)
	for i in range(len(s_)):
		if s_[i][0] + used < available:
			used += s_[i][0]
			ii = s_[i][1]
			ind = br_with_zero.index(ret_rate[ii])
			if ind + 1 < len(br_with_zero):
				ret_rate[ii] = br_with_zero[ind + 1]
				ret_prb[ii] = ret_rate[ii]*1000.0/(bpp[ii]*8)
				#print "\t upgrade", ii, "used", s_[i][0], "from", br_with_zero[ind], "to", br_with_zero[ind + 1]
		else:
			break
	# below dynamic to find optimal
	"""
	v = [[0 for i in range(available)] for j in range(len(admitted))]
	v_r = [[{} for i in range(available)] for j in range(len(admitted))]
	for i in range(len(admitted)):
		for j in range(available):
			if admitted[i] != 1: 
				if i:
					v[i][j] = v[i - 1][j]
					v_r[i][j] = copy.deepcopy(v_r[i - 1][j])
				continue
			if j:
				v[i][j] = v[i][j - 1]
				v_r[i][j] = copy.deepcopy(v_r[i][j - 1])
			for k in range(len(br_with_zero)):
				p = br_with_zero[k]*1000.0/(bpp[i]*8)
				temp = 0
				switch = 0
				for ii in range(len(result) - 2, -1, -1):
					temp += 1
					if result[ii][1][i] != result[ii + 1][1][i]:
						switch += 1
					if temp == 30: break
				u = utility(br_with_zero[k], last[1][i] if last != [] else br_with_zero[k], switch)
				if i:
					if p <= j and v[i - 1][j - int(round(p))] + u > v[i][j]:
						v[i][j] = v[i - 1][j - int(round(p))] + u
						v_r[i][j] = copy.deepcopy(v_r[i - 1][j - int(round(p))])
						v_r[i][j][i] = br_with_zero[k]
				else:
					if p <= j:
						v[i][j] = u
						v_r[i][j][i] = br_with_zero[k]
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_rate[i] = v_r[len(admitted) - 1][available - 1][i] if i in v_r[len(admitted) - 1][available - 1] else 0
		ret_prb[i] = ret_rate[i]*1000.0/(bpp[i]*8)
	"""
	
	#print "paris3 2", ret_rate, used, available
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]	
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000		
	return ret_prb_, ret_rate_, premium_allocation

# below paris3_previous is changed on 08/07
def paris3_previous(bpp, admitted, new_user, current_premium_user, last, admssion_scheme):
	#print "paris3 round starts"
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1)) # users sorted by channel quality, 1st user is with the worst channel
	ret_prb = {}
	ret_rate = {}
	admitted_ = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			admitted_ += 1
	diff = 0 # extra PRBs used
	
	# try R2 first
	total_prb_r1 = 0
	total_prb_r2 = 0
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = available/admitted_
		#need = br[j]*1000.0/(sorted_bpp[i][1]*8)
		close_j, close_v = 0, sys.maxint
		#for j in range(1, len(br)):  # try R2 first
		total_prb_r2 += br[1]*1000.0/(bpp[i]*8)
		total_prb_r1 += br[0]*1000.0/(bpp[i]*8)
	used = 0
	
	downgrade = False # downgrade or upgrade
	if total_prb_r1 >= available:
		common_j = 0 # R1
		downgrade = True
		used = total_prb_r1
	elif available >= total_prb_r2:
		common_j = 1 # R2
		downgrade = False
		used = total_prb_r2
	elif available - total_prb_r1 < total_prb_r2 - available:
		common_j = 0
		downgrade = False
		used = total_prb_r1
	else:
		common_j = 1
		downgrade = True
		used = total_prb_r2
		
	# check if current solution consistant with "last"
	last_min, last_max = sys.maxint, -sys.maxint
	if last != []:
		for i in range(len(last[1])):
			last_min = min(last_min, br_with_zero.index(last[1][i]) - 1)
			last_max = max(last_max, br_with_zero.index(last[1][i]) - 1)
	print "consistent?", last_min, last_max, common_j, downgrade
	if False: #(last_min == common_j and downgrade == False) or (last_max == common_j and downgrade == True):
		print "consistant with last"
		used = 0
		for i in range(len(last[1])):
			ret_prb[i] = 0
			ret_rate[i] = 0
			if admitted[i] != 1:
				continue
			ret_rate[i] = last[1][i]
			ret_prb[i] = ret_rate[i]*1000.0/(bpp[i]*8)
			used += last[1][i]*1000.0/(bpp[i]*8)
		if used <= available:
			downgrade = False
		else:
			downgrade = True
	else:
		for i in range(len(bpp)):
			ret_prb[i] = 0
			ret_rate[i] = 0
			if admitted[i] != 1:
				continue
			ret_prb[i] = br[common_j]*1000.0/(bpp[i]*8)
			ret_rate[i] = br[common_j]
	
	if downgrade:
		diff = used - available
		while int(diff) > 0:
			print "\tparis3 downgrade from rate", common_j, "with", diff
			min_degrade, min_user = sys.maxint, -1
			for ii in range(len(sorted_bpp)):
				i = sorted_bpp[ii][0]
				if ret_prb[i] > available/admitted_:
					new_rate = br_with_zero[br_with_zero.index(ret_rate[i]) - 1]
					#if new_rate == 0: continue
					min_user = i
					print "\t\t user %d downgrade 1 level from rate %d to rate %d save %d PRBs (PRBs from %d to %d) (now diff %d)"%(min_user, ret_rate[min_user], new_rate, (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)), ret_prb[min_user],  new_rate*1000.0/(bpp[min_user]*8), diff - (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)))
					ret_rate[min_user] = new_rate
					diff = diff - (ret_prb[min_user] - ret_rate[min_user]*1000.0/(bpp[min_user]*8))
					ret_prb[min_user] = ret_rate[min_user]*1000.0/(bpp[min_user]*8)
					break
	else:
		print "\tparis3 upgrade from rate", common_j, "with", available - used
		new_available = available - used
		diff = new_available
		if new_available*1.0/available < 0.05:
			used = available
		for i in range(len(sorted_bpp) - 1, -1, -1):
			ii = sorted_bpp[i][0]
			if admitted[sorted_bpp[i][0]] != 1:
				continue
			for j in range(len(br) - 1, -1, -1):
				need = br[j]*1000.0/(sorted_bpp[i][1]*8)
				if need <= ret_prb[sorted_bpp[i][0]]: break
				if used + need - ret_prb[sorted_bpp[i][0]] < available:
					print "\t\t user %d upgrade 1 level from rate %d to rate %d use %d PRBs (PRBs from %d to %d) (now diff %d)"%(ii, ret_rate[ii], br[j], (-ret_prb[ii] +  br[j]*1000.0/(bpp[ii]*8)), ret_prb[ii],  br[j]*1000.0/(bpp[ii]*8), diff - (-ret_prb[ii] + br[j]*1000.0/(bpp[ii]*8)))
					used += need - ret_prb[sorted_bpp[i][0]]
					diff -= need - ret_prb[sorted_bpp[i][0]]
					ret_prb[sorted_bpp[i][0]] = need
					ret_rate[sorted_bpp[i][0]] = br[j]					
					break	
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]
	
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000		
	return ret_prb_, ret_rate_, premium_allocation


def paris2(bpp, admitted, new_user, current_premium_user, last, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				if admssion_scheme == 1:
					sqm_admission(admitted, i, bpp)
				elif admssion_scheme == 2:
					sqm_admission2(admitted, i, bpp)
				elif admssion_scheme == 3:
					sqm_admission3(admitted, i, bpp)
				else:
					paris_admission(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1)) # users sorted by channel quality, 1st user is with the worst channel
	ret_prb = {}
	ret_rate = {}
	admitted_ = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			admitted_ += 1
	diff = 0 # extra PRBs used
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = available/admitted_
		#need = br[j]*1000.0/(sorted_bpp[i][1]*8)
		close_j, close_v = 0, sys.maxint
		for j in range(1, len(br_with_zero)):
			if j == 1: continue # not using R1 at the first time
			t_prb = br_with_zero[j]*1000.0/(bpp[i]*8)
			if abs(t_prb - ret_prb[i]) < close_v:
				close_v = abs(t_prb - ret_prb[i])
				close_j = j
		diff += br_with_zero[close_j]*1000.0/(bpp[i]*8) - ret_prb[i]
		ret_prb[i] = br_with_zero[close_j]*1000.0/(bpp[i]*8)
		ret_rate[i] = br_with_zero[close_j]
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
	#if int(diff) > 0:
		#print "paris3 diff %d out of %d"%(diff, available)
		
	# first downgrade from R2 to R1 (for users who used more then the fair share)
	while int(diff) > 0:
		min_degrade, min_user = sys.maxint, -1
		for ii in range(len(sorted_bpp)):
			i = sorted_bpp[ii][0]
			if ret_prb[i] > available/admitted_ and ret_rate[i] >= br[1]:
				min_user = i
				new_rate = br_with_zero[br_with_zero.index(ret_rate[min_user]) - 1]
				#print "\t user %d downgrade 1 level from rate %d to rate %d save %d PRBs (PRBs from %d to %d) (now diff %d)"%(min_user, ret_rate[min_user], new_rate, (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)), ret_prb[min_user],  new_rate*1000.0/(bpp[min_user]*8), diff - (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)))
				ret_rate[min_user] = new_rate
				diff = diff - (ret_prb[min_user] - ret_rate[min_user]*1000.0/(bpp[min_user]*8))
				ret_prb[min_user] = ret_rate[min_user]*1000.0/(bpp[min_user]*8)
				break
		if min_user == -1: break
		#print "paris2 downgrade level1"
		
	# then downgrade from R2 to R1 (for all the users)
	while int(diff) > 0:
		min_degrade, min_user = sys.maxint, -1
		for ii in range(len(sorted_bpp)):
			i = sorted_bpp[ii][0]
			if ret_rate[i] >= br[1]:
				min_user = i
				new_rate = br_with_zero[br_with_zero.index(ret_rate[min_user]) - 1]
				#print "\t user %d downgrade 1 level from rate %d to rate %d save %d PRBs (PRBs from %d to %d) (now diff %d)"%(min_user, ret_rate[min_user], new_rate, (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)), ret_prb[min_user],  new_rate*1000.0/(bpp[min_user]*8), diff - (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)))
				ret_rate[min_user] = new_rate
				diff = diff - (ret_prb[min_user] - ret_rate[min_user]*1000.0/(bpp[min_user]*8))
				ret_prb[min_user] = ret_rate[min_user]*1000.0/(bpp[min_user]*8)
				break
		if min_user == -1: break
		#print "paris2 downgrade level1"
	
	# lastly downgrade from R1 to R0 (for users who used more then the fair share)
	while int(diff) > 0:
		min_degrade, min_user = sys.maxint, -1
		for ii in range(len(sorted_bpp)):
			i = sorted_bpp[ii][0]
			if ret_prb[i] > available/admitted_ and ret_rate[i] == br[0]:
				min_user = i
				new_rate = br_with_zero[br_with_zero.index(ret_rate[min_user]) - 1]
				#print "\t user %d downgrade 1 level from rate %d to rate %d save %d PRBs (PRBs from %d to %d) (now diff %d)"%(min_user, ret_rate[min_user], new_rate, (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)), ret_prb[min_user],  new_rate*1000.0/(bpp[min_user]*8), diff - (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)))
				ret_rate[min_user] = new_rate
				diff = diff - (ret_prb[min_user] - ret_rate[min_user]*1000.0/(bpp[min_user]*8))
				ret_prb[min_user] = ret_rate[min_user]*1000.0/(bpp[min_user]*8)
				break
		if min_user == -1: break
		#print "paris2 downgrade level1"
	
	# lastly downgrade from R1 to R0 (for all the users)
	while int(diff) > 0:
		min_degrade, min_user = sys.maxint, -1
		for ii in range(len(sorted_bpp)):
			i = sorted_bpp[ii][0]
			if ret_rate[i] == br[0]:
				min_user = i
				new_rate = br_with_zero[br_with_zero.index(ret_rate[min_user]) - 1]
				#print "\t user %d downgrade 1 level from rate %d to rate %d save %d PRBs (PRBs from %d to %d) (now diff %d)"%(min_user, ret_rate[min_user], new_rate, (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)), ret_prb[min_user],  new_rate*1000.0/(bpp[min_user]*8), diff - (ret_prb[min_user] - new_rate*1000.0/(bpp[min_user]*8)))
				ret_rate[min_user] = new_rate
				diff = diff - (ret_prb[min_user] - ret_rate[min_user]*1000.0/(bpp[min_user]*8))
				ret_prb[min_user] = ret_rate[min_user]*1000.0/(bpp[min_user]*8)
				break
		if min_user == -1: break
		#print "paris2 downgrade level1"
		
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
		
	if last != []:
		if last[1] != ret_rate_:
			if True:
				# check last solution is still feasible or not
				t_prb = 0
				for i in range(len(last[1])):
					t_prb += last[1][i]*1.0/(bpp[i]*8)
				if t_prb <= available and abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_)) <lock_parameter:
					#print "\tusing last",diff, last[1], ret_rate_, abs((np.mean(ret_rate_) - np.mean(last[1]))/np.mean(ret_rate_))
					ret_prb_ = copy.deepcopy(last[0])
					ret_rate_ = copy.deepcopy(last[1])		
	premium_allocation = [copy.deepcopy(ret_prb_), copy.deepcopy(ret_rate_)]
	non_premium = 0
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
		elif admitted[i] == -1:
			non_premium += 1
	for i in range(len(admitted)):
		if (admitted[i] == 1 and ret_prb_[i] == 0) or admitted[i] == -1:
			ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
			ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000		
	return ret_prb_, ret_rate_, premium_allocation



def now(bpp, admitted, new_user, current_premium_user, admssion_scheme):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
				admitted[i] = 1
				new_user -= 1
	ret_prb = {}
	ret_rate = {}
	for i in range(len(bpp)):
		ret_prb[i] = 0
		ret_rate[i] = 0
		if admitted[i] != 1:
			continue
		ret_prb[i] = total_prb/(normal_n + current_premium_user)
		#print total_prb, normal_n, current_premium_user, total_prb/(normal_n + current_premium_user)
		temp_rate = ret_prb[i]*bpp[i]*8/1000
		# stair
		#j = 0
		#while j < len(br) and br[j] <= temp_rate:
		#	j += 1
		#ret_rate[i] = br[j - 1] if j - 1 >= 0 else 0
		ret_rate[i] = temp_rate
	ret_prb_ = []
	ret_rate_ = []
	for i in range(len(bpp)):
		ret_prb_.append(ret_prb[i])
		ret_rate_.append(ret_rate[i])
	return ret_prb_, ret_rate_
