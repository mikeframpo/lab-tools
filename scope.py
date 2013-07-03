
import visa_simple

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

