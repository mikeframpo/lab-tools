import time
import numpy
import cmath
import sys

import visa_simple
import scope
import utils
import plotting

def measure_frequencies(scope, siggen, vampl, voffs, averages, frequencies, measurements):

    # Set signal generator to drive a high-Z load with 1Vpp sine wave
    time.sleep(1)

    siggen.put_cmd('OUTP:LOAD INF')
    siggen.put_cmd('APPL:SIN 1KHZ, {0} VPP, 0V'.format(vampl * 2))
    siggen.put_cmd('OUTP ON')

    scope.enable_channel(1)
    scope.enable_channel(2)

    # initially scale the channels to 4volts/screen
    # the reference channel is scaled to half of the sceen
    scope.scale_channel(1, vampl * 2.5)

    # initialized to 1v/div, this will be scaled to match measurement level
    scope.scale_channel(2, 8)

    scope.put_cmd('CHAN2:OFFS {0}'.format(voffs))

    scope.setup_edge_trigger(1, vampl / 4)

    v_ch1 = numpy.zeros(len(frequencies), dtype=complex)
    v_ch2 = numpy.zeros(len(frequencies), dtype=complex)


    if averages is None:
        scope.put_cmd('ACQ:TYPE NORM')
    else:
        num_averages = int(averages)
        scope.put_cmd(':ACQ:TYPE AVER')
        scope.put_cmd(':ACQ:COUN {0}'.format(num_averages))

    for measurement in range(len(frequencies)):

        starttime = time.time()
        freq = frequencies[measurement]
        print('Starting measurement {0} of {1}'.format(measurement + 1,
                                                    len(frequencies)))

        siggen.put_cmd('FREQ {0} HZ'.format(freq))
        scope.adj_timebase(freq)
        
        if averages is not None:
            # allow a number of averages to be collected after the freq
            # has been adjusted
            time.sleep(0.5)

        scope.manual_scale_chan(2)

        v_ch1_complex = complex(0, 0)
        v_ch2_complex = complex(0, 0)

        for avg in range(measurements):

            v_ch1_mag = scope.measure_vpp(1)
            v_ch2_mag = scope.measure_vpp(2)
            v_ch2_phase = scope.measure_phase(1, 2)

            v_ch1_complex += utils.mag_phase_to_complex(v_ch1_mag, 0)
            v_ch2_complex += utils.mag_phase_to_complex(
                                                    v_ch2_mag, v_ch2_phase)

        v_ch1_complex /= measurements
        v_ch2_complex /= measurements

        # make sure that the circuit is correct
        #errorfudge = 0.1
        #assert (cmath.polar(v_ch1_complex)[0] + errorfudge) >= \
        #        cmath.polar(v_ch2_complex)[0]

        v_ch1[measurement] = v_ch1_complex
        v_ch2[measurement] = v_ch2_complex

        print('measurement took: {0} seconds'
                    .format(time.time() - starttime))
    return (v_ch1, v_ch2)

def do_measure_admittance(scope, siggen, frequencies, measurements, resistor):

    (v_ch1, v_ch2) = measure_frequencies(scope, siggen, 5.0, frequencies, measurements)
    admittance = numpy.zeros(len(frequencies))
    for i_freq in frequencies:
        y = (v_ch1[i_freq] - v_ch2[i_freq]) / (v_ch2[i_freq] * resistor)
        admittance[i_freq] = y

    return admittance

def load_devices():

    oscscope = scope.Oscilloscope({
                                'type': 'socket',
                                'address': '132.181.53.147',
                                'port': 5024,
                                'promptstr': '>>'})

    siggen = visa_simple.Instrument({
                                'type': 'socket',
                                'address': '132.181.52.157',
                                'port': 5024,
                                'promptstr': 'sonarsg1>'})
    return (oscscope, siggen)

def measure_admittance(frequencies, filename, resistance):

    measurements = 1

    (oscscope, siggen) = load_devices()
    admittance = do_measure_admittance(oscscope, siggen, frequencies,
                                        measurements, resistance)
    utils.save_arrays(filename, frequencies, admittance)

def measure_admittance_linear(filename_prefix, start_freq, end_freq, num_pts,
                                resistance):

    frequencies = numpy.linspace(start_freq, end_freq, num_pts)
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

def measure_transducer_response(filename_prefix, start_exp, end_exp, num_pts):

    freqs = numpy.logspace(start_exp, end_exp, num_pts)
    (oscscope, siggen) = load_devices()
    (v_ch1, v_ch2) = measure_frequencies(oscscope, siggen, 5.0, 1.677, 64, freqs, 1)

    gain_mag = abs(v_ch2) / abs(v_ch1)
    filename = '{0}_{1}_{2}_{3}.npz'.format(filename_prefix, start_exp, end_exp, num_pts)

    utils.save_arrays(filename, freqs, gain_mag)

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

    elif meas_type == "trans_log":
        if len(sys.argv) != 6:
            print_usage()
            sys.exit(1)
        start_exp = float(sys.argv[3])
        end_exp = float(sys.argv[4])
        num_pts = int(sys.argv[5])
        measure_transducer_response(filename_prefix, start_exp, end_exp, num_pts)

    else:
        print_usage()
        sys.exit(1)

