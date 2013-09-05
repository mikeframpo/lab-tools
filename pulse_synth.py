
import visa_simple
import numpy as np

def measure_waveform(scope, siggen, channel, freq, num_samples):
    
    siggen.put_cmd('FREQ {0} HZ'.format(freq))
    oscscope.set_acq_mode(scope.ACQ_MODE_SINGLE)

    siggen.put_cmd('OUTP ON')
    waveform = fetch_waveform(channel, num_samples)
    return waveform

def pulse_synth():

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

    siggen.put_cmd('OUTP:LOAD INF')
    siggen.put_cmd('VOLT 1 VPP')
    siggen.put_cmd('FUNC SIN')
    siggen.put_cmd('OUTP OFF')

    #TODO: setup scope axis and timebase.

    num_samples = 1000
    channel = 1

    freqs = np.linspace(10e3, 10e3, 1)
    waveforms = np.zeros(len(freqs))

    for i in range(freqs):

        siggen.put_cmd('OUTP OFF')
        waveforms[i] = measure_waveform(oscscope, siggen, channel, freq,
            num_samples)

    #TODO: sum waveforms and plot.

