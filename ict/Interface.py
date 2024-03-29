import pyvisa
import re


class Interface:

    inst = ''
    ip = ''
    ident = ''
    rm = pyvisa.ResourceManager()

    def __init__(self,ip):
        self.ip = ip
        self.inst = self.rm.open_resource('TCPIP0::%s::INSTR' % self.ip)
        self.ident = self.inst.query("*IDN?")

    def query(self,cmd):
        return self.inst.query(cmd)

    def write(self,cmd):
        print(cmd)
        self.inst.write(cmd)

    def read(self,*args,**kwargs):
        return self.inst.query_ascii_values(*args,**kwargs)

    def write_binary_values(self,*args,**kwargs):
        self.inst.write_binary_values(*args,**kwargs)

    def read(self,*args,**kwargs):
        return self.inst.read(*args,**kwargs)

    def query_binary_values(self,*args,**kwargs):
        return self.inst.query_binary_values(*args,**kwargs)

    def query_ascii_values(self,*args,**kwargs):
        return self.inst.query_ascii_values(*args,**kwargs)

    def read_raw(self,*args,**kwargs):
        return self.inst.read_raw(*args,**kwargs)

    def read_bytes(self,*args,**kwargs):
        return self.inst.read_bytes(*args,**kwargs)

    def parse_sci(self,in_str):
        expr = r"[+-]?\d+\.\d+([eE][+-]?\d+)?"
        return float(re.search(expr, in_str).group())






