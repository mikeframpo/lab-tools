import visa_simple
import scope

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

        freq = frequencies[measurement]
        print('Starting measurement {0} of {1}'.format(measurement,
                                                    len(frequencies)))
        siggen.put_cmd('FREQ {0} HZ'.format(freq))
        scope.adj_timebase(freq)
        v_ch1 = scope.measure_vpp(1)
        v_ch2 = scope.measure_vpp(2)

#test code
scope = scope.Oscilloscope('132.181.52.74', 5024)
scope.enable_channel(1)
scope.enable_channel(2)

