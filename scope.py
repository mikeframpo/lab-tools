
import visa_simple
import numpy as np

class Oscilloscope(visa_simple.Instrument):
    
    def __init__(self, config):
        super(Oscilloscope, self).__init__(config)

    def enable_channel(self, channel):
        cmd = ':CHAN{0}:DISP ON'.format(channel)
        self.put_cmd(cmd)
        self.check_errors()

    def scale_channel(self, channel, volts_screen):
        cmd = ':CHAN{0}:RANG {1}'.format(channel, volts_screen)
        self.put_cmd(cmd)
        self.check_errors()

    def adj_timebase(self, frequency):
        '''timebase is adjusted for the expected frequency to draw two
        complete waveforms on screen.'''
        timebase = (1/frequency) * 2
        cmd = ':TIM:RANG {0}'.format(timebase)
        self.put_cmd(cmd)
        self.check_errors()

    def autoscale_chan(self, channel):
        cmd = ':AUT CHAN{0}'.format(channel)
        self.put_cmd(cmd)
        self.check_errors()

    def measure_vpp(self, channel):
        cmd = ':MEAS:VPP? CHAN{0}'.format(channel)
        self.put_cmd(cmd)
        response = self.read_response()
        result = float(response)
        return result

    def measure_phase(self, ch_reference, ch_phase):
        '''returns the phase between the specified channels in degrees'''
        cmd = ':MEAS:PHAS? CHAN{0}, CHAN{1}'.format(ch_phase, ch_reference)
        self.put_cmd(cmd)
        response = self.read_response()
        result = float(response)
        return result

    def _set_num_capture_samples(self, num_samples):
        self.put_cmd(':WAV:POIN {0}'.format(num_samples))

    def _get_sampling_period(self, channel):
        self.put_cmd(':WAV:XINC? {0}'.format(channel))
        response = self.read_response()
        period = float(response)
        return period

    ACQ_MODE_RUN = 0
    ACQ_MODE_SINGLE = 1

    def set_acq_mode(self, mode):
        if mode == ACQ_MODE_RUN:
            self.put_cmd(':RUN')
        else if mode == ACQ_MODE_SINGLE:
            self.put_cmd(':SINGLE')

    def fetch_waveform(self, channel, num_samples):
        self.put_cmd(':WAV:FORM ASCII')
        self.put_cmd(':WAV:POIN:MODE RAW')
        self.put_cmd(':WAV:SOUR {0}'.format(channel))

        self._set_num_capture_samples(num_samples)
        period = _get_sampling_period(channel)
        t = np.array([i * period for i in range(num_samples)])

        #TODO: need to determine whether this is necessary?
        self.put_cmd(':WAV:XOR? {0}'.format(channel))
        print('capture origin: ' + self.read_response())

        self.put_cmd('WAV:DATA? {0}'.format(channel))
        response = self.read_response()

        v = np.array([float(i) for i in response.split(',')])
        return (t, v)

