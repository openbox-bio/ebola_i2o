#!/usr/bin/env python
from __future__ import division
import pygtk
pygtk.require('2.0')
import gtk
import pango
import subprocess
import sys


class MasterFrame:
  def destroy(self, widget):
    gtk.main_quit()

  def main(self):
    gtk.main()
    return 0



  def open_file_selector(self, widget):
      fileSelector= FileSelector(self.file_set)
      return 0

  def run_pipeline(self, widget):
      file_in_list =list(self.file_set)
      increments=len(file_in_list)
      Progress_String="%d of %d files complete" % (0,increments)
      self.progressbar.set_text(Progress_String)
      self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
      self.progressbar.set_fraction(0)
      self.progressbar.show()
      count=0
      while gtk.events_pending():
          gtk.main_iteration(False)
      for file_string in file_in_list:
          print "Analyzing File: " + file_string
          #sys.exit()
          if self.pipeline == 'Ebola':
              print "Running Pipeline For: Ebola"
              result = subprocess.Popen(["perl","/home/Duncan.Lab/openboxbio/code/ebola_i2o",file_string], stdout=subprocess.PIPE)
          if self.pipeline == "BBP":
              print "Running Pipeline For: BBP"
              result = subprocess.Popen(["perl","/home/Duncan.Lab/openboxbio/code/bbp_i2o",file_string], stdout=subprocess.PIPE)
              #print result.communicate()
          count=count+1
          progress=(count/increments)
          self.progressbar.set_fraction(progress)
          Progress_String="%d of %d files complete" % (count,increments)
          self.progressbar.set_text(Progress_String)
          while gtk.events_pending():
              gtk.main_iteration(False)
      self.file_set=set()
      return 0

  def select_pipeline(self, widget, data):
      #data = self.comboBox.entry.get_text()
      self.pipeline = data.get_text()
      return 0

  def __init__(self):
    self.file_set= set ()
    self.pipeline= ""
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title("BioBox")
    self.window.set_size_request(500,400)
    self.window.connect("destroy", self.destroy)
    self.window.set_position(gtk.WIN_POS_CENTER)
    self.window.set_resizable(False)
    self.window.show()

    ############################
    #Progress Bar
    self.progressbar=gtk.ProgressBar()
    ############################


    self.image = gtk.Image()
    self.image.set_from_file('/home/Duncan.Lab/openboxbio/code/icons/GUI Icon.jpg')
    self.image.show()

    fixed= gtk.Fixed()
    self.window.add(fixed)
    fixed.show()

    fileSelectorButton = gtk.Button("Select Input Files")
    pipelineRunButton = gtk.Button("Run")
    quitButton= gtk.Button("Quit")
    fileSelectorButton.set_size_request(130,30)
    pipelineRunButton.set_size_request(130,30)
    quitButton.set_size_request(130,30)

    fileSelectorButton.set_relief(gtk.RELIEF_NORMAL)
    #fileSelectorButton.set_focus_on_click(focus_on_click)

    fileSelectorButton.connect("clicked", self.open_file_selector)
    pipelineRunButton.connect("clicked", self.run_pipeline)
    quitButton.connect("clicked", self.destroy)

    fixed.put(self.image, 215, 25)
    fixed.put(fileSelectorButton, 175,160)
    fixed.put(pipelineRunButton, 175,210)
    fixed.put(quitButton, 175,260)
    fixed.put(self.progressbar, 155,350)


    fileSelectorButton.show()
    pipelineRunButton.show()
    quitButton.show()



    comboBox = gtk.Combo()
    choices = ['BBP', 'Ebola']
    comboBox.set_popdown_strings(choices)
    comboBox.entry.set_text('Select Pipeline')
    #comboBox.set_use_arrows(1)
    comboBox.entry.connect("changed", self.select_pipeline, comboBox.entry)
    fixed.put(comboBox, 148, 120)
    comboBox.show()

class FileSelector:
    # Get the selected filename and print it to the console
    def file_ok_sel(self, widget):
        for file in self.filew.get_selections():
            self.selected_files.add(file)
            self.filew.destroy()

    def destroy(self, widget):
        self.filew.destroy()

    def __init__(self, file_set= set ()):

        self.selected_files = file_set
        # Create a new file selection widget
        self.filew = gtk.FileSelection("Select Input Files")

        self.filew.connect("destroy", self.destroy)
        # Connect the ok_button to file_ok_sel method
        self.filew.ok_button.connect("clicked", self.file_ok_sel)

        # Connect the cancel_button to destroy the widget
        self.filew.cancel_button.connect("clicked",self.destroy)

        # Lets set the filename, as if this were a save dialog,
        # and we are giving a default filename
        self.filew.set_filename("")

        select_multiple= 1
        self.filew.set_select_multiple(select_multiple)

        self.filew.show()

if __name__ == "__main__":
    masterframe = MasterFrame()
    masterframe.main()
