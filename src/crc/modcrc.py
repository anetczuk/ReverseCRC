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

from crc.crcproc import CRCProcessor, CRCProcessorFactory
import crcmod


class CRCModCacheMap(object):
    """Caching results of 'crcmod.mkCrcFun()' gives huge performance boost."""

    def __init__(self):
        self.map = dict()

    def getFunction(self, crcKey):
        if crcKey in self.map:
            return self.map[crcKey]
#         print "Creating new function for", crcKey
        crc_func = crcmod.mkCrcFun(crcKey.poly, rev=crcKey.rev, initCrc=crcKey.init, xorOut=crcKey.xor)
        self.map.update( [(crcKey, crc_func)] )
        return crc_func


## ===================================================================


class ModCRCProcessorFactory( CRCProcessorFactory ):

    # crcSize -- int, number of bits
    # return CRCProcessor
    def createForwardProcessor(self, crcSize=None):
        return ModCRC()

    # crcSize -- int, number of bits
    # return CRCInvertProcessor
    def createInvertProcessor(self, crcSize=None):
        raise NotImplementedError( "ModCRC -- not implemented" )

    # crcSize -- int, number of bits
    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCDataOperator
    def createDataOperator(self, crcSize, inputData):
        raise NotImplementedError( "ModCRC -- not implemented" )


## ===================================================================


##
## Compatible with crcmod library
##
class ModCRC( CRCProcessor ):

    def __init__(self):
        CRCProcessor.__init__(self)

#     def setInitCRC(self, value, crcSize):
#         self.registerInit = value ^ self.xorOut
#         if self._reversed == True:
#             self.registerInit = reverse_number(self.registerInit, crcSize)

    def calculate3(self, dataMask, polyMask):
        ## crcmod requires leading '1' bit
        poly = polyMask.dataNum | polyMask.masterBit
        currXor = self.xorOut & polyMask.dataMask
        initReg = self.registerInit ^ currXor
        crc_func = crcmod.mkCrcFun(poly, rev=self._reversed, initCrc=initReg, xorOut=currXor)
#         crcKey = CRCKey(poly, self.registerInit, currXor, rev=self._reversed)
#         crc_func = CRCModCacheMap.instance.getFunction(crcKey)
        dataString = dataMask.toASCII()
        polyCRC  = crc_func( dataString )
        return polyCRC

#         if self._reversed == False:
#             return self.calculateMSB(dataMask, polyMask)
#         else:
#             revData = dataMask.reorderedBytes()
#             revPoly = polyMask.reversed()
#             return self.calculateLSB(revData, revPoly)
# #             return self.calculateLSB(dataMask, poly)
