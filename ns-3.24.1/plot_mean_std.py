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

ind = np.arange(6)
x_stick = [0.05, 0.1, 0.3, 0.5, 0.8, 1]
mean = [201172, 201150, 199312,197468, 195494,194030]
std = [18053, 19412, 23229,25858,25982,27470]

ax.bar(ind - w/2, mean, 0.35, yerr=std, alpha=0.4)

#ax.errorbar(x, y, yerr=[yerr, yerr], fmt='--o')
ax.set_title('Using different MCS interval')
ax.set_xlabel("MCS interval (s)", fontsize=plot.label_font_size)
ax.set_ylabel("DL rate (B/s)", fontsize=plot.label_font_size)

ax.set_xticks(ind)
ax.set_xticklabels(x_stick)

plot.set_plt(plt)
plot.set_ax(ax)

savefig("mean_std.png")
