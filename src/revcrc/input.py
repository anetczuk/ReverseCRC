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


import logging
import os.path
import re



class InputData:
    def __init__(self, stringList):
        self.stringData = stringList          ## list of pairs
        self.numbersList = []
        self.dataSize = 0
        self.crcSize = 0
    
    def empty(self):
        return len(self.stringData) < 1
    
    def ready(self):
        return ((self.dataSize>0) and (self.crcSize>0))
        
    def convert(self):
        self.numbersList = []
        self.dataSize = 0
        self.crcSize = 0
        for i in range(0, len(self.stringData)):
            dataPair = self.stringData[i]
            dataString = dataPair[0]
            crcString = dataPair[1]
            self.dataSize = max( self.dataSize, len(dataString)*4 )
            self.crcSize = max( self.crcSize, len(crcString)*4 )
            data = int(dataString, 16)
            crc = int(crcString, 16)
            self.numbersList.append((data, crc))
    
    
class DataParser:
    def __init__(self):
        self.data = []          ## list of pairs
    
    ## data is a list of pairs
    def parseFile(self, path):
        self.data = []
        if not os.path.exists(path):
            ## file not exists
            logging.info("file '{}' not exists".format(path))
            return self.data
        if os.path.getsize(path) < 1:
            ## file is empty
            logging.info("file '{}' is empty".format(path))
            return self.data
        
        logging.info("Opening log file: {}".format(path))
        with open(path, 'r') as f:
            for line in f:
                self.parse( line )
        return self.data


    def parse(self, msg):
        trimmed = msg.strip()
        if len(trimmed) < 1:
            return
        if trimmed[0] == '#':
            ## comment
            return
        if trimmed.startswith( '//' ):
            ## comment
            return
        retList = re.findall('(\S+)\s+(\S+)\s*', trimmed)
        for pair in retList:
            ##val = int(pair[1], 16)
            ##self.data.append( (pair[0], val) )
            self.data.append( (pair[0], pair[1]) )
