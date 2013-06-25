import visa_simple
import scope
import time

def measure_frequencies(scope, siggen, frequencies):

    # Set signal generator to drive a high-Z load with 1Vpp sine wave

    siggen.put_cmd('OUTP:LOAD INF')
    siggen.put_cmd('VOLT 1 VPP')
    siggen.put_cmd('FUNC SIN')
    siggen.put_cmd('OUTP ON')

    #TODO: init trigger settings
    # initially scale the channels to 4volts/screen
    scope.enable_channel(1)
    scope.enable_channel(2)
    scope.scale_channel(1, 4)
    scope.scale_channel(2, 4)

    voltages = []

    for measurement in range(len(frequencies)):

        starttime = time.time()
        freq = frequencies[measurement]
        print('Starting measurement {0} of {1}'.format(measurement + 1,
                                                    len(frequencies)))
        siggen.put_cmd('FREQ {0} HZ'.format(freq))

        scope.autoscale_chan(1)
        scope.autoscale_chan(2)

        # timebase adjust is done after autoscale because the autoscale messes
        # with the timebase.
        scope.adj_timebase(freq)

        v_ch1 = scope.measure_vpp(1)
        v_ch2 = scope.measure_vpp(2)

        phase = scope.measure_phase(1, 2)

        #TODO: format measurements for plotting.

        print('measurement took: {0} seconds'
                    .format(time.time() - starttime))

#test code
frequencies = [1e3, 10e3, 100e3]

scope = scope.Oscilloscope({
                            'type': 'socket',
                            'address': '132.181.52.74',
                            'port': 5024,
                            'promptstr': '>>'})

siggen = visa_simple.Instrument({
                            'type': 'socket',
                            'address': '132.181.52.71',
                            'port': 5024,
                            'promptstr': 'sonarsg1>'})

measure_frequencies(scope, siggen, frequencies)

