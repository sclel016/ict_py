from ict.Interface import Interface
import numpy as np
import re

class AwgChannel:


    def __init__(self,awg,ch_idx):
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
    def enabled(self,val):
        if val>=1:
            self.__awg.write("OUTP%i ON" % self.ch_idx)
        elif val==0:
            self.__awg.write("OUTP%i OFF"% self.ch_idx)


    # Channel Mode
    @property
    def mode(self):
        return re.search("(\w+)\,",self.__awg.query(":SOUR%i:APPL?" % self.ch_idx)).group(1)


    # SAMPLE RATE (Samp/s)
    @property
    def sample_rate(self):
        ret_str = self.__awg.query(":SOUR%i:FUNC:ARB:SRAT?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @sample_rate.setter
    def sample_rate(self,val):
        self.__awg.write(":SOUR%i:FUNC:ARB:SRAT %i" % (self.ch_idx, int(val)))


    # Voltage Offset (V_DC)
    @property
    def v_off(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:OFFS?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_off.setter
    def v_off(self,val):
        self.__awg.write(":SOUR%i:VOLT:OFFS %i" % (self.ch_idx, int(val)))

    # Maximum Voltage(V_DC)
    @property
    def v_high(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:HIGH?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_high.setter
    def v_high(self,val):
        self.__awg.write(":SOUR%i:VOLT:HIGH %i" % (self.ch_idx, int(val)))

    # Minimum Voltage(V_DC)
    @property
    def v_low(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT:LOW?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @v_low.setter
    def v_low(self,val):
        self.__awg.write(":SOUR%i:VOLT:LOW %i" % (self.ch_idx, int(val)))


    # Voltage Amplitude (V_pp)
    @property
    def amplitude(self):
        ret_str = self.__awg.query(":SOUR%i:VOLT?" % self.ch_idx)
        return self.__awg.parse_sci(ret_str)

    @amplitude.setter
    def amplitude(self,val):
        self.__awg.write(":SOUR%i:VOLT %i" % (self.ch_idx, int(val)))


    def transfer_wave(self,wave):
        # Configure Channel
        self.v_high = wave.max()
        self.v_low  = wave.min()

        codes = (wave - wave.min()) * (float(16384)/(wave.max() - wave.min()))
        codes.astype('int16')

        self.__awg.write_binary_values(':SOUR%i:TRAC:DATA:DAC16,<END>' % self.ch_idx, codes, datatype='uint16')



class RigolDG(Interface):

    NUM_CHAN = 2

    ch = []

    def __init__(self, ip):
        super().__init__(ip)

        if "DG1022Z" in self.ident:
            self.MAX_SAMPLE_RATE = int(20E6)
        elif "DG1062Z" in self.ident:
            self.MAX_SAMPLE_RATE = int(60E6)

        for ii in range(self.NUM_CHAN):
            self.ch.append(AwgChannel(self, ii))

        # Configure Binary Write


