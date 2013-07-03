import time
import numpy
import cmath
import sys

import visa_simple
import scope
import utils
import plotting

def do_measure_admittance(scope, siggen, frequencies, averages, resistor):

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

        # autoscale reference channel last because this is the most reliable
        # channel to trigger from
        scope.autoscale_chan(2)
        scope.autoscale_chan(1)

        scope.enable_channel(1)
        scope.enable_channel(2)
        scope.put_cmd(':ACQ:TYPE AVER')

        # timebase adjust is done after autoscale because the autoscale messes
        # with the timebase.
        scope.adj_timebase(freq)

        v_ch1_complex = complex(0, 0)
        v_ch2_complex = complex(0, 0)

        for avg in range(averages):

            v_ch1_mag = scope.measure_vpp(1)
            v_ch2_mag = scope.measure_vpp(2)
            v_ch2_phase = scope.measure_phase(1, 2)

            v_ch1_complex += utils.mag_phase_to_complex(v_ch1_mag, 0)
            v_ch2_complex += utils.mag_phase_to_complex(
                                                    v_ch2_mag, v_ch2_phase)

        v_ch1_complex /= averages
        v_ch2_complex /= averages

        # make sure that the circuit is correct
        errorfudge = 0.1
        assert (cmath.polar(v_ch1_complex)[0] + errorfudge) >= \
                cmath.polar(v_ch2_complex)[0]

        y = (v_ch1_complex - v_ch2_complex) / (v_ch2_complex * resistor)
        admittance[measurement] = y

        print('measurement took: {0} seconds'
                    .format(time.time() - starttime))
    return admittance

def measure_admittance(filename_prefix):

    max_frequency = 200e3
    num_points = 2000
    averages = 1
    resistor = 4.66e3

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

    admittance = do_measure_admittance(oscscope, siggen, frequencies,
                                        averages, resistor)
    utils.save_arrays(filename_prefix + '.npz', frequencies, admittance)
    #plotting.plot_show_admittance_magnitude(frequencies, admittance)
    plotting.plot_show_complex_admittance(frequencies, admittance)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: measure_admittance.py filename_prefix')
        sys.exit(-1)
    filename_prefix = sys.argv[1]
    measure_admittance(filename_prefix)

