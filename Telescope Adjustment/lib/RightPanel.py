#! /usr/bin/env python

"""
The content of the right hand side panel of the main window
"""

import tkinter as Tk


class RightPanel(Tk.Frame):
    def __init__(self, window):
        self.window = window
        self.panel = Tk.Frame(self.window.root)
        self.panel.grid(column=1, row=0, padx=6)

        # Object information
        self.objectLabelValue = Tk.StringVar()
        self.objectLabelValue.set("Object: not selected")
        Tk.Label(self.panel, textvariable=self.objectLabelValue, anchor=Tk.W).grid(column=0, row=0, sticky=Tk.W)

        # Number of images information
        self.imagesNumberLabelValue = Tk.StringVar()
        self.imagesNumberLabelValue.set("Images summed: -")
        Tk.Label(self.panel, textvariable=self.imagesNumberLabelValue, anchor=Tk.W).grid(column=0, row=1, sticky=Tk.W)

        # Camera mode information
        self.photModeLabelValue = Tk.StringVar()
        self.photModeLabelValue.set("None")
        self.polarModeLabelValue = Tk.StringVar()
        self.polarModeLabelValue.set("None")
        self.modeFrame = Tk.LabelFrame(self.panel, text="Camera mode", padx=5, pady=5)
        self.modeFrame.grid(column=0, row=2, pady=7)
        Tk.Label(self.modeFrame, text="Photometry:").grid(column=0, row=0)
        Tk.Label(self.modeFrame, textvariable=self.photModeLabelValue, width=4, anchor=Tk.W).grid(column=1, row=0)
        Tk.Label(self.modeFrame, text="Polarimetry:").grid(column=0, row=1)
        Tk.Label(self.modeFrame, textvariable=self.polarModeLabelValue, width=4, anchor=Tk.W).grid(column=1, row=1)

        # Results table
        self.resultsFrame = Tk.LabelFrame(self.panel, text="Results", padx=5, pady=5)
        self.resultsFrame.grid(column=0, row=3, sticky=(Tk.W, Tk.E))
        self.resultsLabelValue = Tk.StringVar()
        # Results value
        Tk.Label(self.resultsFrame, textvariable=self.resultsLabelValue, anchor=Tk.W,
                 justify=Tk.LEFT).grid(column=0, row=0, sticky=Tk.W)

        # Messages
        self.messagesFrame = Tk.LabelFrame(self.panel, text="Messages", padx=5, pady=5, fg="red")
        self.messagesFrame.grid(column=0, row=4, sticky=(Tk.W, Tk.E))
        self.messagesLabelValue = Tk.StringVar()
        Tk.Label(self.messagesFrame, textvariable=self.messagesLabelValue, anchor=Tk.W, fg="red",
                 justify=Tk.LEFT).grid(column=0, row=0, sticky=Tk.W)
        self.messagesFrame.grid_remove()

    def clear_info(self, panelsToClean):
        if "object_name" in panelsToClean:
            self.objectLabelValue.set("")
        if "results" in panelsToClean:
            self.resultsLabelValue.set("")

    def update_object_name(self, objName, addString=""):
        if addString:
            self.objectLabelValue.set("Object: %s (%s)" % (objName, addString))
        else:
            self.objectLabelValue.set("Object: %s" % (objName))

    def update_number_of_images(self, numberOfImages):
        self.imagesNumberLabelValue.set("Images summed: %2i" % numberOfImages)

    def update_camera_mode_info(self, photFiltName, polarFiltName):
        self.photModeLabelValue.set(photFiltName)
        self.polarModeLabelValue.set(polarFiltName)

    def update_message(self, message):
        if (message == "") and (self.messagesLabelValue.get() == ""):
            return
        elif (message == "") and (self.messagesLabelValue.get() != ""):
            self.messagesLabelValue.set("")
            self.messagesFrame.grid_remove()
        else:
            self.messagesFrame.grid()
            self.messagesLabelValue.set(message)

    def show_results_photometry(self, objSn, objMag, objMagSigma, stSn):
        """
        Show photometry results for pure photometry mode and mixed photomerty+polarimetry modes
        """
        resString = ""
        if objMag is None:
            resString += "Mag: undef\n"
        else:
            resString += u"Mag: %1.2f \u00B1 %1.2f\n" % (objMag, objMagSigma)
        if objSn is None:
            resString += "obj s/n: undef\n"
        else:
            resString += "obj s/n: %1.0f\n" % (objSn)
        for key in sorted(stSn):
            value = stSn[key]
            if value is None:
                resString += "%s s/n: undef\n" % (key)
            else:
                resString += "%s s/n: %1.0f\n" % (key, value)
        self.resultsLabelValue.set(resString.strip())

    def show_results_polarimetry(self, objSN, objPairSN, stSnList, fluxRatios):
        """
        Show photometric results for pure polarimetric mode
        """
        resString = "obj s/n: "
        if objSN is None:
            resString += "undef/"
        else:
            resString += "%1.0f/" % (objSN)
        if objPairSN is None:
            resString += "undef\n"
        else:
            resString += "%1.0f\n" % (objPairSN)

        for key in sorted(stSnList):
            values = stSnList[key]
            resString += "%s s/n: " % (key)
            if values[0] is None:
                resString += "undef/"
            else:
                resString += "%1.0f/" % (values[0])
            if values[1] is None:
                resString += "undef\n"
            else:
                resString += "%1.0f\n" % (values[1])
        self.resultsLabelValue.set(resString)
