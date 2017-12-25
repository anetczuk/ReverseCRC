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
from revcrc.reversecrc import CRCKey
from crc.numbermask import intToASCII



def get_all_substrings(input_string):
    length = len(input_string)
    return [input_string[i:j+1] for i in xrange(length) for j in xrange(i,length)]
  
  

class RevCRCCommon(object):
    '''
    classdocs
    '''


    def __init__(self, crcSize):
        '''
        Constructor
        '''
        self.crcSize = crcSize
    
    
    def findSolutionStrings(self, dataList):
        if len(dataList) < 1: 
            return set()
        
        dataPair = dataList[0]
        retList = self.findSubstringCRC(dataPair[0], dataPair[1])
        
        for i in xrange(1, len(dataList)):
            dataPair = dataList[i]
            keys = self.findSubstringCRC(dataPair[0], dataPair[1])
            print "keys:", keys
            ##retList.intersection( keys )
            retList |= keys
        return retList
            
        
    def findSolutionSubstring(self, dataList):
        if len(dataList) < 1: 
            return set()
        
        dataPair = dataList[0]
        dataString = intToASCII(dataPair[0])
        retList = self.findSubstringCRC(dataString, dataPair[1])
        
        for i in xrange(1, len(dataList)):
            dataPair = dataList[i]
            dataString = intToASCII(dataPair[0])
            keys = self.findSubstringCRC(dataString, dataPair[1])
            ##retList.intersection( keys )
            retList |= keys
        return retList
    
    def findSubstringCRC(self, dataString, crc):
        retList = set()
                    
        length = len(dataString)
        for i in xrange(length):                ## start
            for j in xrange(i,length):          ## end
                substr = dataString[i:j + 1]
                subRet = self.findCRC(substr, crc)
                for key in subRet:
                    key.dataPos = i*8
                    key.dataLen = (j-i+1)*8
                retList |= subRet
            
        return retList
    
    def findSolution(self, dataList):
        if len(dataList) < 1: 
            return set()
        
        dataPair = dataList[0]
        retList = self.findCRCKey(dataPair[0], dataPair[1])
        
        for i in xrange(1, len(dataList)):
            dataPair = dataList[i]
            keys = self.findCRCKey(dataPair[0], dataPair[1])
            retList.intersection( keys )
        return retList
        
    def findCRCKey(self, dataValue, crcNum):
        dataString = intToASCII(dataValue)
        ret = self.findCRC(dataString, crcNum)
        for crcItem in ret:
            crcItem.dataPos = 0
            crcItem.dataLen = len(dataString)*8
        return ret
    
    def findCRC(self, data, crc):
        retList = set()
        if self.crcSize == 8:
            self.checkCRC(data, crc, CRCKey(0x107, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x139, True, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x11D, False, 0xFD, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x107, False, 0x55, 0x55), retList)
            self.checkCRC(data, crc, CRCKey(0x131, True, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x107, True, 0xFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x19B, True, 0x0, 0x0), retList)
        elif self.crcSize == 16:
            self.checkCRC(data, crc, CRCKey(0x18005, True, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x18005, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x18005, False, 0x800D, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x10589, False, 0x0001, 0x0001), retList)
            self.checkCRC(data, crc, CRCKey(0x13D65, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x13D65, False, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, False, 0x0, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x18005, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, True, 0xFFFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, True, 0x554D, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x18BB7, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x1A097, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x18005, True, 0x0, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, True, 0x0, 0xFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x18005, True, 0xFFFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, True, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, False, 0xFFFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x11021, False, 0x1D0F, 0x0), retList)
        elif self.crcSize == 24:
            self.checkCRC(data, crc, CRCKey(0x1864CFB, False, 0xB704CE, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x15D6DCB, False, 0xFEDCBA, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x15D6DCB, False, 0xABCDEF, 0x0), retList)
        elif self.crcSize == 32:
            self.checkCRC(data, crc, CRCKey(0x104C11DB7, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x104C11DB7, False, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x11EDC6F41, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x1A833982B, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0xFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x1814141AB, False, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x104C11DB7, True, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x1000000AF, False, 0x0, 0x0), retList)
        elif self.crcSize == 64:
            self.checkCRC(data, crc, CRCKey(0x1000000000000001B, True, 0x0, 0x0), retList)
            self.checkCRC(data, crc, CRCKey(0x142F0E1EBA9EA3693, False, 0x0, 0xFFFFFFFFFFFFFFFF), retList)
            self.checkCRC(data, crc, CRCKey(0x1AD93D23594C935A9, True, 0xFFFFFFFFFFFFFFFF, 0x0), retList)
        return retList


    def checkCRC(self, dataString, crc, crcKey, retList):
        crc_func = crcmod.mkCrcFun(crcKey.poly, rev=crcKey.rev, initCrc=crcKey.init, xorOut=crcKey.xor)
        polyCRC  = crc_func( dataString )
        ##print "comp:", polyCRC, crc
        if polyCRC == crc:
            retList.add( crcKey )
        

