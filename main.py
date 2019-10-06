from ict import RigolDG
from ict import SiglentSDS

import numpy as np
import time


if __name__ == '__main__':
    awg = RigolDG('192.168.1.14')
    scope = SiglentSDS('192.168.1.16')


    # test = np.sin(np.arange(0,10))
    # awg.ch[0].transfer_wave(test)
    #awg.ch[0].transfer_wave(np.arange(0,4,0.1))


    # print(scope.ch[0].v_off)
    # scope.ch[0].v_off =  0.3
    # print(scope.ch[0].v_off)
    # scope.ch[0].v_off = 0

    # print(scope.ch[0].skew)
    # scope.ch[0].skew = 13E-9
    # print(scope.ch[0].skew)
    # scope.ch[0].skew = 0


    # print(scope.ch[0].enabled)
    # scope.ch[0].enabled = 0
    # print(scope.ch[0].enabled)
    # scope.ch[0].enabled = 1

    # print(scope.ch[0].v_div)
    # scope.ch[0].v_div = 1.3
    # print(scope.ch[0].v_div)
    # scope.ch[0].v_div = 1

    # print(scope.ch[0].wfsu)

    lol = scope.ch[0].get_waveform()
    print(type(lol))



