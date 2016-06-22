import operator, copy, numpy as np

n = 6
normal_n = 30 #number of normal user
bpp_mid = int((135+292)*0.8/2)
bpp_min = int(135*0.8) # bpp is bytes per prb
bpp_max = int(292*0.8)  # this value maps to 712bits/s as TBS
total_prb = 12000*4
percentage = .3
lock_parameter = 0 #0.3
time = 600

label = ["N","R1", "R2", "R3", "R4", "R5"]

br = [350, 700, 1200, 2400, 4800]
#br = [350, 700, 1200, 2400]
br_with_zero = [0] + br

def count_admitted_user(a): # user with 1 is admitted, -1 is rejected, 0 is not seen
	c = 0
	for x in a:
		if x == 1:
			c += 1
	return c

def sqm_admission(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += br_with_zero[1]*1000.0/(bpp[i]*8)
	if t_prb <= total_prb*percentage:
		admitted[x] = 1
	else:
		admitted[x] = -1
		print "sqm rejected user ", x
		
def sqm_admission2(admitted, x, bpp):
	t_prb = 0
	admitted[x] = 1
	for i in range(x + 1):
		if admitted[i] == 1:
			t_prb += 2000*1000.0/(bpp[i]*8)#br_with_zero[-2]*1000.0/(bpp[i]*8)
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
			t_prb +=1000*1000.0/(bpp[i]*8) # br_with_zero[len(br_with_zero)/2-1]*1000.0/(bpp[i]*8)
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
				else:
					sqm_admission3(admitted, i, bpp)
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
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
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
				else:
					sqm_admission3(admitted, i, bpp)
				new_user -= 1
	available = total_prb*percentage
	used = 0
	ret_prb = {}
	ret_rate = {}
	sorted_bpp = sorted(bpp.items(), key=operator.itemgetter(1), reverse=True)
	fairness_rate = 0
	maximum_fair_support = len(br) - 1 if maximum_fair else 0
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
	print fairness_rate, available, used
	# assign fairness_rate to everyone
	used = 0
	for i in range(len(sorted_bpp)):
		if admitted[sorted_bpp[i][0]] != 1:
			continue
		need = br[fairness_rate]*1000.0/(sorted_bpp[i][1]*8)
		if used + need < available:
			used += need
			ret_prb[sorted_bpp[i][0]] = need
			ret_rate[sorted_bpp[i][0]] = br[fairness_rate]
	# assign the rest of PRBs according to previous method
	available -= used
	print available
	used = 0
	for i in range(len(sorted_bpp)):
		if admitted[sorted_bpp[i][0]] != 1:
			continue
		for j in range(len(br) - 1, -1, -1):
			need = br[j]*1000.0/(sorted_bpp[i][1]*8)
			if used + need - ret_prb[sorted_bpp[i][0]] < available:
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
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				non_premium += 1
	for i in range(len(admitted)):
		if admitted[i] == 1:
			if ret_prb_[i] == 0:
				ret_prb_[i] = total_prb*(1-percentage)*1.0/(non_premium+normal_n)
				ret_rate_[i] = ret_prb_[i]*bpp[i]*8/1000
	return ret_prb_, ret_rate_, premium_allocation



def paris(bpp, admitted, new_user, current_premium_user):
	if new_user:
		for i in range(len(admitted)):
			if admitted[i] == 0 and new_user:
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
	return ret_prb_, ret_rate_

def now(bpp, admitted, new_user, current_premium_user):
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
