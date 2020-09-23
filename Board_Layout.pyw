import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.uic import loadUi
import sqlite3
import Functions
import json
from math import gcd


class Main(QMainWindow):
    # initialize method to load main startup window
	def __init__(self):
		super(Main, self).__init__()
		loadUi('mainWindow2.ui', self)
		self.show()

		# # create and connect to database
		# self.conn = sqlite3.connect('data.db')

  #       # create cursor
		# self.c = self.conn.cursor()

  #       # call method to create tables in database
		# self.create_tables()

		# Create keyboard shortcuts
		self.shortcut = QShortcut(Qt.Key_Enter, self)
		self.shortcut2 = QShortcut(Qt.Key_Return, self)
		self.shortcut_bulk = QShortcut(QKeySequence('Shift+Return'), self)
		
		# Signals for keyboard shortcuts
		self.shortcut.activated.connect(self.on_add_click)
		self.shortcut2.activated.connect(self.on_add_click)
		self.shortcut_bulk.activated.connect(self.on_bulk_add_click)

		# Signal for add button click
		self.pushButton_add.clicked.connect(self.on_add_click)

		# Signal for bulk add button click
		self.pushButton_bulkAdd.clicked.connect(self.on_bulk_add_click)

		# Signal for calculate button click
		self.pushButton_calc.clicked.connect(self.on_calculate_click)

		# Signal for wood pipes checkbox
		self.checkBox_wood.clicked.connect(self.on_wood_click)

		# Signal for bass pipes checkbox
		self.checkBox_bass.clicked.connect(self.on_bass_click)

	# def create_tables(self):
	# 	# create tables in database
	# 	# statements left even though they are passed
	# 	# in order to see layout of all of the tables
	# 	try:
	# 		self.c.execute('''CREATE TABLE rank_info (
 #                            job_name text,
 #                            rank_name text,
 #                            side_room text,
 #                            end_room text,
 #                            wood_depth1 text,
 #                            wood_depth2 text,
 #                            bass_num text,
 #                            pipe_sizes text''')
	# 	except:
	# 		pass

		self.pipe_diameter = []
		self.pipe_radius = []
		self.pipeY = []
		self.calculated_pipe = []
		for n in range(1, 74):
			self.pipe_diameter.append(0)
			self.pipe_radius.append(0)
			self.pipeY.append(0)
			self.calculated_pipe.append(0)

		self.XDistance = 0
		self.DistAdded = 0
		self.distance = 0
		self.bassdistance = 0
		self.firstrun = True

	def on_add_click(self):
		if self.lineEdit_bodySize.text() != '':
			self.new_pipe_size = self.lineEdit_bodySize.text()
			self.add_pipe(self.new_pipe_size)
			self.lineEdit_bodySize.clear()
		else:
			QMessageBox.warning(self, "Error", "Must enter a pipe size!", QMessageBox.Ok)

	def add_pipe(self, pipe_size):
		self.num = str(self.treeWidget_pipes.topLevelItemCount() + 1)
		self.new_item = [self.num, pipe_size]
		self.treeWidget_pipes.addTopLevelItem(QTreeWidgetItem(self.new_item))
		
	def on_bulk_add_click(self):
		if self.lineEdit_bodySize.text() != '' and self.lineEdit_bulkAddNum.text() != "":
			self.bulk_add_num = int(self.lineEdit_bulkAddNum.text())
			self.new_bulk_pipe_size = self.lineEdit_bodySize.text()
			for num in range(0, self.bulk_add_num):
				self.add_pipe(self.new_bulk_pipe_size)
			self.lineEdit_bulkAddNum.clear()
			self.lineEdit_bodySize.clear()
		else:
			QMessageBox.warning(self, "Error", "Must enter a pipe size and number of pipes to add!", QMessageBox.Ok)

	def on_wood_click(self):
		if self.checkBox_wood.isChecked() == True:
			self.label_woodDepth1.setEnabled(True)
			self.lineEdit_woodDepth1.setEnabled(True)
			self.label_woodDepth2.setEnabled(True)
			self.lineEdit_woodDepth2.setEnabled(True)
		else:
			self.label_woodDepth1.setEnabled(False)
			self.lineEdit_woodDepth1.setEnabled(False)
			self.label_woodDepth2.setEnabled(False)
			self.lineEdit_woodDepth2.setEnabled(False)

	def on_bass_click(self):
		if self.checkBox_bass.isChecked() == True:
			self.label_bassPipes.setEnabled(True)
			self.lineEdit_bassPipeNum.setEnabled(True)
		else:
			self.label_bassPipes.setEnabled(False)
			self.lineEdit_bassPipeNum.setEnabled(False)

	def on_calculate_click(self):
		# assign all of the pipes to numbers in a list, converted to float
		for n in range(0, self.treeWidget_pipes.topLevelItemCount()):
			self.temp_pipe_item = self.treeWidget_pipes.topLevelItem(n)
			self.pipe_diameter[n + 1] = Functions.MakeFloat(self.temp_pipe_item.text(1))
			self.pipe_radius[n + 1] = self.pipe_diameter[n + 1] / 2

		# Define first and last pipe
		if self.checkBox_bass.isChecked() == True:
			self.FirstPipe = int(self.lineEdit_bassPipeNum) + 1
		else:
			self.FirstPipe = 1


		# Get number of pipes
		self.NumberofPipes = self.treeWidget_pipes.topLevelItemCount()

		# Convert Information into Float to use for math
		if self.checkBox_wood.isChecked() == True:
			self.WoodDepth1 = Functions.MakeFloat(self.lineEdit_woodDepth1)
			self.WoodDepth2 = Functions.MakeFloat(self.lineEdit_woodDepth2)
		self.SideRoom = Functions.MakeFloat(self.lineEdit_sideRoom.text())
		self.EndRoom = Functions.MakeFloat(self.lineEdit_endRoom.text())

		# --------------------- Find X Values of Pipes --------------------
		# Pipes ARE Wood
		if self.checkBox_wood.isChecked() == True:
			self.TotalWidth = (self.SideRoom * 2) + self.WoodDepth1
			self.row1x = Functions.XofRow1(self.SideRoom, self.WoodDepth1)
			if self.radioButton_twoRows.isChecked() == True:
				self.TotalWidth += self.XDistance + self.WoodDepth2
				self.row2x = Functions.XofRow2(self.row1x, self.XDistance, self.WoodDepth1, self.WoodDepth2)
			else:
				self.row2x = "N/A"

		# Pipes AREN'T Wood
		else:
			self.TotalWidth = (self.SideRoom * 2)+self.pipe_diameter[self.FirstPipe]
			self.row1x = Functions.XofRow1(self.SideRoom, self.pipe_diameter[self.FirstPipe])
			if self.radioButton_twoRows.isChecked() == True:
				self.TotalWidth += self.XDistance+self.pipe_diameter[self.FirstPipe+1]
				self.row2x = Functions.XofRow2(self.row1x, self.XDistance, self.pipe_diameter[self.FirstPipe],
									 self.pipe_diameter[self.FirstPipe+1])
			else:
				self.row2x = "N/A"

		if self.checkBox_bass.isChecked() == True:
			self.rowbassx = self.TotalWidth / 2

		else:
			self.rowbassx = "N/A"
			self.BassNum = "N/A"

		# ------------------ Find Y value of Pipes------------------------
		# Check for bass and then find Y of bass pipes and first non bass pipes
		if self.checkBox_bass.isChecked() == True:
			self.pipeY[self.FirstBassPipe] = self.EndRoom + (self.pipe_diameter[self.FirstBassPipe] / 2)

			for n in range(self.FirstBassPipe + 2, self.FirstPipe):
				self.pipeY[n] = self.pipeY[n - 1] + (self.pipe_diameter[n - 1] / 2) + self.DistAdded + (self.pipe_diameter[n] / 2)

			self.pipeY[self.FirstPipe] = self.pipeY[self.FirstPipe-1] + (self.pipe_diameter[self.FirstPipe - 1] / 2) + self.DistAdded + (self.pipe_diameter[self.FirstPipe] / 2)
		else:
			self.pipeY[self.FirstPipe] = self.EndRoom + (self.pipe_diameter[self.FirstPipe] / 2)

		# Non bass pipes
		if self.radioButton_twoRows.isChecked() == True:
			# First row
			for n in range(self.FirstPipe + 2, self.NumberofPipes + 1, 2):
				self.pipeY[n] = self.pipeY[n - 2] + self.pipe_radius[n - 2] + self.distance + self.pipe_radius[n]
			# Second row
			for n in range(self.FirstPipe + 1, self.NumberofPipes + 1, 2):
				if n == self.NumberofPipes:
					if self.NumberofPipes % 2 == 0:
						self.pipeY[n] = self.pipeY[n - 2] + self.pipe_radius[n - 2] + self.distance + self.pipe_radius[n]
					else:
						self.pipeY[n] = (((self.pipeY[n + 1]-(self.pipe_diameter[n + 1] / 2)) - (self.pipeY[n - 1] + (self.pipe_diameter[n - 1] / 2))) / 2) + self.pipeY[n - 1] + (self.pipe_diameter[n - 1] / 2)
				else:
					self.pipeY[n] = (((self.pipeY[n + 1] - (self.pipe_diameter[n + 1] / 2)) - (
					self.pipeY[n - 1] + (self.pipe_diameter[n - 1] / 2))) / 2) + self.pipeY[n - 1] + (
									self.pipe_diameter[n - 1] / 2)
		else:
			#Single row
			for n in range(self.FirstPipe + 1, self.NumberofPipes + 1):
				self.pipeY[n] = self.pipeY[n - 1] + (self.pipe_diameter[n - 1] / 2) + self.distance + (self.pipe_diameter[n] / 2)
		for n in range(self.FirstPipe + 1, self.NumberofPipes + 1):
			if self.pipeY[n] - self.pipeY[n - 1] < 0.75:
				self.pipeY[n] = self.pipeY[n - 1] + 0.75

		# Show results on result window
		if self.firstrun:
			self.LengthPosition = 0
			self.treeWidget_calculated.clear()
			
			for x in range(1, self.NumberofPipes+1):
				self.calculated_pipe[x] = [str(x), str(Functions.rulerfrac(self.pipeY[x]))]
				self.treeWidget_calculated.addTopLevelItem(QTreeWidgetItem(self.calculated_pipe[x]))

			if self.XDistance < 0:
				self.label_xDistance.setText("{} {}".format("X Overlap:", Functions.rulerfrac(abs(self.XDistance))))
			else:
				self.label_xDistance.setText("{} {}".format("X Distance:", Functions.rulerfrac(abs(self.XDistance))))

			self.label_yDistance.setText("{} {}".format("Y Distance:", self.distance))
			self.label_distAdded.setText("{} {}".format("Distance Added:", self.DistAdded))

			if self.lineEdit_sideRoom.text() == "":
				self.label_sideLength.setText("{} {}".format("Side Length:", 0))
			else:
				self.label_sideLength.setText("{} {}".format("Side Length:", self.lineEdit_sideRoom.text()))

			self.side_length = Functions.MakeFloat(self.lineEdit_sideRoom.text())

			if self.lineEdit_endRoom.text() == "":
				self.label_endLength.setText("{} {}".format("End Length:", 0))
			else:
				self.label_endLength.setText("{} {}".format("End Length:", self.lineEdit_endRoom.text()))

			self.end_length = Functions.MakeFloat(self.lineEdit_endRoom.text())
		else:
			self.Update()

		#Check if each row is being used and convert into fraction if so
		if isinstance(self.row1x, float):
			self.row1x = Functions.rulerfrac(self.row1x)
		if isinstance(self.row2x, float):
			self.row2x = Functions.rulerfrac(self.row2x)

		#Create labels to display rows
		if self.firstrun:
			self.label_rowOne.setText("{} {}".format("Row One:", self.row1x))
			self.label_rowTwo.setText("{} {}".format("Row Two:", self.row2x))
			if self.checkBox_bass.isChecked() == True:
				self.label_middleRow.setText("{} {}".format("Middle Row:", Functions.rulerfrac(self.rowbassx)))
				self.label_bassPipes.setText("{} {}".format("Bass Pipes:", self.BassNum.get()))
			else:
				self.label_middleRow.setText("{} {}".format("Middle Row:", self.rowbassx))
				self.label_bassPipes.setText("{} {}".format("Bass Pipes:", self.BassNum))

			self.XDistance = 0
			self.DistAdded = 0

		#Calculate total length of toe board
		self.TotalLength = self.pipeY[self.NumberofPipes] + self.pipe_radius[self.NumberofPipes] + self.end_length

		if self.firstrun:
			self.label_totalWidth.setText("{} {}".format("Total Width:", Functions.rulerfrac(self.TotalWidth)))

		self.label_totalLength.setText("{} {}".format("Total Length:", Functions.rulerfrac(self.TotalLength)))

		self.firstrun = False


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())