#! /usr/bin/env python

"""
Definitions related to the main window menu: the menu itself and some
windows that can be invoked by the menu
"""

import os
from os import path
import glob
from collections import OrderedDict
import tkinter as Tk
from tkinter import font as tkFont
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from matplotlib import rc

import PolarChecker
import Configuration

rc('text', usetex=False)


class MenuBar(Tk.Frame):
    def __init__(self, window):
        self.window = window
        self.menubar = Tk.Menu(window.root)
        self.fileMenu = Tk.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Select folder", command=self.select_folder)
        # self.fileMenu.add_command(label="Rename files", command=self.rename_files)
        self.fileMenu.add_command(label="Reset", command=self.window.reset_new_object)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)

        # Alarm menu button
        self.menubar.add_command(label="Alarm", command=self.set_alarm)

        # Polar check menu button
        self.menubar.add_command(label="PolarCheck", command=self.polar_check)

        # Log menu button
        self.logMenu = Tk.Menu(self.menubar, tearoff=0)
        self.logMenu.add_command(label="Show log", command=self.show_log)
        self.logMenu.add_command(label="Select object", command=self.select_object)
        self.menubar.add_cascade(label="History", menu=self.logMenu)

        # Config menu button
        self.menubar.add_command(label="Config", command=self.configure)

        # Quit
        self.menubar.add_command(label="Quit", command=self.window.on_closing)
        self.window.root.config(menu=self.menubar)

    def select_folder(self):
        # Find newest directory in telescopedata as an initial dir
        if os.name == "nt":
            pathToData = path.join("D:\\", "TelescopeData", "*")
            listOfDirs = filter(path.isdir, glob.glob(pathToData))
            initialdir = max(listOfDirs, key=path.getctime)
        else:
            initialdir = None
        dirPath = tkFileDialog.askdirectory(parent=self.window.root,
                                            title="Open data folder",
                                            initialdir=initialdir)
        dirPath = path.normpath(dirPath)
        self.window.setup(dirPath)

    def set_alarm(self):
        AlarmPopup(self.window)

    def polar_check(self):
        if self.window.polarFiltName is not None:
            tkMessageBox.showwarning("PolarCheck",
                                     "Works only in pure photometry mode.")
            return
        PolarChecker.PolarChecker(self.window)

    # def rename_files(self):
    #     RenameFilesPopup(self.window)

    def show_log(self):
        LogWindow(self.window)

    def select_object(self):
        SelectObjectWindow(self.window)

    def configure(self):
        Configuration.ConfigWindow(self.window)


class AlarmPopup(Tk.Frame):
    def __init__(self, window):
        self.window = window
        self.top = Tk.Toplevel(window.root)
        self.top.geometry('+%i+%i' % (window.root.winfo_x()+30, window.root.winfo_y()+30))
        Tk.Label(self.top, text="Exposures").grid(column=0, row=0, padx=5, pady=5)
        self.entry = Tk.Entry(self.top, width=5)
        self.entry.insert(0, str(abs(window.desiredExposures)))
        self.entry.grid(column=1, row=0, padx=5, pady=5)
        self.button = Tk.Button(self.top, text="OK", command=self.ok)
        self.button.grid(column=0, row=1, padx=5, pady=5)
        self.cancelButton = Tk.Button(self.top, text="Cancel", command=self.top.destroy)
        self.cancelButton.grid(column=1, row=1, padx=5, pady=5)

    def ok(self):
        self.window.desiredExposures = int(self.entry.get())
        self.top.destroy()


# class RenameFilesPopup(Tk.Frame):
#     def __init__(self, window):
#         self.window = window
#         self.top = Tk.Toplevel(window.root)
#         self.top.geometry('+%i+%i' % (window.root.winfo_x()+30, window.root.winfo_y()+30))
#         Tk.Label(self.top, text="Input desired number of exposures").grid(column=0, row=0, padx=5, pady=5)
#         self.entry = Tk.Entry(self.top, width=5)
#         self.entry.insert(0, str(abs(window.numOfCoaddedImages)))
#         self.entry.grid(column=1, row=0, padx=5, pady=5)
#         self.button = Tk.Button(self.top, text="OK", command=self.ok)
#         self.button.grid(column=0, row=1, padx=5, pady=5)
#         self.cancelButton = Tk.Button(self.top, text="Cancel", command=self.top.destroy)
#         self.cancelButton.grid(column=1, row=1, padx=5, pady=5)
#         self.top.wm_attributes("-topmost", 1)

#     def ok(self):
#         desiredExposures = int(self.entry.get())
#         if desiredExposures >= len(self.window.rawImages):
#             minorExp = self.window.rename_files(desiredExposures)
#             self.window.reset_new_object()
#             tkMessageBox.showinfo("Rename files",
#                                   "All done, minor exposure is %i" % (minorExp+1))
#             self.top.destroy()
#         else:
#             errorString = "The number of desired exposures should be bigger than the number of already taken ones."
#             tkMessageBox.showwarning("Rename files", errorString)


