
import numpy
import cmath

def save_arrays(filename, frequencies, y_vals):
    npzfile = file(filename, 'w')
    numpy.savez(npzfile, freq=frequencies, y=y_vals)
    npzfile.close()

def load_arrays(filename):
    npzfile = file(filename, 'r')
    npz = numpy.load(npzfile)
    arrays = [npz['freq'], npz['y']]
    npzfile.close()
    return arrays

def mag_phase_to_complex(mag, phase_degrees):
    return cmath.rect(mag, (cmath.pi/180) * phase_degrees)

