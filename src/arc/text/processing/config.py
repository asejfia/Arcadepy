'''
Created on Jun 9, 2011

@author: joshua
'''

import ConfigParser
import unittest
import os

class Langs:
    java, cpp, cfunc, cfile = range(4)

workspaceLoc = subjectsDir = projectDirName = ''
langType = Langs.cfile
configFilename = 'cfg//main.cfg'

def get_config_from_filename():
    global langType, configFilename, workspaceLoc, subjectsDir, projectDirName
    config = ConfigParser.RawConfigParser()
    config.read(configFilename)
    print os.getcwd()
    print config.sections()
    workspaceLoc = str(config.get('Main','workspace_location'))
    subjectsDir =  str(config.get('Main','subjects_dir'))
    projectDirName = str(config.get('Main','projectDirName'))
    lang = str(config.get('Main','lang'))
    if lang == 'java':
        langType = Langs.java
    if lang == 'cpp':
        langType = Langs.cpp
    if lang == 'cfunc':
        langType = Langs.cfunc
    if lang == 'cfile':
        langType = Langs.cfile
    
class TestSequenceFunctions(unittest.TestCase):

    def test_get_config_from_filename(self):
        get_config_from_filename()
    
    