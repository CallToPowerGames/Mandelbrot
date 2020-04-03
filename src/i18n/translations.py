#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Denis Meyer
#
# This file is part of the mandelbrot application.
#

"""Mandelbrot - Translations"""

import logging

class Translations:
    """The translations"""

    _translations = {
        'APP.TITLE': 'Mandelbrot',
        'APP.STATUS': 'Status: {}',
        'APP.CURRZOOMLVL': 'Current zoom level: {}',
        'APP.HELP': 'Left mouse = Move, right mouse = Reset, mouse wheel or +/- keys = zoom in/out',
        'STATUS.PROCESSING': 'Processing...',
        'STATUS.PROCESSING_DONE': 'Done processing in {:4.4f} seconds.'
    }

    def get(self, key, default=''):
        """Returns the value for the given key or - if not found - a default value"""
        try:
            return self._translations[key]
        except KeyError as e:
            logging.warn('Returning default for key \'{}\': {}'.format(key, e))
            return default
