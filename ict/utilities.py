class Waveform:

    x_values = []
    x_units = ''
    x_name = ''

    y_values = []
    y_units = ''
    y_name = ''

    user_field = ''

    def __init__(self):
        pass

    @property
    def x_label(self):
        str_try = "%s (%s)" % (self.x_name, self.x_units)
        print(str_try)
        return str_try

    @property
    def y_label(self):
        return "%s (%s)" % (self.y_name, self.y_units)



def freq_response(scope,awg,freqs):
    # Setup
    scope.ch[0].enable = 1
    scope.ch[1].enable = 1

    awg.ch[0].enable = 1
    awg.ch[0].enable = 1


    # scope.t_div

    pass



