
import numpy

def save_arrays(filename_prefix, arrays):
    npzfile = file(filename_prefix + '.npz', 'w')
    numpy.savez(npzfile, arrays)
    npzfile.close()

def load_arrays(filename):
    npzfile = file(filename_prefix + 'npz', 'r')
    npz = numpy.load(npzfile)
    arrays = npz[npz.files[0]]
    npzfile.close()
    return arrays

