import time
import numpy
import cmath
import sys

import visa_simple
import scope
import utils
import plotting

def do_measure_admittance(scope, siggen, frequencies, resistor):

    # Set signal generator to drive a high-Z load with 1Vpp sine wave

    siggen.put_cmd('OUTP:LOAD INF')
    siggen.put_cmd('VOLT 1 VPP')
    siggen.put_cmd('FUNC SIN')
    siggen.put_cmd('OUTP ON')

    # initially scale the channels to 4volts/screen
    scope.scale_channel(1, 4)
    scope.scale_channel(2, 4)

    admittance = numpy.zeros(len(frequencies), dtype=complex)

    for measurement in range(len(frequencies)):

        starttime = time.time()
        freq = frequencies[measurement]
        print('Starting measurement {0} of {1}'.format(measurement + 1,
                                                    len(frequencies)))
        siggen.put_cmd('FREQ {0} HZ'.format(freq))

        scope.autoscale_chan(1)
        scope.autoscale_chan(2)
        scope.enable_channel(1)
        scope.enable_channel(2)

        # timebase adjust is done after autoscale because the autoscale messes
        # with the timebase.
        scope.adj_timebase(freq)

        v_ch1 = scope.measure_vpp(1)
        v_ch2 = scope.measure_vpp(2)

        phase = scope.measure_phase(1, 2)

        v_ch2_complex = cmath.rect(v_ch1, (cmath.pi/180) * phase)

        y = (v_ch1 - v_ch2_complex) / (v_ch2_complex * resistor)
        admittance[measurement] = y

        print('measurement took: {0} seconds'
                    .format(time.time() - starttime))
    return admittance

def measure_admittance(filename_prefix):

    max_frequency = 200e3
    num_points = 400
    resistor = 4.7e3

    frequencies = numpy.array([(i + 1) * max_frequency/num_points
                                for i in range(num_points)])

    oscscope = scope.Oscilloscope({
                                'type': 'socket',
                                'address': '132.181.52.74',
                                'port': 5024,
                                'promptstr': '>>'})

    siggen = visa_simple.Instrument({
                                'type': 'socket',
                                'address': '132.181.52.71',
                                'port': 5024,
                                'promptstr': 'sonarsg1>'})

    admittance = do_measure_admittance(oscscope, siggen, frequencies, resistor)
    utils.save_arrays(filename_prefix, [frequencies, admittance])
    plot_admittance_magnitude(filename_prefix, frequencies, admittance)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: measure_admittance.py filename_prefix')
        sys.exit(-1)
    filename_prefix = sys.argv[1]
    measure_admittance(filename_prefix)

