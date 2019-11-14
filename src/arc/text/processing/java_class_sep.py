'''
Created on Jul 12, 2011

@author: joshua
'''

import os, subprocess, shlex, sys, string, platform, logging
import config

def runClassSeparator():
    subjectsDirMod = string.replace(config.subjectsDir, " ", "\ ")
    command_line = "java -cp lib" + os.sep + "class_separator.jar" + os.pathsep + "lib" + os.sep + "antlr-master-3.3-completejar.jar  manual.Driver " + config.workspaceLoc + os.sep + config.projectDirName + \
    os.sep + 'src' + os.sep + 'main' + os.sep + 'java' + " " + subjectsDirMod + os.sep +  config.projectDirName + os.sep + 'separated'
    logging.debug('platform.system(): ' + platform.system())
    logging.debug('command_line: ' + command_line)
    args = None
    if (platform.system() == 'Windows'):
        args = shlex.split(command_line,posix=False)
    else:
        args = shlex.split(command_line)
    logging.debug('Command to be run: ')
    logging.debug(args)
    p = subprocess.call(args)
    logging.debug('Command return output: ')
    logging.debug(p)
    
def main(argv=None):
    runClassSeparator()

if __name__ == "__main__":
    sys.exit(main())
