#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the mandelbrot application.
#

import logging
from gui.gui import MandelbrotGUI

"""Mandelbrot - Main"""

SETTINGS = {
    'xmin': -2.0,
    'xmax': 0.5,
    'ymin': -1.25,
    'ymax': 1.25,
    'width': 10,
    'height': 10,
    'maxiter': 128,
    'dpi': 75,
    'cmap': 'hot',
    'gamma': 0.3,
    'zoomfactor': 0.7,
    'show_axes': False,
    'show_orig_axes': False,
    # Logging configuration
    'logging': {
        'loglevel': logging.INFO,
        'date_format': '%Y-%m-%d %H:%M:%S',
        'format': '[%(asctime)s] [%(levelname)-5s] [%(module)-20s:%(lineno)-4s] %(message)s'
    }
}

def initialize_logger(loglevel, frmt, datefmt):
    '''Initializes the logger

    :param loglevel: The log level
    :param frmt: The log format
    :param datefmt: The date format
    '''
    logging.basicConfig(level=loglevel, format=frmt, datefmt=datefmt)

if __name__ == '__main__':
    initialize_logger(SETTINGS['logging']['loglevel'], SETTINGS['logging']
                      ['format'], SETTINGS['logging']['date_format'])

    gui = MandelbrotGUI(xmin=SETTINGS['xmin'],
                        xmax=SETTINGS['xmax'],
                        ymin=SETTINGS['ymin'],
                        ymax=SETTINGS['ymax'],
                        width=SETTINGS['width'],
                        height=SETTINGS['height'],
                        maxiter=SETTINGS['maxiter'],
                        dpi=SETTINGS['dpi'],
                        cmap=SETTINGS['cmap'],
                        gamma=SETTINGS['gamma'],
                        zoomfactor=SETTINGS['zoomfactor'],
                        show_axes=SETTINGS['show_axes'],
                        show_orig_axes=SETTINGS['show_orig_axes'])
    gui.display()
