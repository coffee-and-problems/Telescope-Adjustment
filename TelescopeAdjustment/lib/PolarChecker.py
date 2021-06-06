#! /usr/bin/env python

from math import cos, sin, radians

import tkinter as Tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pylab
import numpy as np


class PolarChecker(Tk.Frame):
    def __init__(self, window):
        self.window = window
        self.top = Tk.Toplevel(window.root)
        # self.top.geometry("500x1000")
        self.yFitsPlotInstance = None
        self.xFitsPlotInstance = None
        self.yObjPlotInstance = None
        self.xObjPlotInstance = None
        self.yStdPlotInstance = []
        self.xStdPlotInstance = []
        self.rotation = 0.0
        self.cosa = 1
        self.sina = 0
        # Find figure axis ratio
        x_to_y_size_ratio = self.window.camera.resolution_x / self.window.camera.resolution_y
        xFigSize = 5.5  # inches
        yFigSize = xFigSize / x_to_y_size_ratio
        # Initialisation of graph for y-mode
        self.yGraph = pylab.Figure(figsize=(xFigSize, yFigSize), dpi=80)
        self.yCanvas = FigureCanvasTkAgg(self.yGraph, master=self.top)
        self.yFig = self.yGraph.add_subplot(111)
        self.yFig.axes.set_xticks([])
        self.yFig.axes.set_yticks([])
        self.yFig.axis([0, self.window.camera.resolution_x, self.window.camera.resolution_y, 0])
        self.yFig.axes.set_title("%s-mode" % self.window.camera.polar_filters[0])
        self.yCanvas.draw()
        self.yCanvas.get_tk_widget().grid(column=0, row=0, columnspan=4)

        # Initialisation of graph for x-mode
        self.xGraph = pylab.Figure(figsize=(xFigSize, yFigSize), dpi=80)
        self.xCanvas = FigureCanvasTkAgg(self.xGraph, master=self.top)
        self.xFig = self.xGraph.add_subplot(111)
        self.xFig.axes.set_xticks([])
        self.xFig.axes.set_yticks([])
        self.xFig.axis([0, self.window.camera.resolution_x, self.window.camera.resolution_y, 0])
        self.xFig.axes.set_title("%s-mode" % self.window.camera.polar_filters[1])
        self.xCanvas.draw()
        self.xCanvas.get_tk_widget().grid(column=0, row=1, columnspan=4)

        # Add some bottons
        self.rotIncButton = Tk.Button(self.top, text="+5 deg", command=lambda: self.rotate(5.0))
        self.rotIncButton.grid(column=0, row=2, pady=10)
        self.rotDecButton = Tk.Button(self.top, text="-5 deg", command=lambda: self.rotate(-5.0))
        self.rotDecButton.grid(column=2, row=2, pady=10)
        self.okButton = Tk.Button(self.top, text="Ok", command=self.top.destroy)
        self.okButton.grid(column=3, row=2, pady=10)

        # Text with current rotation
        self.angleValue = Tk.StringVar()
        self.angleValue.set("0")
        Tk.Label(self.top, textvariable=self.angleValue).grid(column=1, row=2)

        # show catalogue
        self.show_cat()

    def rotate(self, angle):
        self.rotation += angle
        self.angleValue.set("%i" % (int(self.rotation)))
        self.cosa = cos(radians(self.rotation))
        self.sina = sin(radians(self.rotation))
        # Show catalogues
        self.show_cat()

    def clear_fig(self):
        # remove previous plots if exist
        if self.yFitsPlotInstance is not None:
            self.yFitsPlotInstance.remove()
            self.yFitsPlotInstance = None

        if self.xFitsPlotInstance is not None:
            self.xFitsPlotInstance.remove()
            self.xFitsPlotInstance = None

        if self.yObjPlotInstance is not None:
            self.yObjPlotInstance.remove()
            self.yObjPlotInstance = None

        if self.xObjPlotInstance is not None:
            self.xObjPlotInstance.remove()
            self.xObjPlotInstance = None

        while self.yStdPlotInstance:
            self.yStdPlotInstance.pop().remove()
        while self.xStdPlotInstance:
            self.xStdPlotInstance.pop().remove()

    def show_cat(self):
        """ Show catalogue as an image to check if some polar pairs are too close"""
        self.clear_fig()

        # Load camera-specific parameters
        xSize = int(self.window.camera.resolution_x)
        ySize = int(self.window.camera.resolution_y)
        xCen = xSize / 2
        yCen = ySize / 2
        polar_pair_shift_x_dx = self.window.camera.polar_pair_shift[0][0]
        polar_pair_shift_x_dy = self.window.camera.polar_pair_shift[0][1]
        polar_pair_shift_y_dx = self.window.camera.polar_pair_shift[1][0]
        polar_pair_shift_y_dy = self.window.camera.polar_pair_shift[1][1]
        gridX, gridY = np.meshgrid(range(xSize), range(ySize))

        # Create images for x and y mode
        dataY = np.zeros((ySize, xSize))
        dataX = np.zeros((ySize, xSize))
        for obj in self.window.seCat:
            if (obj["FLUX_AUTO"] <= 0) or (obj["FWHM_IMAGE"] <= 0):
                continue
            xObjOrig = obj["X_IMAGE"]
            yObjOrig = obj["Y_IMAGE"]
            # Lets rotate points by angle self.rotation around the centre
            xObj = self.cosa * (xObjOrig-xCen) - self.sina * (yObjOrig-yCen) + xCen
            yObj = self.sina * (xObjOrig-xCen) + self.cosa * (yObjOrig-yCen) + yCen

            xPairY = xObj + polar_pair_shift_y_dx
            yPairY = yObj + polar_pair_shift_y_dy
            xPairX = xObj + polar_pair_shift_x_dx
            yPairX = yObj + polar_pair_shift_x_dy

            r = 3*int(obj["FWHM_IMAGE"])
            # set indexes to work only for part of the image
            idxObj = np.s_[int(yObj)-r:int(yObj)+r+1,
                           int(xObj)-r:int(xObj)+r+1]
            idxPairY = np.s_[int(yPairY)-r:int(yPairY)+r+1,
                             int(xPairY)-r:int(xPairY)+r+1]
            idxPairX = np.s_[int(yPairX)-r:int(yPairX)+r+1,
                             int(xPairX)-r:int(xPairX)+r+1]

            sqDistsObj = np.zeros((ySize, xSize))
            sqDistsPairY = np.zeros((ySize, xSize))
            sqDistsPairX = np.zeros((ySize, xSize))

            sqDistsObj[idxObj] = (gridX[idxObj]-xObj)**2.0 + (gridY[idxObj]-yObj)**2.0
            sqDistsPairY[idxPairY] = (gridX[idxPairY]-xPairY)**2.0 + (gridY[idxPairY]-yPairY)**2.0
            sqDistsPairX[idxPairX] = (gridX[idxPairX]-xPairX)**2.0 + (gridY[idxPairX]-yPairX)**2.0

            objImag = np.zeros((ySize, xSize))
            objImag[idxObj] = obj["FLUX_AUTO"] * np.exp(-sqDistsObj[idxObj]/(2*obj["FWHM_IMAGE"]))
            dataY[idxObj] += objImag[idxObj]
            dataY[idxPairY] += obj["FLUX_AUTO"] * np.exp(-sqDistsPairY[idxPairY]/(2*obj["FWHM_IMAGE"]))
            dataX[idxObj] += objImag[idxObj]
            dataX[idxPairX] += obj["FLUX_AUTO"] * np.exp(-sqDistsPairX[idxPairX]/(2*obj["FWHM_IMAGE"]))

        yMean = np.mean(dataY)
        yStd = np.std(dataY)
        self.yFitsPlotInstance = self.yFig.imshow(dataY, interpolation='gaussian',
                                                  cmap='gray', vmin=yMean, vmax=yMean+2*yStd)

        xMean = np.mean(dataX)
        xStd = np.std(dataX)
        self.xFitsPlotInstance = self.xFig.imshow(dataX, interpolation='gaussian',
                                                  cmap='gray', vmin=xMean, vmax=xMean+2*xStd)

        # Overplot location of the object and reference stars
        circSize = 7.5
        circWidth = 1.25
        if self.window.ref.objSEParams is not None:
            objX0 = self.window.ref.objSEParams["X_IMAGE"]
            objY0 = self.window.ref.objSEParams["Y_IMAGE"]
        else:
            objX0 = self.window.ref.xObjObs
            objY0 = self.window.ref.yObjObs
        objX = self.cosa * (objX0-xCen) - self.sina * (objY0-yCen) + xCen
        objY = self.sina * (objX0-xCen) + self.cosa * (objY0-yCen) + yCen
        self.yObjPlotInstance = self.yFig.plot([objX, objX+polar_pair_shift_y_dx], [objY, objY+polar_pair_shift_y_dy],
                                               marker="o", markerfacecolor="none", markersize=circSize,
                                               markeredgewidth=circWidth, markeredgecolor="r", linestyle="")[0]
        self.xObjPlotInstance = self.xFig.plot([objX, objX+polar_pair_shift_x_dx], [objY, objY+polar_pair_shift_x_dy],
                                               marker="o", markerfacecolor="none", markersize=circSize,
                                               markeredgewidth=circWidth, markeredgecolor="r", linestyle="")[0]

        for st in self.window.ref.standartsObs:
            if st['seParams'] is not None:
                stx0 = st['seParams']["X_IMAGE"]-1
                sty0 = st['seParams']["Y_IMAGE"]-1
                markColor = "g"
            else:
                stx0 = st['xCen'] - 1
                sty0 = st['yCen'] - 1
                markColor = "0.75"
            stx = self.cosa * (stx0-xCen) - self.sina * (sty0-yCen) + xCen
            sty = self.sina * (stx0-xCen) + self.cosa * (sty0-yCen) + yCen
            self.yStdPlotInstance.append(self.yFig.plot([stx, stx+polar_pair_shift_y_dx],
                                                        [sty, sty+polar_pair_shift_y_dy], marker="o",
                                                        markerfacecolor="none", linestyle="", markersize=circSize,
                                                        markeredgewidth=circWidth, markeredgecolor=markColor)[0])
            self.xStdPlotInstance.append(self.xFig.plot([stx, stx+polar_pair_shift_x_dx],
                                                        [sty, sty+polar_pair_shift_x_dy], marker="o",
                                                        markerfacecolor="none", linestyle="", markersize=circSize,
                                                        markeredgewidth=circWidth, markeredgecolor=markColor)[0])

        self.yCanvas.draw()
        self.xCanvas.draw()
