
from ict import RigolDG
from ict import SiglentSDS
from ict import Waveform
import matplotlib.pyplot as plt
from bokeh.plotting import figure, output_file, show
import numpy as np
import time


# if __name__ == '__main__':

#%%
awg = RigolDG('192.168.1.14')
#
# awg.ch[0].set_sine(freq = 1e3,vpp=4)
# awg.ch[0].set_square(freq = 1e4,vpp=4)

# #
# A = 1
# N = 20e3
# Fs = 20e6

# f = 993
# awg.ch[0].sample_rate = Fs
# # # # test = np.sin(np.arange(0,10))
# # # # awg.ch[0].transfer_wave(test)
# awg.ch[0].transfer_wave(A*np.sin(2*np.pi * np.arange(0, N) * Fs / f),Fs)
# # awg.ch[0].transfer_wave(np.array([1,2,3,2,1,-1,-4]),Fs)

#%%
scope = SiglentSDS('192.168.1.16')
scope.get_phase_delay()
# scope.time_div

# scope.time_div = 100e-6

# scope.measure_phase()
print(scope.ch[0].all)
#
# wave = scope.ch[0].get_waveform()
#
# plt.plot(wave.x_values, wave.y_values)



#%%
