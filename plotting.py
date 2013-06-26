import numpy
import cmath
import matplotlib.pyplot as plt

def plot_admittance_magnitude(filename, frequencies, complex_admittance):
    
    y_mag_ms = numpy.array([cmath.polar(y_val)[0] * 1000
                            for y_val in complex_admittance])
    freq_khz = numpy.array([f/1000 for f in frequencies])
    plt.plot(freq_khz, y_mag_ms)
    plt.ylabel('Admittance (millisiemens)')
    plt.xlabel('Frequency (kHz)')
    plt.savefig(filename)

