#! /usr/bin/env python

import tkinter as Tk
from tkinter import filedialog as tkFileDialog
from os import path
import shelve
from cameras.camera import list_of_cameras


class ConfigWindow(Tk.Frame):
    """Window to configure the package behaviour. All parameters are
    saved into params.db file upon change and will be loaded next time
    the package launched"""
    def __init__(self, window):
        self.window = window
        self.top = Tk.Toplevel(window.root)

        # Camera selection subpanel
        self.cameraNameVar = Tk.StringVar()
        self.cameraNameVar.set(self.window.params.get('camera_name'))
        self.cameraNameVar.trace("w", lambda n, m, x: self.toggle_camera(self.cameraNameVar.get()))
        Tk.Label(self.top, text="Select camera:").grid(column=0, row=0)
        Tk.OptionMenu(self.top, self.cameraNameVar, *list_of_cameras).grid(column=1, row=0, columnspan=2)

        # Background type subpanel
        self.backTypeVar = Tk.StringVar()
        self.backTypeVar.set(self.window.params.get("background_type"))
        self.backTypeVar.trace("w", lambda n, m, x: self.window.params.set("background_type", self.backTypeVar.get()))
        Tk.Label(self.top, text="Background type:").grid(column=0, row=1)
        Tk.Radiobutton(self.top, text="Local", variable=self.backTypeVar, value="LOCAL").grid(column=1, row=1)
        Tk.Radiobutton(self.top, text="Global", variable=self.backTypeVar, value="GLOBAL").grid(column=2, row=1)

        # Show hot pixels subpanel
        self.showHotPixelsVar = Tk.BooleanVar()
        self.showHotPixelsVar.set(self.window.params.get("show_hot_pixels"))
        self.showHotPixelsVar.trace("w", lambda n, m, x: self.toggle_show_pixel())
        Tk.Label(self.top, text="Show hot pixels").grid(column=0, row=2)
        Tk.Checkbutton(self.top, variable=self.showHotPixelsVar).grid(column=1, row=2)

        # Flat fields subpanel
        Tk.Label(self.top, text="Flats directory").grid(column=0, row=3)
        Tk.Button(self.top, text="Choose", command=self.select_flats_dir).grid(column=1, row=3)

        # Ok button
        Tk.Button(self.top, text="OK", command=self.top.destroy).grid(column=0, row=4)

        self.top.geometry('+%i+%i' % (window.root.winfo_x()+window.root.winfo_width()/2-200,
                                      window.root.winfo_y()+window.root.winfo_height()/2-200))

    def toggle_camera(self, camera):
        self.window.params.set("camera_name", camera)
        msg = "Camera is set to '%s'.\n" % camera
        msg += "Restart SignalNoise to apply all the changes."
        Tk.messagebox.showinfo("Camera set", msg)

    def toggle_show_pixel(self):
        self.window.params.set("show_hot_pixels", self.showHotPixelsVar.get())
        self.window.update_plot()

    def select_flats_dir(self):
        if path.exists(self.window.params.get("path_to_flats")):
            initialdir = self.window.params.get("path_to_flats")
        else:
            initialdir = path.dirname(path.abspath(__file__))
        flats_directory = tkFileDialog.askdirectory(parent=self.top,
                                                    title="Open flats directory",
                                                    initialdir=initialdir)
        self.window.params.set("path_to_flats", flats_directory)
        self.window.cache_flats()


class Parameters(object):
    """
    Parameters of the package
    """
    def __init__(self):
        self.__paramsFileName = path.join(path.dirname(path.abspath(__file__)), 'params.db')
        self.__default_values = {"show_hot_pixels": False,
                                 "background_type": "GLOBAL",
                                 "camera_name": "fli_lx200",
                                 "path_to_flats": "flats"}
        # Load parameters from a file, if it exists. Otherwise use defaults
        if path.exists(self.__paramsFileName):
            with shelve.open(self.__paramsFileName) as db:
                self.__params_values = db['params']
        else:
            self.__params_values = self.__default_values.copy()
            # Create a file with defaults for the future use
            self.save()

    def get(self, param_name):
        return self.__params_values[param_name]

    def set(self, param_name, new_value):
        self.__params_values[param_name] = new_value
        self.save()

    def save(self):
        with shelve.open(self.__paramsFileName) as db:
            db['params'] = self.__params_values
