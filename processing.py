# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import subprocess


def process_image(sourcefile, destfile):
    subprocess.check_call(['convert',
                           '-channel', 'RGB',
                           '-sigmoidal-contrast', '3.5x10%',
                           '-modulate', '100,130,100',
                           '-resize', '1500x1500',
                           '-unsharp', '0x1',
                           sourcefile, destfile])
