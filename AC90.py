#!/usr/bin/env python
import csv
import os
import sys
import  tkinter as tk
from tkFileDialog import askopenfile
from tkFileDialog import asksaveasfilename
import matplotlib.pyplot as plt 
import seaborn
import pandas
import numpy as np
import scipy

assembly_output = {}
total_sum = 0
total_time = 0
total_count = 0
model_list = []
csv_input = 'AC-90,Model,Total,Order Count,Operation Time\n'
input_file = ''

def time_hms(t):
	hours = t/10000
	minutes = (t/100 - hours*100)
	seconds = (t - minutes*100 - hours*10000)
	return hours, minutes, seconds

def process_time(t1, t2):
	h1, m1, s1 = time_hms(t1)
	h2, m2, s2 = time_hms(t2)

	if(h2<h1):
		h2 = 24 + h2

	time_sec1 = (s1 + m1*60 + h1*3600)
	time_sec2 = (s2 + m2*60 + h2*3600)
	diff = time_sec2 - time_sec1
	return diff

def time_format(t):
	h = t/3600
	t = t%3600
	m = t/60
	s = t%60

	str_time = str("%02d"%h) + ':' + str("%02d"%m) + ':' + str("%02d"%s)
	return str_time

def find_pairs(input_file):
    global model_list
    with open(input_file, 'rb') as file:
    	reader = csv.reader(file)
    	list2 = []
    	for row in reader:
    		if (row[2],row[3]) not in list2:
    			list2.append((row[2],int(row[3])))
    		if row[2] not in model_list:
    			model_list.append(row[2])
    file.close()
    return list2
	


def find_sum(input_file):
	global assembly_output
	global total_sum
	global total_time
	global total_count
	list =find_pairs( input_file)
	for x in list:
		assembly_output[x] = {'sum':0 , 'time':0, 'order_count':0 }

	with open(input_file, 'rb') as file:
		reader = csv.reader(file)
		for row in reader:
			x = row[2]
			y = int(row[3])
			assembly_output[(x,y)]['sum'] += int(row[19])
			assembly_output[(x,y)]['time'] += process_time(int(row[48]), int(row[49]))
			assembly_output[(x,y)]['order_count'] += 1
	file.close()

	for i in assembly_output:
		total_sum += assembly_output[i]['sum']
		total_count += assembly_output[i]['order_count']
		total_time += assembly_output[i]['time']
		t = int(assembly_output[i]['time'])
		assembly_output[i]['time'] = time_format(t)

	total_time = time_format(total_time)



class Application(tk.Frame):
	global input_file

	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid(sticky = tk.N+tk.S+tk.E+tk.W)
		self.createWidgets()
				


	def createWidgets(self):		
		self.grid(padx=2, pady=2)
		self.canvas = tk.Canvas(self, height = 360,width = 400, border = 5, relief = "groove", bg = 'white')
		self.canvas.grid(column = 7, row = 0,  padx = 12, rowspan = 21, columnspan = 14)
		self.canvas.create_text(50, 50, text ="\n\tUpload file..", font = "Pursia, 14", justify = tk.LEFT)
		
		def upload_file():
			global input_file
			input_file = askopenfile(mode ='r').name
			self.canvas.delete("all")
			self.canvas.create_text(50, 90, text ="\t\t\tFile selected", font = "Pursia, 12", justify = tk.LEFT)
			# print input_file
			if(input_file != ''):
				find_sum(input_file)

		def to_CSV():
			global assembly_output
			global csv_input
			global input_file
			global model_list
			file_write = ''
			assembly_count = len(assembly_output)

			for y in model_list:
				for x in range(assembly_count):
					try:
						csv_input += str(x+1) + ', ' + str(y) + ', ' + str(assembly_output[(y,x+1)]['sum']) + ', ' + str(assembly_output[(y,x+1)]['order_count']) + ', ' + str(assembly_output[(y,x+1)]['time']) + '\n'
					except:
						a = 1

			csv_input += 'Total, ' + ',' + str(total_sum) + ', ' + str(total_count) + ', ' + str(total_time) + '\n'
			# print csv_input
			self.canvas.delete("all")
			if(input_file != ''):
				try:
					file_write = asksaveasfilename(defaultextension = '.csv')
					with open(file_write, 'w') as csvfile:
						csvfile.write(csv_input)
					csvfile.close()			
					csv_input = 'AC-90,Model,Total,Order Count,Drive Time\n '
					os.system("start " + file_write)
					self.canvas.create_text(20, 70, text ="\t\tFile exported to CSV", font = "Pursia, 12", justify = tk.LEFT)
					self.canvas.create_text(20, 90, text ="\t\tOpening file...", font = "Pursia, 12", justify = tk.LEFT)
				
				except:
					print "ERROR"
					self.canvas.create_text(20, 70, text ="\tERROR", font = "Pursia, 12", justify = tk.LEFT)
					self.canvas.create_text(30, 90, text ="\t\t\tCheck if the output file is closed.", font = "Pursia, 12", justify = tk.LEFT)
					
							
			else:
				print 'file path not selected'
				self.canvas.create_text(20, 70, text ="\t\tFile path not selected!", font = "Pursia, 12", justify = tk.LEFT)

			if(file_write != ''):
				f = pandas.read_csv(file_write)
				fig = plt.figure()
				pivot = f.pivot_table(index = "AC-90", values = 'Total', aggfunc = sum)
				pivot_new = pivot[0:assembly_count-2]
				ax = fig.add_subplot(1,1,1)
				x = scipy.arange(assembly_count)
				ax.set_xticks(x)
				ax.set_xlim([0,assembly_count])
				plt.style.use("ggplot")
				# print pivot_new.index.tolist()
				plt.bar((pivot_new.index.tolist()), pivot_new)
				plt.xlabel("Assembly no.")
				plt.ylabel("Total Output")
				plt.title("AC-90 Comparison")
				plt.show()


		top = self.winfo_toplevel()
		top.rowconfigure(0, weight = 1)
		top.columnconfigure(0, weight = 1)
		top = self.winfo_toplevel()
		self.menuBar = tk.Menu(top)
		top['menu'] = self.menuBar
		self.subMenu = tk.Menu(self.menuBar)
		self.subMenu1 = tk.Menu(self.menuBar)
		self.menuBar.add_cascade(label='File', menu=self.subMenu)
		self.subMenu.add_command(label='About')
		self.subMenu.add_command(label = 'Exit', command=self.quit)
		self.menuBar.add_cascade(label='Help', menu=self.subMenu1)		
		

		self.uploadButton = tk.Button(self, foreground = 'green', border = 3, relief = "groove" , text = 'Upload CSV')
		self.uploadButton["command"] = upload_file
		self.uploadButton.grid(column = 7, row = 31, padx = 5, pady = 5, rowspan = 3,ipadx = 35, ipady = 5,columnspan = 7)

		self.toCsvButton = tk.Button(self, border = 3, relief = "groove" , text = 'Export to CSV', foreground = 'blue')
		self.toCsvButton["command"] = to_CSV
		self.toCsvButton.grid(column = 14, row = 31, rowspan = 3,ipadx = 25, ipady = 5, columnspan = 5)

		self.exitButton = tk.Button(self, foreground = 'red', justify = tk.CENTER, border = 3, relief = "groove",text = 'Exit', command = self.quit)
		self.exitButton.grid(column = 19, row = 31,  padx = 0, pady = 1, rowspan = 3,ipadx = 47, ipady = 5)



app = Application()
app.master.title('Yazaki_AC-90')
app.master.minsize(width=440, height=440)
app.master.maxsize(width=440, height=4540)
app.mainloop()
