#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Denis Meyer
#
# This file is part of the mandelbrot application.
#

"""Mandelbrot - MandelbrotGUI"""

import sys
import logging
import tkinter as tk
from tkinter import font
from math import fabs
import numpy as np
import matplotlib
matplotlib.use('TkAgg') # fix macOS crash
from matplotlib import colors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from threads.guiworker import GUIWorker
from i18n.translations import Translations

class MandelbrotGUI(tk.Frame):
    """Main application GUI"""

    def __init__(self,
                 xmin=-2.0, xmax=0.5,
                 ymin=-1.25, ymax=1.25,
                 width=10, height=10,
                 maxiter=512,
                 dpi=75,
                 cmap='hot', gamma=0.3,
                 zoomfactor=0.7,
                 show_axes=False, show_orig_axes=False):
        tk.Frame.__init__(self)
        
        logging.info('Initializing')
        logging.info('Parameters: xmin=-2.0, xmax=0.5, ymin={}, ymax={}, width={}, height={}, maxiter={},  dpi={}, cmap={}, gamma={}, zoomfactor={}, show_axes={}, show_orig_axes={}'
        .format(xmin, xmax,
                 ymin, ymax,
                 width, height,
                 maxiter, dpi,
                 cmap, gamma,
                 zoomfactor, show_axes,
                 show_orig_axes))

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.width = width
        self.height = height
        self.maxiter = maxiter
        self.dpi = dpi
        self.cmap = cmap
        self.gamma = gamma
        self.show_axes = show_axes
        self.show_orig_axes = show_axes and show_orig_axes

        self.img_width = dpi * self.width
        self.img_height = dpi * self.height
        self.processing = False

        self.curr_zoomlvl = 0
        self.zoomfactor_in = zoomfactor
        self.zoomfactor_out = 1 / self.zoomfactor_in
        self._set_currdata(self.xmin, self.ymin, self.xmax, self.ymax)

        self.mset = None
        self.fig = None
        self.subplot = None
        self.canvas = None
        self.font_text_status = None
        self.text_status = None

        self.translations = Translations()

    def display(self):
        """Initializes the GUI and starts the main loop"""
        logging.info('Displaying')
        self._initgui()
        logging.info('Starting main loop')
        self.mainloop()

    def _set_currdata(self, xmin, ymin, xmax, ymax):
        """Sets the current data by values"""
        self._set_currdata_d((xmin, ymin, xmax, ymax))
        self._calc_cd_wh()

    def _set_currdata_d(self, data):
        """Sets the current data by tuple"""
        self.currdata = data
        self._calc_cd_wh()

    def _calc_cd_wh(self):
        """Calculates the current width and height"""
        self.cd_width = fabs(self.currdata[0] - self.currdata[2])
        self.cd_height = fabs(self.currdata[1] - self.currdata[3])

    def _center(self):
        """Centers the window"""
        logging.debug('Centering window')
        self.master.update_idletasks()
        width = self.master.winfo_width()
        frm_width = self.master.winfo_rootx() - self.master.winfo_x()
        win_width = width + 2 * frm_width
        height = self.master.winfo_height()
        titlebar_height = self.master.winfo_rooty() - self.master.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.master.winfo_screenwidth() // 2 - win_width // 2
        y = self.master.winfo_screenheight() // 2 - win_height // 2
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.master.resizable(width=False, height=False)
        self.master.deiconify()

    def _calc_mandelbrot_callback(self, mset, starttime, endtime):
        """Callback when Mandebrot calculation is done"""
        delta = endtime - starttime
        logging.info('Done calculating mandelbrot in {:4.4f} seconds.'
                .format(delta.total_seconds()))

        self.mset = mset
        if self.subplot:
            self.subplot.cla()
        self.subplot = self.fig.add_subplot(111)

        self.subplot.set_xticks([])
        self.subplot.set_yticks([])
        if self.show_axes:
            if not self.show_orig_axes:
                ticks = np.arange(0, self.img_width, 3 * self.dpi)
                tmp_x = (self.currdata[2] - self.currdata[0])
                x_ticks = self.currdata[0] + tmp_x * ticks / self.img_width
                self.subplot.set_xticklabels(x_ticks)
                self.subplot.set_xticks(ticks)
                tmp_y = (self.currdata[3] - self.currdata[1])
                y_ticks = self.currdata[1] + tmp_y * ticks / self.img_width
                self.subplot.set_yticklabels(y_ticks)
                self.subplot.set_yticks(ticks)

        norm = colors.PowerNorm(self.gamma)
        self.subplot.imshow(mset.T, cmap='hot', origin='lower', norm=norm)
        self.canvas.draw_idle()
        self._update_text_status(self.translations.get('STATUS.PROCESSING_DONE')
                                 .format(delta.total_seconds()))
        logging.debug('Done processing...')
        self.processing = False

    def _calc_mandelbrot(self):
        """Starts Mandelbrot calculation in a separate thread"""
        logging.debug('Starting processing...')
        self._update_text_status(self.translations.get('STATUS.PROCESSING'))
        self.update() # Force text update
        guiworker = GUIWorker(callback=self._calc_mandelbrot_callback,
                              xmin=self.currdata[0], xmax=self.currdata[2],
                              ymin=self.currdata[1], ymax=self.currdata[3],
                              width=self.width, height=self.height,
                              maxiter=self.maxiter,
                              dpi=self.dpi)
        guiworker.start()

    # Coordinates
    #
    # (0, 750) ~= (-2.0,  1.25)      (750, 750) ~= ( 0.5,  1.25)
    #
    # (0,   0) ~= (-2.0, -1.25)      (750,   0) ~= (-2.0, -1.25)
    def _transform_coords(self, coords):
        """
        Transforms the coordinates from a click event on a plot.


        The math behind it:
        Rectangle 1 has (x1, y1) origin and (w1, h1) for width and height, and
        Rectangle 2 has (x2, y2) origin and (w2, h2) for width and height, then

        Given point (x, y) in terms of Rectangle 1 coords, to convert it to Rectangle 2 coords:

        xNew = ((x-x1)/w1)*w2+x2
        yNew = ((y-y1)/h1)*h2+y2


        Example:
        R1: (x1 =  0  , y1 =  0   ) origin, (w1 = 750  , h1 = 750  ) width/height
        R2: (x2 = -2.0, y2 = -1.25) origin, (w2 =   2.5, h2 =   2.5) width/height

        Point (x = 0, y = 0)
        xNew = ((0-0)/750)*2.5+-2.0  = -2
        yNew = ((0-0)/750)*2.5+-1.25 = -1.25

        Point (x = 750, y = 750)
        xNew = ((750-0)/750)*2.5+-2.0  = 0.5
        yNew = ((750-0)/750)*2.5+-1.25 = 1.25
        """
        x1, y1, w1, h1 = (0, 0, self.width * self.dpi, self.height * self.dpi)
        x2, y2, w2, h2 = (self.currdata[0], self.currdata[1], self.cd_width, self.cd_height)

        x_new = ((coords[0] - x1) / w1) * w2 + x2
        y_new = ((coords[1] - y1) / h1) * h2 + y2

        logging.debug('Transform coordinates')
        logging.debug('x, y: {}'.format(coords))
        logging.debug('width: {}, height: {}'
                .format(self.cd_width, self.cd_height))
        logging.debug('x1: {}, y1: {}, w1: {}, h1: {}'
                .format(x1, y1, w1, h1))
        logging.debug('x2: {}, y2: {}, w2: {}, h2: {}'
                .format(x2, y2, w2, h2))

        return (x_new, y_new)

    def _calc_new_coordinates_around(self, coords):
        """Calculates new rectangle position around the given coordinate


        The math behind it:
        newXMin = x - width / 2
        newYMin = y - height / 2
        newXMax = newXMin + width
        newYMax = newYMIn + height


        Example:
        (x = -0.75, y = 0) -> (-0.75-2.5/2, 0-2.5/2), (-2+2.5, -1.25+2.5) = (-2, -1.25), (0.5, 1.25)
        """
        xmin_new = coords[0] - (self.cd_width / 2)
        ymin_new = coords[1] - (self.cd_height / 2)
        xmax_new = xmin_new + self.cd_width
        ymax_new = ymin_new + self.cd_height

        logging.debug('Calculate new coordinates around')
        logging.debug('x, y: {}'.format(coords))
        logging.debug('width: {}, height: {}'
                .format(self.cd_width, self.cd_height))
        logging.debug('xmin: {}, ymin: {}, xmax: {}, ymax: {}'
                .format(xmin_new, ymin_new, xmax_new, ymax_new))

        return (xmin_new, ymin_new, xmax_new, ymax_new)

    def _button_released(self, event):
        logging.debug('Button pressed')
        if event.button == 1:
            self._button_mouse1_released(event)
        elif event.button == 3:
            self._button_mouse3_released(event)
        elif event.button == 'up':
            self._button_mousescrollup(event)
        elif event.button == 'down':
            self._button_mousescrolldown(event)
        else:
            logging.info('Unregistered button released: {}'.format(event.button))

    def _key_released(self, event):
        logging.debug('Key released')
        if event.key == '+':
            self._button_mousescrolldown(event)
        elif event.key == '-':
            self._button_mousescrollup(event)

    def _apply_zoomin(self):
        """Zooms in"""
        logging.debug('Zooming in')
        mid = (self.currdata[0] + (self.cd_width / 2),
               self.currdata[1] + (self.cd_height / 2))
        wval = self.cd_width / 2 * self.zoomfactor_in
        hval = self.cd_height / 2 * self.zoomfactor_in
        self._set_currdata(mid[0] - wval,
                           mid[1] - hval,
                           mid[0] + wval,
                           mid[1] + hval)

    def _apply_zoomout(self):
        """Zooms out"""
        logging.debug('Zooming out')
        mid = (self.currdata[0] + (self.cd_width / 2),
               self.currdata[1] + (self.cd_height / 2))
        wval = self.cd_width / 2 * self.zoomfactor_out
        hval = self.cd_height / 2 * self.zoomfactor_out
        self._set_currdata(mid[0] - wval,
                           mid[1] - hval,
                           mid[0] + wval,
                           mid[1] + hval)

    def _button_mouse1_released(self, event):
        """On mouse button 1 released"""
        logging.debug('Mouse 1 released')
        if not self.processing:
            if event.inaxes is not None:
                self.processing = True
                trans_coords = self._transform_coords((event.xdata, event.ydata))
                new_coords = self._calc_new_coordinates_around(trans_coords)
                self._set_currdata_d(new_coords)
                self._calc_mandelbrot()
        else:
            logging.debug('Already processing...')

    def _button_mouse3_released(self, event):
        """On mouse button 3 released"""
        logging.debug('Mouse 3 released')
        if not self.processing:
            self.processing = True
            self._set_currdata(self.xmin,
                               self.ymin,
                               self.xmax,
                               self.ymax)
            self.curr_zoomlvl = 0
            self._calc_mandelbrot()
        else:
            logging.debug('Already processing...')

    def _button_mousescrollup(self, event):
        """On mouse scroll up"""
        logging.debug('Mouse scrolled up')
        if not self.processing:
            self.processing = True
            self._apply_zoomout()
            self.curr_zoomlvl -= 1
            self._calc_mandelbrot()
        else:
            logging.debug('Already processing...')

    def _button_mousescrolldown(self, event):
        """On mouse scroll down"""
        logging.debug('Mouse scrolled down')
        if not self.processing:
            self.processing = True
            self._apply_zoomin()
            self.curr_zoomlvl += 1
            self._calc_mandelbrot()
        else:
            logging.debug('Already processing...')

    def _create_canvasbinding(self):
        """Binds actions to the canvas"""
        logging.debug('Creating canvas binding')
        self.canvas.callbacks.connect('button_release_event', self._button_released)
        self.canvas.callbacks.connect('key_release_event', self._key_released)
        self.canvas.callbacks.connect('scroll_event', self._button_released)

    def _update_text_status(self, txt):
        """Updates the loading label text"""
        _txt = '\n' + self.translations.get('APP.CURRZOOMLVL').format(self.curr_zoomlvl)
        _txt += '\n' + self.translations.get('APP.HELP')
        _txt += '\n' + self.translations.get('APP.STATUS').format(txt)
        self.canvas_text.itemconfig(self.text_status, text=_txt)

    def _create_canvas(self):
        """Creates the canvas to draw on"""
        logging.info('Creating canvas')
        self.fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0,
                                         column=0,
                                         sticky=tk.N+tk.E+tk.S+tk.W)
        self.canvas_text = tk.Canvas(width=self.img_width,
                                     height=100,
                                     bg='#FFFFFF')
        self.canvas_text.grid(row=1, column=0,
                              sticky=tk.S)
        self.font_text_status = font.Font(family='Helvetica',
                                          size='14',
                                          weight='normal')
        self.text_status = self.canvas_text.create_text(self.img_width / 2,
                                                        45,
                                                        anchor=tk.CENTER,
                                                        text=self.translations.get('STATUS.PROCESSING'),
                                                        font=self.font_text_status)

    def _doquit(self):
        """Destroys the window and quits"""
        logging.info('Quitting')
        self.quit()
        self.destroy()
        sys.exit(0)

    def _registercommands(self):
        """Registers some commands on special events, e.g. 'exit'"""
        logging.info('Registering commands')
        self.master.createcommand('exit', self._doquit)
        self.master.protocol('WM_DELETE_WINDOW', self._doquit)

    def _configureproperties(self):
        """Configures frame properties"""
        logging.info('Configuring properties')
        self.master.title(self.translations.get('APP.TITLE'))
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=9)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=tk.N+tk.E+tk.S+tk.W, padx=0, pady=0)

    def _initgui(self):
        """Initializes the GUI"""
        logging.info('Init GUI (internal)')
        self._configureproperties()
        self._registercommands()
        self._create_canvas()
        self._create_canvasbinding()
        self._center()
        self._calc_mandelbrot()