class LogWindow(Tk.Frame):
    """
    Window to show photometry log data
    """
    def __init__(self, window):
        self.top = Tk.Toplevel(window.root)
        self.textFrame = Tk.Text(self.top)
        self.scroll = Tk.Scrollbar(self.top)
        self.scroll.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.textFrame.pack(side=Tk.LEFT, fill=Tk.Y)
        self.scroll.config(command=self.textFrame.yview)
        self.textFrame.config(yscrollcommand=self.scroll.set,
                              font=tkFont.Font(family="Times", size=12))
        # Put text into frame
        for key in window.photoLog:
            objName = key.split(":")[0]
            addString = key.split(":")[1]
            if addString:
                logString = "%s(%s): " % (objName, addString)
            else:
                logString = "%s:  " % (objName)
            for filtName in window.photoLog[key]:
                magValue = window.photoLog[key][filtName]
                if magValue is not None:
                    logString += "M_%s=%1.2f  " % (filtName, magValue)
            logString += "\n"
            self.textFrame.insert(Tk.END, logString)


class SelectObjectWindow(Tk.Frame):
    """
    Window to select previously observed objects to be processed
    """
    def __init__(self, window):
        self.window = window
        self.top = Tk.Toplevel(window.root)
        self.top.protocol('WM_DELETE_WINDOW', self.close)

        # Before going into processing let's check the directory real quick to
        # find the list of already observed objects.
        self.list_of_all_observed_objects = OrderedDict()
        self.all_filter_combinations = []
        allFiles = glob.glob(path.join(self.window.dirName, "*.FIT"))
        allFiles.sort(key=path.getctime)
        for fName in allFiles:
            fNameWithoutPath = path.basename(fName)
            if ("dark" not in fNameWithoutPath) and ("bias" not in fNameWithoutPath) and (path.isfile(fName)):
                objName, filterCombination, addString = window.camera_parser.parse_object_file_name(fNameWithoutPath)

                if objName is None:
                    continue

                objStr = "%s:%s" % (objName, addString)
                if objStr not in self.list_of_all_observed_objects:
                    # A new object found -> add it to the dictionary
                    self.list_of_all_observed_objects[objStr] = []
                if filterCombination not in self.list_of_all_observed_objects[objStr]:
                    # Add a new filter for the filterlist of the current object
                    self.list_of_all_observed_objects[objStr].append(filterCombination)

                if filterCombination not in self.all_filter_combinations:
                    self.all_filter_combinations.append(filterCombination)

        # Scrollbar
        self.scrollbar = Tk.Scrollbar(self.top)
        self.scrollbar.grid(column=1, row=0, rowspan=8, sticky=Tk.S+Tk.N)

        # List of all observed objects
        self.objectsListBox = Tk.Listbox(self.top, selectmode=Tk.SINGLE,
                                         height=10, yscrollcommand=self.scrollbar.set)
        self.objectsListBox.grid(column=0, row=0, rowspan=8)
        for objStr in self.list_of_all_observed_objects.keys():
            self.objectsListBox.insert(Tk.END, objStr)
        self.objectsListBox.selection_set(Tk.END)
        self.objectsListBox.bind('<<ListboxSelect>>', self.select_object)
        self.scrollbar.config(command=self.objectsListBox.yview)
        self.objectsListBox.yview_moveto(1)

        # Radoibuttons with filtres
        self.selectedFilter = Tk.StringVar()
        self.selectedFilter.set("r")
        self.selectedFilter.trace("w", self.compute_previous_object)
        self.filterRadioButtons = {}
        for i, filt in enumerate(self.all_filter_combinations):
            self.filterRadioButtons[filt] = Tk.Radiobutton(self.top, text=filt, variable=self.selectedFilter,
                                                           value=filt)
            self.filterRadioButtons[filt].grid(column=2, row=i)

        # Close button
        self.closeButton = Tk.Button(self.top, text="Close", command=self.close)
        self.closeButton.grid(column=2, row=len(self.all_filter_combinations)+1)
        self.objectsListBox.event_generate("<<ListboxSelect>>")

    def select_object(self, event):
        self.objStr = self.objectsListBox.get(self.objectsListBox.curselection())
        observed_filters = self.list_of_all_observed_objects[self.objStr]
        # Make visible only radiobuttons that correspond to observed filters
        for filt in self.all_filter_combinations:
            if (filt in observed_filters) or (filt.upper() in observed_filters):
                self.filterRadioButtons[filt].config(state="normal")
            else:
                self.filterRadioButtons[filt].config(state="disabled")
        # Select r filter if it was observed, otherwise select just first observed filter
        if 'r' in observed_filters:
            self.selectedFilter.set('r')
        else:
            self.selectedFilter.set(observed_filters[0])

    def compute_previous_object(self, *args):
        objName, addString = self.objStr.split(":")
        self.window.object_selected_manually = True
        self.window.objName = objName
        if self.selectedFilter.get() in self.list_of_all_observed_objects[self.objStr]:
            self.window.filterCombination = self.selectedFilter.get()
        else:
            # Take into account the possibilirt that the user have set
            # a capital character to denote the filter
            self.window.filterCombination = self.selectedFilter.get().upper()
        self.window.addString = addString

    def close(self):
        self.window.object_selected_manually = False
        self.top.destroy()
