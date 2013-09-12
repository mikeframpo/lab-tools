
import matplotlib.pyplot as plt
import numpy as np

def plot_separaton_uncertainty(ax, d_t):
    d_s = 0.001
    v = 5000

    num_pts = 1000
    s_min = 0.1
    s_max = 2.0

    s = np.linspace(s_min, s_max, num_pts)
    d_v = np.zeros(len(s))

    for i_s in range(len(s)):
        tau = s[i_s] / v
        d_v[i_s] = ( (d_s * tau) + (d_t * s[i_s]) ) / (tau ** 2)

    ax.plot(s, d_v, label='dt={0} s'.format(d_t))

fig, ax = plt.subplots()

plot_separaton_uncertainty(ax, 1e-6)
plot_separaton_uncertainty(ax, 5e-6)
plot_separaton_uncertainty(ax, 10e-6)

#fig.xlabel('Separation (meters)')
#fig.ylabel('Velocity Uncertainty (m/s')

ax.legend('upper right')

plt.show()


