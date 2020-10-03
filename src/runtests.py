#!/usr/bin/python
#
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

import unittest
import re
import argparse
import cProfile
import subprocess

try:
    import coverage
except ImportError:
    print "Missing coverage module. Try running 'pip install coverage'"
    raise

import os
import tempfile
import logging


script_dir = os.path.dirname(os.path.abspath(__file__))


_LOGGER = logging.getLogger(__name__)


def match_tests( pattern ):
    if pattern.find("*") < 0:
        ## regular module
        loader = unittest.TestLoader()
        return loader.loadTestsFromName( pattern )

    ## wildcarded
    rePattern = pattern
    # pylint: disable=W1401
    rePattern = rePattern.replace(".", "\.")
    rePattern = rePattern.replace("*", ".*")
    ## rePattern = "^" + rePattern + "$"
    _LOGGER.info( "searching test cases with pattern: %s", rePattern )
    loader = unittest.TestLoader()
    testsSuite = loader.discover( script_dir )
    return match_test_suites(testsSuite, rePattern)


def match_test_suites( testsList, rePattern ):
    retSuite = unittest.TestSuite()
    for testObject in testsList:
        if isinstance(testObject, unittest.TestSuite):
            subTests = match_test_suites( testObject, rePattern )
            retSuite.addTest( subTests )
            continue
        if isinstance(testObject, unittest.TestCase):
            classobj         = testObject.__class__
            # pylint: disable=W0212,
            testCaseFullName = ".".join([ classobj.__module__, classobj.__name__,
                                          testObject._testMethodName ] )
            matched = re.search(rePattern, testCaseFullName)
            if matched is not None:
                ## _LOGGER.info("test case matched: %s", testCaseFullName )
                retSuite.addTest( testObject )
            continue
        _LOGGER.warning("unknown type: %s", type( testObject ))
    return retSuite


## ============================= main section ===================================


if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description='Test runner')
    # pylint: disable=C0301
    parser.add_argument('-rt', '--runtest', action='store', required=False, default="",
                        help='Module with tests, e.g. module.submodule.test_file.test_class.test_method, wildcard * allowed' )
    parser.add_argument('-r', '--repeat', action='store', type=int, default=0, help='Repeat tests given number of times' )
    parser.add_argument('-ut', '--untilfailure', action="store_true", help='Run tests in loop until failure' )
    parser.add_argument('-cov', '--coverage', action="store_true", help='Measure code coverage' )
    parser.add_argument('--profile', action="store_true", help='Profile the code' )
    parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )
    
    args = parser.parse_args()
    
    
    coverageData = None
    ## start code coverage
    if args.coverage == True:
        print "Executing code coverage"
        currScript = os.path.realpath(__file__)
        coverageData = coverage.Coverage(branch=True, omit=currScript)
        ##coverageData.load()
        coverageData.start()
        
        
    if args.runtest:
        ## not empty
        suite = match_tests( args.runtest )
    else:
        testsLoader = unittest.TestLoader()
        suite = testsLoader.discover( script_dir )
        

    testsRepeats = int(args.repeat)

    profiler = None

    try:
        ## start code profiler
        profiler_outfile = args.pfile
        if args.profile == True or profiler_outfile != None:
            print "Starting profiler"
            profiler = cProfile.Profile()
            profiler.enable()
            
        ## run proper tests
        if args.untilfailure == True:
            counter = 1
            while True:
                print "Tests iteration:", counter
                counter += 1
                testResult = unittest.TextTestRunner().run(suite)
                if testResult.wasSuccessful() == False:
                    break;
                print "\n"
        elif testsRepeats > 0:
            for counter in xrange(1, testsRepeats+1):
                print "Tests iteration:", counter
                testResult = unittest.TextTestRunner().run(suite)
                if testResult.wasSuccessful() == False:
                    break;
                print "\n"
        else:
            unittest.TextTestRunner().run(suite)
    
    finally:
        ## stop profiler            
        if profiler != None:
            profiler.disable()
            if profiler_outfile == None:
                print "Generating profiler data"
                profiler.print_stats(1)
            else:
                print "Storing profiler data to", profiler_outfile
                profiler.dump_stats( profiler_outfile )

            if profiler_outfile != None:
                ##pyprof2calltree -i $PROF_FILE -k
                print "Launching: pyprof2calltree -i {} -k".format(profiler_outfile)
                subprocess.call(["pyprof2calltree", "-i", profiler_outfile, "-k"])
        
        ## prepare coverage results
        if coverageData != None:
            ## convert results to html
            tmprootdir=tempfile.gettempdir()
            revCrcTmpDir=tmprootdir+"/revcrc"
            if not os.path.exists(revCrcTmpDir):
                os.makedirs(revCrcTmpDir)
            htmlcovdir=revCrcTmpDir+"/htmlcov"
            
            coverageData.stop()
            coverageData.save()
            coverageData.html_report(directory=htmlcovdir)
            print "\nCoverage HTML output:", (htmlcovdir+"/index.html")

        