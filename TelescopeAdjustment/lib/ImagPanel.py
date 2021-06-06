#! /usr/bin/env python

"""
Image panel is described here
"""

import tkinter as Tk
import pylab
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib import rc

try:
    import pyfits
except ImportError:
    from astropy.io import fits as pyfits

rc('text', usetex=False)


class ImagPanel(Tk.Frame):
    def __init__(self, window):
        self.window = window
        # Find figure axis ratio
        x_to_y_size_ratio = self.window.camera.resolution_x / self.window.camera.resolution_y
        xFigSize = 5.5  # inches
        yFigSize = xFigSize / x_to_y_size_ratio
        self.mainGraph = pylab.Figure(figsize=(xFigSize, yFigSize), dpi=100)
        self.mainGraph.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98, wspace=0, hspace=0)
        self.canvas = FigureCanvasTkAgg(self.mainGraph, master=self.window.root)
        self.fig = self.mainGraph.add_subplot(111)
        self.fig.axes.set_xticks([])
        self.fig.axes.set_yticks([])
        self.fitsPlotInstance = None
        self.objPlotInstance = None
        self.standartsPlotIntance = []
        self.objPairPlotInstance = None
        self.standartsPairPlotInstance = []
        self.hotPixelsPlotInstance = []
        self.messagePlotInstance = None

        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=0)

    def remove_objects_from_plot(self, updateFigure=False):
        if self.objPlotInstance:
            self.objPlotInstance.remove()
            self.objPlotInstance = None
        while self.standartsPlotIntance:
            self.standartsPlotIntance.pop().remove()
        if self.objPairPlotInstance:
            self.objPairPlotInstance.remove()
            self.objPairPlotInstance = None
        while self.standartsPairPlotInstance:
            self.standartsPairPlotInstance.pop().remove()
        while self.hotPixelsPlotInstance:
            self.hotPixelsPlotInstance.pop().remove()
        if self.messagePlotInstance is not None:
            self.messagePlotInstance.remove()
            self.messagePlotInstance = None
        if updateFigure:
            self.canvas.draw()

    def plot_fits_file(self, fitsName):
        if self.fitsPlotInstance:
            # remove previous plot if exists
            self.fitsPlotInstance.remove()
            self.fitsPlotInstance = None
        hdu = pyfits.open(fitsName)
        data = hdu[0].data.copy()
        hdu.close()
        ySize, xSize = data.shape
        meanValue = np.mean(data)
        stdValue = np.std(data)
        maxValue = meanValue + 2*stdValue
        self.fitsPlotInstance = self.fig.imshow(data, interpolation='gaussian', cmap='gray',
                                                vmin=meanValue, vmax=maxValue)
        # self.fig.axis([0, xSize, ySize, 0])  # 180 degrees rotated image
        self.fig.axis([xSize, 0, 0, ySize])
        self.canvas.draw()

    def plot_objects(self, reference, polarMode=None, hotPixels=[]):
        self.remove_objects_from_plot()
        circSize = 7.5
        circWidth = 1.25
        if reference.objSEParams is not None:
            xCoord = reference.objSEParams["X_IMAGE"] - 1
            yCoord = reference.objSEParams["Y_IMAGE"] - 1
            self.objPlotInstance = self.fig.plot([xCoord], [yCoord], marker="o", markerfacecolor="none",
                                                 markersize=circSize, markeredgewidth=circWidth, markeredgecolor="r")[0]
        else:
            self.objPlotInstance = self.fig.plot([reference.xObjObs-1], [reference.yObjObs-1], marker="o",
                                                 markerfacecolor="none", markersize=circSize, markeredgewidth=circWidth,
                                                 markeredgecolor="0.75")[0]

        for st in reference.standartsObs:
            if st['seParams'] is None:
                stx = st['xCen']-1
                sty = st['yCen']-1
                markColor = "0.75"
            else:
                stx = st['seParams']["X_IMAGE"]-1
                sty = st['seParams']["Y_IMAGE"]-1
                markColor = "g"
            self.standartsPlotIntance.append(self.fig.plot([stx], [sty], marker="o", markerfacecolor="none",
                                                           linestyle="", markersize=circSize, markeredgewidth=circWidth,
                                                           markeredgecolor=markColor)[0])

        if polarMode:
            if reference.objPairSEParams is not None:
                self.objPairPlotInstance = self.fig.plot([reference.objPairSEParams["X_IMAGE"]-1],
                                                         [reference.objPairSEParams["Y_IMAGE"]-1],
                                                         marker="o", markerfacecolor="none", markersize=circSize,
                                                         markeredgewidth=circWidth, markeredgecolor="r")[0]
            else:
                self.objPairPlotInstance = self.fig.plot([reference.xObjPairObs-1],
                                                         [reference.yObjPairObs-1],
                                                         marker="o", markerfacecolor="none", markersize=circSize,
                                                         markeredgewidth=circWidth, markeredgecolor="0.75")[0]

            for st in reference.standartPairsObs:
                if st['seParams'] is None:
                    stx = st['xCen']-1
                    sty = st['yCen']-1
                    markColor = "0.75"
                else:
                    stx = st['seParams']["X_IMAGE"]-1
                    sty = st['seParams']["Y_IMAGE"]-1
                    markColor = "g"
                self.standartsPairPlotInstance.append(self.fig.plot([stx], [sty], marker="o", markerfacecolor="none",
                                                                    linestyle="", markersize=circSize,
                                                                    markeredgewidth=circWidth, markeredgecolor="g")[0])

        # plot hot pixels
        if self.window.params.get('show_hot_pixels') is True:
            self.hotPixelsPlotInstance.append(self.fig.plot(hotPixels[1], hotPixels[0], marker="x", markersize=5,
                                                            markeredgecolor="b", markerfacecolor="b",
                                                            markeredgewidth=1, linestyle="")[0])
        self.canvas.draw()

    def show_message(self, message):
        self.remove_objects_from_plot()
        if self.fitsPlotInstance:
            # remove previous plot if exists
            self.fitsPlotInstance.remove()
            self.fitsPlotInstance = None
        self.messagePlotInstance = self.fig.text(x=0.5, y=0.5, s=message, ha='center',
                                                 fontsize=16, transform=self.fig.transAxes)
        self.canvas.draw()
