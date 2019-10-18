from ict.Interface import Interface
import numpy as np
import re


class AwgChannel:
    """
        Class designed to interface with individual channels on the Rigol DG1062Z AWG
    """
    def __init__(self, awg, ch_idx):
        self.__awg = awg
        self.ch_idx = ch_idx + 1

    # ENABLE
    @property
    def enabled(self):
        ret = self.__awg.query("OUTP%i?" % self.ch_idx)
        if "OFF" in ret:
            return 0
        elif "ON" in ret:
            return 1
        else:
            raise ValueError("Unexpected return string: %s", ret)

    @enabled.setter
    def enabled(self, val):
        if val >= 1:
            self.__awg.write("OUTP%i ON" % self.ch_idx)
        elif val == 0:
            self.__awg.write("OUTP%i OFF" % self.ch_idx)

    # Channel Mode
    @property
    def mode(self):
        return re.search("(\w+)\,", self.__awg.query(":SOUR%i:APPL?" % self.ch_idx)).group(1)

    # SAMPLE RATE (Samp/s)
    @property
    def sample_rate(self):
        ret_str = self.__awg.query(":SOUR%i:FUNC:ARB:SRAT?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @sample_rate.setter
    def sample_rate(self, val):
        self.__awg.write(":SOUR%i:FUNC:ARB:SRAT %i" % (self.ch_idx, int(val)))

    # Voltage Offset (V_DC)
    @property
    def v_off(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:OFFS?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_off.setter
    def v_off(self, val):
        self.__awg.write(":SOUR%i:VOLT:OFFS %f" % (self.ch_idx, val))

    # Maximum Voltage(V_DC)
    @property
    def v_high(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:HIGH?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_high.setter
    def v_high(self, val):
        self.__awg.write(":SOUR%i:VOLT:HIGH %f" % (self.ch_idx, val))

    # Minimum Voltage(V_DC)
    @property
    def v_low(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:LOW?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_low.setter
    def v_low(self, val):
        self.__awg.write(":SOUR%i:VOLT:LOW %f" % (self.ch_idx, val))

    # Voltage Amplitude (V_pp)
    @property
    def amplitude(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @amplitude.setter
    def amplitude(self, val):
        self.__awg.write(":SOUR%i:VOLT %f" % (self.ch_idx, val))

    def transfer_wave(self, wave, Fs):
        """ Set the AWG to output a arbitrary waveform
        :param
            wave: Arbitrary wave samples (V)
            Fs: Sample Rate (Samp/s)
        :return:
        """

        # Set channel to ARB mode
        self.__awg.write(":SOUR%i:APPL:ARB" % self.ch_idx)

        # Set Sample Rate
        self.sample_rate = Fs

        # Configure optimal voltage range
        self.v_high = wave.max()
        self.v_low = wave.min()

        # Generate uint16 codes
        codes = (wave - wave.min()) * (float(16383) / (wave.max() - wave.min()))
        codes = np.round(codes)

        # Send data
        header_str = ':SOUR%i:TRAC:DATA:DAC16 VOLATILE,' % self.ch_idx
        NUM_PTS_PER_WRITE = 16384
        num_writes = int(np.ceil(codes.size / NUM_PTS_PER_WRITE))
        for slc_idx in np.arange(0, num_writes):
            if slc_idx == num_writes - 1:
                print(slc_idx * NUM_PTS_PER_WRITE)
                codes_slc = codes[(slc_idx * NUM_PTS_PER_WRITE):None]
                self.__awg.write_binary_values(header_str + 'END,', codes_slc.astype("uint16"), datatype='H')
            else:
                codes_slc = codes[slc_idx * NUM_PTS_PER_WRITE:(slc_idx + 1) * NUM_PTS_PER_WRITE]
                self.__awg.write_binary_values(header_str + 'CON,', codes_slc.astype("uint16"), datatype='H')

    def set_sine(self, **kwargs):
        """ Set the AWG to output a sine wave
        :param
            freq: Frequency (Hz)
            vpp: Peak to Peak Voltage (V)
            dc_offs: DC Voltage Offset (V)
            phase: Phase Offset (Degrees)
        :return:
        """
        opt = dict()
        opt['freq'] = kwargs.get('freq', 1e3)
        opt['vpp'] = kwargs.get('vpp', 5)
        opt['dc_offs'] = kwargs.get('dc_offs', 0)
        opt['phase'] = kwargs.get('phase', 0)

        self.__awg.write(":SOUR%i:APPL:SIN %f,%f,%f,%f" % (self.ch_idx, opt['freq'], opt['vpp'],
                                                                 opt['dc_offs'], opt['phase']))

    def set_square(self, **kwargs):
        """ Set the AWG to output a square wave
        :param
            freq: Frequency (Hz)
            vpp: Peak to Peak Voltage (V)
            dc_offs: DC Voltage Offset (V)
            phase: Phase Offset (Degrees)
        :return:
        """
        Opt = dict()
        Opt['freq'] = kwargs.get('freq', 1e3)
        Opt['vpp'] = kwargs.get('vpp', 5)
        Opt['dc_offs'] = kwargs.get('dc_offs', 0)
        Opt['phase'] = kwargs.get('phase', 0)

        self.__awg.write(":SOUR%i:APPL:SQU %f,%f,%f,%f" % (self.ch_idx, Opt['freq'], Opt['vpp'],
                                                           Opt['dc_offs'], Opt['phase']))

    def get_output(self):
        """ Get info on the current transmission mode
        :param

        :return: Dictionary with
            type: Type of waveform
            freq: Frequency (Hz)
            vpp: Peak to Peak Voltage (V)
            dc_offs: DC Voltage Offset (V)
            phase: Phase Offset (Degrees)
        """
        ret_str = self.__awg.query("SOUR%i:APPL?" % self.ch_idx)
        ret_str = ret_str.rstrip("\"\n")
        ret_str = ret_str.lstrip("\"")

        ret_list = ret_str.split(",")

        ret_dict = dict()
        ret_dict['type'] = ret_list[0]
        ret_dict['freq'] = float(ret_list[1])
        ret_dict['vpp'] = float(ret_list[2])
        ret_dict['dc_offs'] = float(ret_list[3])
        ret_dict['phase'] = float(ret_list[4])
        return ret_dict


class RigolDG(Interface):
    """
        Class designed to interface with individual channels on the Rigol DG1062Z AWG
    """
    NUM_CHAN = 2

    ch = []

    def __init__(self, ip):
        super().__init__(ip)
        # self.inst.write_termination = '\n'
        self.inst.chunk_size = 16e6 * 16 + 1e3

        if "DG1022Z" in self.ident:
            self.MAX_SAMPLE_RATE = int(20E6)
        elif "DG1062Z" in self.ident:
            self.MAX_SAMPLE_RATE = int(60E6)

        for ii in range(self.NUM_CHAN):
            self.ch.append(AwgChannel(self, ii))

    # Couple Channels
    @property
    def couple(self):
        ret_str = self.query(":COUP?")
        if "OFF" in ret_str:
            return 0
        elif "ON" in ret_str:
            return 1
        else:
            raise ValueError("Unexpected return string: %s", ret_str)

    @couple.setter
    def couple(self, val):
        if val >= 1:
            self.write("COUP ON")
        elif val == 0:
            self.write("COUP OFF")

