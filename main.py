from ict import RigolDG
import numpy as np


if __name__ == '__main__':
    awg = RigolDG('192.168.1.14')

    # test = np.sin(np.arange(0,10))
    # awg.ch[0].transfer_wave(test)
    awg.ch[0].transfer_wave(np.arange(0,4,0.1))