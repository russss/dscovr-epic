# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import subprocess


def process_image(sourcefile, destfile):
    subprocess.check_call(['convert',
                           '-channel', 'B', '-gamma', '0.95',
                           '-channel', 'R', '-gamma', '0.98',
                           '-channel', 'RGB',
                           '-sigmoidal-contrast', '3.6x6%',
                           '-modulate', '100,140,100',
                           '-resize', '1500x1500',
                           '-unsharp', '0x1',
                           sourcefile, destfile])
