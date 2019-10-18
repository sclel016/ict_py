from ict.Interface import Interface
from ict.utilities import Waveform
import numpy as np
import json
import re

class ScopeChannel:

    def __init__(self,scope,ch_idx):
        self._scope = scope
        self.ch_idx = ch_idx + 1

    # Enable channel
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


    @property
    def all(self):
        ret_str = self._scope.query("C%i:PAVA? ALL" % self.ch_idx)

        # Strip
        ret_str = ret_str.lstrip('C%i:PAVA ' % self.ch_idx)
        ret_str = ret_str.rstrip('\n')

        # Capture name and value
        name_expr = r"(?P<name>[A-Z]{3,})"
        val_expr = r"(?P<val>[+-]?\d+\.\d+[eE]?[+-]?\d+)"
        r = re.compile(name_expr+","+val_expr)

        # Convert to dict() of floats
        ret_dict = dict(r.findall(ret_str))
        for key in ret_dict:
            ret_dict[key] = float(ret_dict[key])

        return ret_dict

    def _get_waveform(self):
        # self._scope.write("C%i:WF? DAT2" % self.ch_idx)
        wav_resp = self._scope.query_binary_values("C%i:WF? DAT2" % self.ch_idx, datatype='b')
        return np.asarray(wav_resp)

    def get_waveform(self):
        wave = Waveform

        # Y axis
        wave.codes = self._get_waveform()
        wave.v_off = self.v_off
        wave.v_div = self.v_div
        wave.y_values = wave.codes*(wave.v_div / 25)-wave.v_off
        wave.y_units = "V"
        wave.y_name = "Samples"

        # X axis
        wave.sample_rate = self._scope.sample_rate
        wave.trg_offset = self._scope.trg_offset
        wave.x_values = np.arange(0,wave.codes.size) * (1/wave.sample_rate) + wave.trg_offset
        wave.x_units = "s"
        wave.x_name = "Time"

        return wave


class SiglentSDS(Interface):

    NUM_CHAN = 2
    ch = []

    def __init__(self, ip):
        super().__init__(ip)
        self.inst.chunk_size = 14e6 * 8 + 1e3 # 14Mpts * 8bits/pt + overhead

        for ii in range(self.NUM_CHAN):
            self.ch.append(ScopeChannel(self, ii))

    # WaveForm SetUp
    @property
    def wfsu(self):
        ret_str = self._scope.query("WFSU?")
        return ret_str.split()

    # SAmple RAte (Samp/s)
    @property
    def sample_rate(self):
        ret_str = self.query("SARA?")
        return self.parse_sci(ret_str)

    # Trigger Offset (s)
    @property
    def trg_offset(self):
        ret_str = self.query("TRDL?")
        return self.parse_sci(ret_str)

    @trg_offset.setter
    def trg_offset(self,val):
        self.write("TRDL %E" % val)

    # Time Division (s)
    @property
    def time_div(self):
        ret_str = self.query("TDIV?")
        return self.parse_sci(ret_str)

    @time_div.setter
    def time_div(self, val):
        self.write("TDIV %E" % val)


    # def measure_phase(self):
    #     """ Measures the phase delay between CH1 and CH2
    #
    #     :return: Phase Delay (Degrees)
    #     """
    #
    #     # Set measurement type
    #     self.write("PACU 1, PHASE, C1-C2")
    #
    #     ret_str = self.query("PAVA? CUST1")
    #
    #     print(ret_str)
    #
    #     return self.parse_sci(ret_str)


    def get_phase_delay(self):
        """ Measures the phase delay between CH1 and CH2

        :return: Phase Delay (Degrees)
        """
        ret_str = self.query("C1-C2:MEAD? PHA")
        expr = "PHA,(?P<val>[+-]?\d+(.\d+)?)degree"
        return float(re.search(expr,ret_str).group('val'))
        # return self.parse_sci(ret_str)

    def get_time_delay(self):
        """ Measures the time delay between CH1 and CH2

        :return: Phase Delay (Degrees)
        """
        ret_str = self.query("C1-C2:MEAD? FRR")
        return self.parse_sci(ret_str)


