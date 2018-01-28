# MIT License
# 
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


# import logging
from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC
from revcrc.hwcrcbackward import HwCRCBackward
from revcrc.divisioncrcbackward import DivisionCRCBackward
from revcrc.reverse import Reverse

    

##
##
class BackwardReverse(Reverse):
    
    ## crcSize  -- size of crc in bits
#     def __init__(self, crcSize, printProgress = None):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)
        
    def createBackwardCRCProcessor(self, dataMask, crc):
        raise NotImplementedError
    
    
## =========================================================================
    
    
class RevHwCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return HwCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc):        
        return HwCRCBackward( dataMask, crc )
    
    
class RevDivisionCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return DivisionCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc):     
        return DivisionCRCBackward( dataMask, crc )
    
    
class RevModCRC(Reverse):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return ModCRC()        

    