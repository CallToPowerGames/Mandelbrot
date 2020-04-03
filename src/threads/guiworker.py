#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Denis Meyer
#
# This file is part of the mandelbrot application.
#

"""Mandelbropt - GUIWorker"""

from datetime import datetime
import threading
import logging

from service.mandelbrotops import mandelbrot_set_for_image

class GUIWorker(threading.Thread):
    """The GUI worker"""

    def __init__(self,
                 callback=None,
                 xmin=-2.0, xmax=0.5,
                 ymin=-1.25, ymax=1.25,
                 width=10, height=10,
                 maxiter=256,
                 dpi=72):
        threading.Thread.__init__(self)
        self.daemon = True # OK for main to exit even if instance is still running
        self.callback = callback
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.width = width
        self.height = height
        self.maxiter = maxiter
        self.dpi = dpi

    def run(self):
        """Starts the thread"""
        starttime = datetime.now()
        logging.debug('Starting')
        mset = mandelbrot_set_for_image(self.xmin, self.xmax,
                                        self.ymin, self.ymax,
                                        width=self.width, height=self.height,
                                        maxiter=self.maxiter,
                                        dpi=self.dpi)
        logging.debug('Ended')
        endtime = datetime.now()
        if self.callback:
            self.callback(mset, starttime, endtime)
