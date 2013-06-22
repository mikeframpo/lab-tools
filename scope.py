
import visa_simple

class Oscilloscope(visa_simple.Instrument):
    
    def __init__(self, address, port):
        super(Oscilloscope, self).__init__(address, port)

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
        pass
        
    def autoscale_chan(self, channel):
        #TODO
        pass

    def measure_vpp(self, channel):
        #TODO
        pass

    def measure_phase(self, ch_reference, ch_phase):
        #TODO
        pass
