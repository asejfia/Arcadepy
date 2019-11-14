'''
Created on Feb 17, 2014

@author: joshua
'''
import unittest
import simevolanalyzer


class Test(unittest.TestCase):


    def testName(self):
        version1 = "0.1.5"
        version2 = "0.13.1.1"
        self.assertTrue(simevolanalyzer.compare(version1, version2) < 0)
        version1 = '0.30.5'
        version2 = '0.3.1'
        self.assertTrue(simevolanalyzer.compare(version1, version2) > 0)
        version1 = "alpha"
        version2 = "beta"
        self.assertTrue(simevolanalyzer.compare(version1, version2) < 0)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()