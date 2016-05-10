#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
sys.path.append("/home/xing/research/")
import plot

fig = plt.figure()
ax = fig.add_subplot(111)

w = 0.35

ind = np.arange(5)
x_stick = [0.1, 0.5, 1,5,10]
mean = [176498, 200478, 201150, 194008, 184508]
std = [19508, 20444, 19412, 18682,     18663]

ax.bar(ind - w/2, mean, 0.35, yerr=std, alpha=0.4)

#ax.errorbar(x, y, yerr=[yerr, yerr], fmt='--o')
ax.set_title('Using different requirement interval')
ax.set_xlabel("Requirement interval (s)", fontsize=plot.label_font_size)
ax.set_ylabel("DL rate (B/s)", fontsize=plot.label_font_size)

ax.set_xticks(ind)
ax.set_xticklabels(x_stick)

plot.set_plt(plt)
plot.set_ax(ax)

savefig("mean_std_req.png")
