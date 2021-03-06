#!/usr/bin/env python
# encoding: utf-8
"""pwr.py: API for SCPI commands for
kikusui PWR1600L though PIA4850 usb control model
"""
__version__ = "0.0.1"
__author__ = "@boqiling"
__all__ = ["PowerSupply"]

import usbtmc
import re
import logging
import time

vid = 0x0b3e  # kikusui PIA4850 vendor id
pid = 0x1014  # kikusui PIA4850 product id


class PowerSupplyException(Exception):
    pass


class PowerSupply(object):
    def __init__(self):
        self.instr = usbtmc.Instrument(vid, pid)
        idn = self.instr.ask("*IDN?")
        if re.match(r"KIKUSUI[\w|\s|\.|\,]+PIA4850", idn):
            logging.info("Power Supply Found: " + idn)
        else:
            raise PowerSupplyException("No power supply found.")
        # clean err msg
        errmsg = self.instr.ask("ERR?")
        while (errmsg != "0"):
            errmsg = self.instr.ask("ERR?")

    def reset(self):
        self.instr.write("*RST")

    def _checkerr(self):
        errmsg = self.instr.ask("ERR?")
        while (errmsg != "0"):
            self.reset()
            raise PowerSupplyException(errmsg)

    def selectChannel(self, node, ch):
        self.instr.write("NODE {0}".format(node))
        self.instr.write("CH {0}".format(ch))
        time.sleep(1)
        self._checkerr()

    def measureVolt(self):
        volt = self.instr.ask("VOUT?")
        v = float(volt.strip())
        self._checkerr()
        return v

    def measureCurr(self):
        curr = self.instr.ask("IOUT?")
        c = float(curr.strip())
        self._checkerr()
        return c

    def set(self, params):
        self.instr.write("VSET {0}".format(params["volt"]))
        self.instr.write("ISET {0}".format(params["curr"]))
        self.instr.write("OVSET {0}".format(params["ovp"]))
        self.instr.write("OCSET {0}".format(params["ocp"]))
        self._checkerr()

    def setVolt(self, volt):
        self.instr.write("VSET {0}".format(volt))
        self._checkerr()

    def setCurr(self, curr):
        self.instr.write("ISET {0}".format(curr))
        self._checkerr()

    def setOVP(self, ovp):
        self.instr.write("OVSET {0}".format(ovp))
        self._checkerr()

    def setOCP(self, ocp):
        self.instr.write("OCSET {0}".format(ocp))
        self._checkerr()

    def activateOutput(self):
        self.instr.write("OUT 1")
        self._checkerr()

    def deactivateOutput(self):
        self.instr.write("OUT 0")
        self._checkerr()


if __name__ == "__main__":
    ps = PowerSupply()
    print "###ADDR 5###"
    ps.selectChannel(node=5, ch=1)
    setting = {"volt": 12.0, "curr": 15, "ovp": 13.0, "ocp": 20.0}
    ps.set(setting)
    ps.activateOutput()
    time.sleep(2)
    print ps.measureVolt()
    print ps.measureCurr()
    time.sleep(20)
    ps.deactivateOutput()

    # print "###ADDR 6###"
    #ps.selectChannel(node=6, ch=1)
    #setting = {"volt": 12.0, "curr": 5, "ovp": 13.0, "ocp": 10.0}
    #ps.set(setting)
    #ps.activateOutput()
    #time.sleep(2)
    #print ps.measureVolt()
    #print ps.measureCurr()
    #time.sleep(2)
    #ps.deactivateOutput()
