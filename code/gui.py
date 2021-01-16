from tkinter import *
from tkinter import filedialog
import subprocess

root = Tk()
root.geometry('500x500')
#root.withdraw()

def fire_pipeline():
	tool_dict = {'Ebola': '/home/anjan-purkayastha/Documents/openboxbio/FDA/20150527_ebola_chip_duncan_FDA/ebov_pipeline/ebola_i2o/code/ebola_i2o',
			  }

	my_list = list(root.tk.splitlist(root.filenames))
	myLabel = Label(root, text = clicked.get())
	tool = clicked.get()
	myLabel.pack()
	for file in my_list :
		# myLabel = Label(root, text = label)
		# myLabel.pack()
		# print(label)
		subprocess.run([tool_dict[tool], file], stdout = subprocess.DEVNULL)


def select_files():
	root.filenames = filedialog.askopenfilenames(initialdir = "/home/anjan-purkayastha/", title = "Select Input File")



clicked = StringVar()
clicked.set("BBP")
drop_down = OptionMenu(root, clicked, "BBP", "Ebola")
drop_down.config(width = 8,  bg = 'blue')
drop_down.pack()

myButton = Button(root, text = "Select Files", padx = 6, command = select_files, bg = '#ff8c1a')
myButton.pack()

myButton = Button(root, text = "Run", padx = 15, command = fire_pipeline)
myButton.pack()

myQuitButton = Button(root, text = "Quit", padx = 10, command = root.destroy)
myQuitButton.pack()

root.mainloop()
