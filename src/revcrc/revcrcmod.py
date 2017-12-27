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


import crcmod
from revcrc.reverse import Reverse, MessageCRC, CRCKey
from crc.numbermask import intToASCII
import itertools



class RevCRCMod(Reverse):
    '''
    Uses crcmod library to check CRC configurations.
    '''


    def __init__(self, printProgress = None):
        '''
        Constructor
        '''
        Reverse.__init__(self, printProgress)
    
    def findSolution(self, dataList, dataSize, crcSize, searchRange = 0):
        if len(dataList) < 2:
            return []
        
        retList = []
        comb = list( itertools.combinations( dataList, 2 ) )
        
        cLen = len(comb)
        for i in range(0, cLen):
            combPair = comb[i]
            dataPair1 = combPair[0]
            dataPair2 = combPair[1]
            
            data1 = dataPair1[0]
            crc1 = dataPair1[1]
            data2 = dataPair2[0]
            crc2 = dataPair2[1]
            keys = self.findCRCKey(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
            
            retList += keys
            
        return retList
    
    def findCRCKey(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange=0):
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X}".format(data1, crc1, data2, crc2)
            
        xorData = data1 ^ data2
        diffLength = xorData.bit_length()
        xorCRC = crc1 ^ crc2
        dataCrc = MessageCRC(xorData, diffLength, xorCRC, crcSize)
        polyList = self.bruteForce3(dataCrc)
        
        dataString1 = intToASCII(data1)
        dataString2 = intToASCII(data2)
        regMax = 1 << crcSize
        
        if self.progress:
            print "found polys:", polyList
    
        retList = []
        for poly in polyList:
            polyAdded = False
#             print "checking poly: {:X}".format( poly )
            for initReg in xrange(0, regMax):
#                 print "checking init: {:b}".format( initReg )
                for xorReg in xrange(0, regMax):
                    verifyCrc1 = self.calculateStringCRC(poly, False, initReg, xorReg, dataString1 )
                    if (verifyCrc1 != crc1):
                        continue
                        
                    verifyCrc2 = self.calculateStringCRC(poly, False, initReg, xorReg, dataString2 )
                    if (verifyCrc2 != crc2):
                        continue
                    
                    ret = CRCKey()
                    ret.poly = poly
                    ret.init = initReg
                    ret.xor = xorReg
                    ret.dataPos = 0
                    ret.dataLen = data1.bit_length()
                    retList.append(ret)
                    polyAdded = True
                    if self.returnFirst == True:
                        return retList
                     
            if polyAdded == False:
                ret = CRCKey()
                ret.poly = poly
                retList.append(ret)
                
        return retList
    
    def calculateStringCRC(self, poly, reverse, initReg, xorOut, data):
        #TODO: non-zero 'initReg' not supported
        #TODO: non-zero 'xorOut' not supported
        crc_func = crcmod.mkCrcFun(poly, rev=reverse, initCrc=initReg, xorOut=xorOut)
        return crc_func( data )
#         crc_func = crcmod.Crc(poly, rev=reverse, initCrc=initReg, xorOut=xorOut)
#         crc_func.update( data )
#         return crc_func.crcValue
