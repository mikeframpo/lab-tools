
import numpy as np
import math
import matplotlib.pyplot as plt

def gen_cos_wave_analogue(f, delay_seconds, f_s, time):
    F = f / f_s
    samples = int(f_s * time)
    delay_samples = int(f_s * delay_seconds)
    (t, s) = gen_cos_wave_digital(F, samples, delay_samples)
    time = t
    return (time, s)

def gen_cos_wave_digital(F, samples, delay_samples):
    t = np.array(range(samples))
    s = np.cos(2 * np.pi * F * (t - delay_samples))
    return (t, s)

def sum_cos_waves(f_start, f_end, num_freqs, delay_seconds, f_s, total_time):
    freqs = np.linspace(f_start, f_end, num_freqs)
    cos_sum = None
    time = None
    for freq in freqs:
        (t, s) = gen_cos_wave_analogue(freq, delay_seconds, f_s, total_time)
        if cos_sum is None:
            time = t
            cos_sum = s
        else:
            cos_sum += s
    return (time, cos_sum)

def hamming_filter(s, N):
    hamm = np.hamming(N)
    out = np.convolve(s, hamm, 'same')
    return out

(t, s) = sum_cos_waves(10e3, 40e3, 10, 200e-6, 375e3, 400e-6)
windowed = hamming_filter(s, 20)

plt.clf()
plt.plot(t, s, 'b-')
plt.plot(t, windowed, 'r-')
plt.show()
