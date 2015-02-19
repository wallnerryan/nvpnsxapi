#!/usr/bin/python

import sys
import os
import commands

def cmdrun(cmd):
    status,output = commands.getstatusoutput(cmd);
    return status

def execute(cmd):
    print cmd
    status,output = commands.getstatusoutput(cmd);

    if status :
      sys.stderr.write(output)
      exit(1)

    return status

