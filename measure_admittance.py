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

def measure_admittance(frequencies, filename, resistance):

    averages = 1

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
                                        averages, resistance)
    utils.save_arrays(filename, frequencies, admittance)

def measure_admittance_linear(filename_prefix, start_freq, end_freq, num_pts,
                                resistance):

    frequencies = numpy.array([(i + 1) * end_freq/num_pts
                                for i in range(num_pts)])
    filename = '{0}_log_{1}_{2}_{3}.npz'.format(filename_prefix, start_freq,
                                                end_freq, num_pts)
    measure_admittance(frequencies, filename, resistance)


def measure_admittance_log(filename_prefix, start_freq, decades, num_pts,
                            resistance):

    frequencies = numpy.logspace(1.0, decades + 1, num_pts)
    frequencies = frequencies * start_freq / 10

    filename = '{0}_log_{1}_{2}_{3}.npz'.format(filename_prefix, start_freq,
                                                decades, num_pts)
    measure_admittance(frequencies, filename, resistance)

def print_usage():
    print('''
Usage: measure_admittance.py filename_prefix log|linear options
    filename_prefix
        a unique name to identify the measurement or device being tested.

    log options
        log requires the following parameters in this order:
        start_freq decades num_pts resistor_val

    linear options
        linear requires the following parameters in this order:
        start_freq end_freq num_pts resistor_val
''')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(-1)
    filename_prefix = sys.argv[1]
    meas_type = sys.argv[2]
    if meas_type == "log":
        if len(sys.argv) != 7:
            print_usage()
            sys.exit(1)
        start_freq = float(sys.argv[3])
        decades = float(sys.argv[4])
        num_pts = int(sys.argv[5])
        resistance = float(sys.argv[6])
        measure_admittance_log(filename_prefix, start_freq, decades, num_pts,
                                resistance)
    elif meas_type == "linear":
        if len(sys.argv) != 7:
            print_usage()
            sys.exit(1)
        start_freq = float(sys.argv[3])
        end_freq = float(sys.argv[4])
        num_pts = int(sys.argv[5])
        resistance = float(sys.argv[6])
        measure_admittance_linear(filename_prefix, start_freq, end_freq,
                                    num_pts, resistance)

