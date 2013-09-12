import numpy
import cmath
import matplotlib.pyplot as plt

def plot_admittance_magnitude(frequencies, complex_admittance):
    plt.clf()
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

    plt.clf()
    plt.plot(frequencies, complex_admittance.real, 'b', label='real')
    plt.plot(frequencies, complex_admittance.imag, 'r', label='imag')
    plt.legend(loc='upper left')
    plt.ylabel('Admittance (siemens)')
    plt.xlabel('Frequency (Hz)')

def plot_show_complex_admittance(frequencies, complex_admittance):
    plot_complex_admittance(frequencies, complex_admittance)
    plt.show()

def plot_complex_admittance_log(frequencies, complex_admittance):

    plt.clf()
    plt.loglog(frequencies, complex_admittance.real, 'b', label='real')
    plt.loglog(frequencies, complex_admittance.imag, 'r', label='imag')
    plt.legend(loc='upper left')
    plt.ylabel('Admittance (siemens)')
    plt.xlabel('Frequency (Hz)')

def plot_show_complex_admittance_log(frequencies, complex_admittance):

    plot_complex_admittance_log(frequencies, complex_admittance)
    plt.show()

def plot_combined_transducer_output_db(frequencies, complex_gain):

    gain_mag_db = numpy.array([20 * cmath.log10(cmath.polar(gain_val)[0])
        for gain_val in complex_gain])
    plt.clf()
    plt.semilogx(frequencies, gain_mag_db)
    plt.ylabel('Combined transducer gain (dB)')
    plt.xlabel('Frequency (Hz)')

