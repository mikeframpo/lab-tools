import numpy
import scipy.signal as sig

def moving_average(a, m1, m2):
    a_padded = numpy.pad(a, (m1 + 1, m2), 'constant')
    cumsum = numpy.cumsum(a_padded, dtype=float)
    return (cumsum[(m2 + m1 + 1):] - cumsum[:-(m2 + m1 + 1)])/(m2 + m1 + 1)

def findpeaks(data, ma_len, ampl_threshold):
    # Basic strategy taken from:
    # http://terpconnect.umd.edu/~toh/spectrum/PeakFindingandMeasurement.htm
    diff = numpy.diff(data)
    diff_filt = moving_average(diff, ma_len, ma_len)

    peaks = []
    for i,deriv in enumerate(diff_filt):
        if i > 0:
            if diff_filt[i-1] > 0 and diff_filt[i] < 0:
                if ampl_threshold != None and data[i] > ampl_threshold:
                    peaks.append(i)
    return peaks

def filter_dc_level(data, taps, cutoff):
    taps = sig.firwin(taps, cutoff, pass_zero=False)
    data_filtered = sig.lfilter(taps, 1.0, data)
    return data_filtered

if __name__ == '__main__':
    import utils
    import matplotlib.pyplot as plt
    arrays = utils.load_arrays('probe1_10000pt_1av.npz')
    peaks = findpeaks(arrays[1].real, 10, 3e-5)
    peak_freq = [arrays[0][i_freq] for i_freq in peaks]
    peak_ampl = [arrays[1].real[i_freq] for i_freq in peaks]

    plt.plot(arrays[0], arrays[1].real, 'b-', peak_freq, peak_ampl, 'ro')
    plt.show()

