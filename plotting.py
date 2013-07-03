import numpy
import cmath
import matplotlib.pyplot as plt

def plot_admittance_magnitude(frequencies, complex_admittance):
    y_mag_ms = numpy.array([cmath.polar(y_val)[0] * 1000
                            for y_val in complex_admittance])
    freq_khz = numpy.array([f/1000 for f in frequencies])
    plt.plot(freq_khz, y_mag_ms)
    plt.ylabel('Admittance (millisiemens)')
    plt.xlabel('Frequency (kHz)')

def plot_show_admittance_magnitude(frequencies, complex_admittance):
    plot_admittance_magnitude(frequencies, complex_admittance)
    plt.show()

def plot_complex_admittance(frequencies, complex_admittance):

    plt.plot(frequencies, complex_admittance.real, 'b',
            frequencies, complex_admittance.imag, 'r')
    plt.legend('Real', 'Imaginary', loc='upper left')
    plt.ylabel('Admittance (siemens)')
    plt.ylabel('Frequency (Hz)')

def plot_show_complex_admittance(frequencies, complex_admittance):
    plot_complex_admittance(frequencies, complex_admittance)
    plt.show()

