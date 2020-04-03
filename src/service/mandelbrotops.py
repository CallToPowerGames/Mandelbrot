#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Denis Meyer
#
# This file is part of the mandelbrot application.
#

"""Mandelbrot - MandelbrotOps"""
# see: https://www.ibm.com/developerworks/community/blogs/jfp/entry/My_Christmas_Gift?lang=en

import os
import logging
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from numba import jit

@jit
def mandelbrot(c, maxiter, horizon=2):
    """Calculates whether given c is in the Mandelbrot set"""
    z = c
    for n in range(maxiter):
        if abs(z) > horizon:
            return n
        z = z * z + c
    return 0

@jit
def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, maxiter):
    """Calculates the whole Mandelbrot set within given boundaries"""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            n3[i, j] = mandelbrot(r1[i] + 1j * r2[j], maxiter)
    return n3

def mandelbrot_set_for_image(xmin, xmax,
                             ymin, ymax,
                             width=10, height=10,
                             maxiter=256,
                             dpi=72):
    """Calculates the whole Mandelbrot set within given boundaries for rendering it to an image"""
    img_width = dpi * width
    img_height = dpi * height
    return mandelbrot_set(xmin, xmax, ymin, ymax,
                          img_width, img_height, maxiter)

def mandelbrot_image(xmin, xmax,
                     ymin, ymax,
                     width=10, height=10,
                     maxiter=512,
                     dpi=72,
                     cmap='hot', gamma=0.3,
                     display_ticks=True):
    """Calculates the whole Mandelbrot set within given boundaries to an image"""
    img_width = dpi * width
    img_height = dpi * height
    mset = mandelbrot_set(xmin, xmax, ymin, ymax,
                          img_width, img_height, maxiter)

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    if display_ticks:
        ticks = np.arange(0, img_width, 3 * dpi)
        x_ticks = xmin + (xmax - xmin) * ticks / img_width
        plt.xticks(ticks, x_ticks)
        y_ticks = ymin + (ymax - ymin) * ticks / img_width
        plt.yticks(ticks, y_ticks)
    else:
        plt.xticks([])
        plt.yticks([])

    norm = colors.PowerNorm(gamma)
    ax.imshow(mset.T, cmap=cmap, origin='lower', norm=norm)

    return fig

def save_image(fig, img_name):
    """Saves a figure to an image"""
    filename = img_name
    fig.savefig(filename)

if __name__ == '__main__':
    # It can be shown that the Mandelbrot set is entirely contained
    # in the region where -2.5 <= x <= 0.5 and -1.25 <= y <= 1.25
    starttime = datetime.now()
    fig = mandelbrot_image(-2.0, 0.5, -1.25, 1.25,
                           width=10, height=10, maxiter=256)
    delta = datetime.now() - starttime
    save_image(fig, os.getcwd() + '/mandelbrot_{}.png'.format(0))
    logging.info('Done processing in {:4.4f} seconds.'
          .format(delta.total_seconds()))
