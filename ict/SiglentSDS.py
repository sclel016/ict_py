from ict.Interface import Interface
import numpy as np
import re
import argparse

class ScopeChannel:


    def __init__(self,scope,ch_idx):
        self._scope = scope
        self.ch_idx = ch_idx + 1


    # ENABLE TRACE
    @property
    def enabled(self):
        ret = self._scope.query("C%i:TRA?" % self.ch_idx)
        if "OFF" in ret:
            return 0
        elif "ON" in ret:
            return 1
        else:
            raise ValueError("Unexpected return string: %s", ret)

    @enabled.setter
    def enabled(self,val):
        if val>=1:
            self._scope.write("C%i:TRA ON" % self.ch_idx)
        elif val==0:
            self._scope.write("C%i:TRA OFF"% self.ch_idx)




    # DC Offset (V_DC)
    @property
    def v_off(self):
        ret_str = self._scope.query("C%i:OFST?" % self.ch_idx)
        return self._scope.parse_sci(ret_str)

    @v_off.setter
    def v_off(self,val):
        self._scope.write("C%i:OFST %f" % (self.ch_idx, val))


    # Channel Skew (+-100 NS)
    @property
    def skew(self):
        ret_str = self._scope.query("C%i:SKEW?" % self.ch_idx)
        return self._scope.parse_sci(ret_str)

    @skew.setter
    def skew(self,val):
        self._scope.write("C%i:SKEW %E" % (self.ch_idx, val))


    # V_DIV (V_pp)
    @property
    def v_div(self):
        ret_str = self._scope.query("C%i:VOLT_DIV?" % self.ch_idx)
        return self._scope.parse_sci(ret_str)

    @v_div.setter
    def v_div(self,val):
        self._scope.write("C%i:VOLT_DIV %E" % (self.ch_idx, val))

    # WaveForm SetUp
    @property
    def wfsu(self):
        ret_str = self._scope.query("WFSU?")
        return ret_str.split()

    def get_waveform(self):
        return self._scope.query_binary_values("C%i:WF? DAT2" % self.ch_idx)



class SiglentSDS(Interface):

    NUM_CHAN = 2

    ch = []

    def __init__(self, ip):
        super().__init__(ip)

        for ii in range(self.NUM_CHAN):
            self.ch.append(ScopeChannel(self, ii))



    # SAMPLE RATE (Samp/s)
    @property
    def sample_rate(self):
        ret_str = self.query("SARA?")
        return self.parse_sci(ret_str)

    @sample_rate.setter
    def sample_rate(self,val):
        self.write("SARA %i" % int(val))