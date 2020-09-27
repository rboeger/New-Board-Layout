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

		# Signal for new menubutton click
		self.actionNew.triggered.connect(self.on_new_click)

		# Signals for increasing and decreasing length and width
		self.pushButton_incLength.clicked.connect(self.increase_length)
		self.pushButton_decLength.clicked.connect(self.decrease_length)
		self.pushButton_incWidth.clicked.connect(self.increase_width)
		self.pushButton_decWidth.clicked.connect(self.decrease_width)

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

		self.pipe_diameter_list = []
		self.pipe_radius_list = []
		self.pipe_y_list = []
		self.calculated_pipe_list = []
		for n in range(1, 74):
			self.pipe_diameter_list.append(0)
			self.pipe_radius_list.append(0)
			self.pipe_y_list.append(0)
			self.calculated_pipe_list.append(0)

		self.x_distance = 0
		self.dist_added = 0
		self.distance = 0
		self.bass_distance = 0
		self.first_run = True

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
			self.label_bass.setEnabled(True)
			self.lineEdit_bassPipeNum.setEnabled(True)
		else:
			self.label_bass.setEnabled(False)
			self.lineEdit_bassPipeNum.setEnabled(False)

	def on_calculate_click(self):
		# assign all of the pipes to numbers in a list, converted to float
		for n in range(0, self.treeWidget_pipes.topLevelItemCount()):
			self.temp_pipe_item = self.treeWidget_pipes.topLevelItem(n)
			self.pipe_diameter_list[n + 1] = Functions.MakeFloat(self.temp_pipe_item.text(1))
			self.pipe_radius_list[n + 1] = self.pipe_diameter_list[n + 1] / 2

		# Define first and last pipe
		if self.checkBox_bass.isChecked() == True:
			self.first_pipe = int(self.lineEdit_bassPipeNum) + 1
		else:
			self.first_pipe = 1


		# Get number of pipes
		self.number_of_pipes = self.treeWidget_pipes.topLevelItemCount()

		# Convert Information into Float to use for math
		if self.checkBox_wood.isChecked() == True:
			self.wood_depth_1 = Functions.MakeFloat(self.lineEdit_woodDepth1)
			self.wood_depth_2 = Functions.MakeFloat(self.lineEdit_woodDepth2)

		if self.lineEdit_sideRoom.text() == "":
			self.lineEdit_sideRoom.setText("0")
		if self.lineEdit_endRoom.text() == "":
			self.lineEdit_endRoom.setText("0")

		self.side_room = Functions.MakeFloat(self.lineEdit_sideRoom.text())
		self.end_room = Functions.MakeFloat(self.lineEdit_endRoom.text())


		# --------------------- Find X Values of Pipes --------------------
		# Pipes ARE Wood
		if self.checkBox_wood.isChecked() == True:
			self.total_width = (self.side_room * 2) + self.wood_depth_1
			self.row1_x = Functions.XofRow1(self.side_room, self.wood_depth_1)
			if self.radioButton_twoRows.isChecked() == True:
				self.total_width += self.x_distance + self.wood_depth_2
				self.row2_x = Functions.XofRow2(self.row1_x, self.x_distance, self.wood_depth_1, self.wood_depth_2)
			else:
				self.row2_x = "N/A"

		# Pipes AREN'T Wood
		else:
			self.total_width = (self.side_room * 2)+self.pipe_diameter_list[self.first_pipe]
			self.row1_x = Functions.XofRow1(self.side_room, self.pipe_diameter_list[self.first_pipe])
			if self.radioButton_twoRows.isChecked() == True:
				self.total_width += self.x_distance+self.pipe_diameter_list[self.first_pipe+1]
				self.row2_x = Functions.XofRow2(self.row1_x, self.x_distance, self.pipe_diameter_list[self.first_pipe],
									 self.pipe_diameter_list[self.first_pipe+1])
			else:
				self.row2_x = "N/A"

		if self.checkBox_bass.isChecked() == True:
			self.row_bass_x = self.total_width / 2

		else:
			self.row_bass_x = "N/A"
			self.bass_num = "N/A"

		# ------------------ Find Y value of Pipes------------------------
		# Check for bass and then find Y of bass pipes and first non bass pipes
		if self.checkBox_bass.isChecked() == True:
			self.pipe_y_list[self.FirstBassPipe] = self.end_room + (self.pipe_diameter_list[self.FirstBassPipe] / 2)

			for n in range(self.FirstBassPipe + 2, self.first_pipe):
				self.pipe_y_list[n] = self.pipe_y_list[n - 1] + (self.pipe_diameter_list[n - 1] / 2) + self.dist_added + (self.pipe_diameter_list[n] / 2)

			self.pipe_y_list[self.first_pipe] = self.pipe_y_list[self.first_pipe-1] + (self.pipe_diameter_list[self.first_pipe - 1] / 2) + self.dist_added + (self.pipe_diameter_list[self.first_pipe] / 2)
		else:
			self.pipe_y_list[self.first_pipe] = self.end_room + (self.pipe_diameter_list[self.first_pipe] / 2)

		# Non bass pipes
		if self.radioButton_twoRows.isChecked() == True:
			# First row
			for n in range(self.first_pipe + 2, self.number_of_pipes + 1, 2):
				self.pipe_y_list[n] = self.pipe_y_list[n - 2] + self.pipe_radius_list[n - 2] + self.distance + self.pipe_radius_list[n]
			# Second row
			for n in range(self.first_pipe + 1, self.number_of_pipes + 1, 2):
				if n == self.number_of_pipes:
					if self.number_of_pipes % 2 == 0:
						self.pipe_y_list[n] = self.pipe_y_list[n - 2] + self.pipe_radius_list[n - 2] + self.distance + self.pipe_radius_list[n]
					else:
						self.pipe_y_list[n] = (((self.pipe_y_list[n + 1]-(self.pipe_diameter_list[n + 1] / 2)) - (self.pipe_y_list[n - 1] + (self.pipe_diameter_list[n - 1] / 2))) / 2) + self.pipe_y_list[n - 1] + (self.pipe_diameter_list[n - 1] / 2)
				else:
					self.pipe_y_list[n] = (((self.pipe_y_list[n + 1] - (self.pipe_diameter_list[n + 1] / 2)) - (
					self.pipe_y_list[n - 1] + (self.pipe_diameter_list[n - 1] / 2))) / 2) + self.pipe_y_list[n - 1] + (
									self.pipe_diameter_list[n - 1] / 2)
		else:
			#Single row
			for n in range(self.first_pipe + 1, self.number_of_pipes + 1):
				self.pipe_y_list[n] = self.pipe_y_list[n - 1] + (self.pipe_diameter_list[n - 1] / 2) + self.distance + (self.pipe_diameter_list[n] / 2)
		for n in range(self.first_pipe + 1, self.number_of_pipes + 1):
			if self.pipe_y_list[n] - self.pipe_y_list[n - 1] < 0.75:
				self.pipe_y_list[n] = self.pipe_y_list[n - 1] + 0.75

		# Show results on result window
		if self.first_run:
			self.length_position = 0
			self.treeWidget_calculated.clear()
			
			for x in range(1, self.number_of_pipes+1):
				self.calculated_pipe_list[x] = [str(x), str(Functions.rulerfrac(self.pipe_y_list[x]))]
				self.treeWidget_calculated.addTopLevelItem(QTreeWidgetItem(self.calculated_pipe_list[x]))

			if self.x_distance < 0:
				self.label_xDistance.setText("{} {}".format("X Overlap:", Functions.rulerfrac(abs(self.x_distance))))
			else:
				self.label_xDistance.setText("{} {}".format("X Distance:", Functions.rulerfrac(abs(self.x_distance))))

			self.label_yDistance.setText("{} {}".format("Y Distance:", self.distance))
			self.label_distAdded.setText("{} {}".format("Distance Added:", self.dist_added))

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
			self.update()

		#Check if each row is being used and convert into fraction if so
		if isinstance(self.row1_x, float):
			self.row1_x = Functions.rulerfrac(self.row1_x)
		if isinstance(self.row2_x, float):
			self.row2_x = Functions.rulerfrac(self.row2_x)

		#Create labels to display rows
		if self.first_run:
			self.label_rowOne.setText("{} {}".format("Row One:", self.row1_x))
			self.label_rowTwo.setText("{} {}".format("Row Two:", self.row2_x))
			if self.checkBox_bass.isChecked() == True:
				self.label_middleRow.setText("{} {}".format("Middle Row:", Functions.rulerfrac(self.row_bass_x)))
				self.label_bassPipes.setText("{} {}".format("Bass Pipes:", self.bass_num.get()))
			else:
				self.label_middleRow.setText("{} {}".format("Middle Row:", self.row_bass_x))
				self.label_bassPipes.setText("{} {}".format("Bass Pipes:", self.bass_num))

			self.x_distance = 0
			self.dist_added = 0

		#Calculate total length of toe board
		self.total_length = self.pipe_y_list[self.number_of_pipes] + self.pipe_radius_list[self.number_of_pipes] + self.end_length

		if self.first_run:
			self.label_totalWidth.setText("{} {}".format("Total Width:", Functions.rulerfrac(self.total_width)))

		self.label_totalLength.setText("{} {}".format("Total Length:", Functions.rulerfrac(self.total_length)))

		self.first_run = True

	# Clear all inputs and reset all checkboxes and radio buttons
	def on_new_click(self):
		self.lineEdit_jobName.clear()
		self.lineEdit_rankName.clear()
		self.lineEdit_sideRoom.clear()
		self.lineEdit_endRoom.clear()

		self.radioButton_twoRows.click()
		self.checkBox_wood.setCheckState(False)
		self.lineEdit_woodDepth1.clear()
		self.lineEdit_woodDepth2.clear()
		self.checkBox_bass.setCheckState(False)
		self.lineEdit_bassPipeNum.clear()

		self.treeWidget_pipes.clear()
		self.lineEdit_bodySize.clear()
		self.lineEdit_bulkAddNum.clear()

		self.treeWidget_calculated.clear()
		self.label_rowOne.setText("Row One:")
		self.label_rowTwo.setText("Row Two:")
		self.label_middleRow.setText("Middle Row:")
		self.label_bassPipes.setText("Bass Pipes:")

		self.label_xDistance.setText("X Distance:")
		self.label_yDistance.setText("Y Distance:")
		self.label_distAdded.setText("Distance Added:")
		self.label_sideLength.setText("Side Length:")
		self.label_endLength.setText("End Length:")

		self.label_totalLength.setText("Total Length:")
		self.label_totalWidth.setText("Total Width:")


	# Method to update result page
	def update(self):
		self.label_totalLength.setText("{} {}".format("Total Length:", Functions.rulerfrac(self.total_length)))
		self.label_totalWidth.setText("{} {}".format("Total Width:", Functions.rulerfrac(self.total_width)))
		self.label_rowOne.setText("{} {}".format("Row One:", Functions.rulerfrac(self.row1_x)))
		self.label_rowTwo.setText("{} {}".format("Row Two:", Functions.rulerfrac(self.row2_x)))

		if self.checkBox_bass.isChecked():
			self.label_middleRow.setText("{} {}".format("Middle Row:", Functions.rulerfrac(self.row_bass_x)))
		else:
			self.label_middleRow.setText("{} {}".format("Middle Row:", self.row_bass_x))

		self.treeWidget_calculated.clear()

		for x in range(1, self.number_of_pipes+1):
			self.calculated_pipe_list[x] = [str(x), str(Functions.rulerfrac(self.pipe_y_list[x]))]
			self.treeWidget_calculated.addTopLevelItem(QTreeWidgetItem(self.calculated_pipe_list[x]))

		if self.x_distance < 0:
			self.x_relation = "Overlap"
			self.label_xDistance.setText("{} {}".format("X Overlap:", Functions.rulerfrac(abs(self.x_distance))))
		else:
			self.x_relation = "Distance"
			self.label_xDistance.setText("{} {}".format("X Distance:", Functions.rulerfrac(self.x_distance)))

		self.label_yDistance.setText("{} {}".format("Y Distance:", Functions.rulerfrac(self.distance)))
		self.label_distAdded.setText("{} {}".format("Dist Added:", Functions.rulerfrac(self.dist_added)))
		self.label_sideLength.setText("{} {}".format("Sides:", self.lineEdit_sideRoom.text()))
		self.label_endLength.setText("{} {}".format("Ends:", self.lineEdit_endRoom.text()))

	#Method for when length is increased
	def increase_length(self):
		self.distance += 0.0625
		self.length_position += 1
		self.dist_added = self.length_position * 0.0625
		self.first_run = False
		self.on_calculate_click()

	#Method for when length is decreased
	def decrease_length(self):
		if self.length_position > 0:
			self.distance -= 0.0625
			self.length_position -= 1
			self.dist_added = self.length_position * 0.0625
			self.first_run = False
			self.on_calculate_click()

	#Method for when width is increased
	def increase_width(self):
		self.x_distance += .0625

		if self.x_distance >= 0:
			self.distance = 0
		else:
			if self.checkBox_wood.isChecked():
				self.width_position += 1

			self.pipe_1_width = self.pipe_diameter_list[self.first_pipe]
			self.pipe_2_width = self.pipe_diameter_list[self.first_pipe + 1]
			self.pipe_3_width = self.pipe_diameter_list[self.first_pipe + 2]

			if not self.checkBox_wood.isChecked():
				self.chord_length_1 = Functions.chordlength(self.pipe_1_width / 2, ((self.pipe_1_width / 2) - abs(self.x_distance)))
				self.chord_length_2 = Functions.chordlength(self.pipe_2_width / 2, ((self.pipe_2_width / 2) - abs(self.x_distance)))
				self.chord_length_3 = Functions.chordlength(self.pipe_3_width / 2, ((self.pipe_3_width / 2) - abs(self.x_distance)))
				self.chord_remainder_1 = (self.pipe_1_width - self.chord_length_1) / 2
				self.chord_remainder_3 = (self.pipe_3_width - self.chord_length_3) / 2

				self.distance = self.chord_length_2 - (self.chord_remainder_1 + self.chord_remainder_3)

				if self.distance < 0:
					self.distance = 0

				self.length_position = 0
				self.dist_added = 0

		self.first_run = False
		self.on_calculate_click()

	#Method for when width is decreased
	def decrease_width(self):
		if self.x_distance > 0:
			self.x_distance = self.x_distance - .0625
		else:
			if self.checkBox_wood.isChecked():
				if self.width_position > 0:
					self.width_position -= 1
					self.x_distance -= .0625
				else:
					QMessageBox.warning(self, "Error", "Cannot decrease width if pipes are wood!", QMessageBox.Ok)

			else:
				if self.checkBox_wood.isChecked():
					if (self.side_room * 2) + self.pipe_diameter_list[self.FirstBassPipe] >= self.TotalWidth:
						QMessageBox.warning(self, "Error", "Cannot decrease width any more!", QMessageBox.Ok)
					else:
						self.x_distance -= .0625

						self.pipe_1_width = self.pipe_diameter_list[self.first_pipe]
						self.pipe_2_width = self.pipe_diameter_list[self.first_pipe + 1]
						self.pipe_3_width = self.pipe_diameter_list[self.first_pipe + 2]

						self.chord_length_1 = Functions.chordlength(self.pipe_1_width / 2, ((self.pipe_1_width / 2) - abs(self.x_distance)))
						self.chord_length_2 = Functions.chordlength(self.pipe_2_width / 2, ((self.pipe_2_width / 2) - abs(self.x_distance)))
						self.chord_length_3 = Functions.chordlength(self.pipe_3_width / 2, ((self.pipe_3_width / 2) - abs(self.x_distance)))
						self.chord_remainder_1 = (self.pipe_1_width - self.chord_length_1) / 2
						self.chord_remainder_3 = (self.pipe_3_width - self.chord_length_3) / 2

						self.distance = self.chord_length_2 - (self.chord_remainder_1 + self.chord_remainder_3)

						if self.distance < 0:
							self.distance = 0

						self.length_position = 0
						self.dist_added = 0
				else:
					self.x_distance -= .0625

					self.pipe_1_width = self.pipe_diameter_list[self.first_pipe]
					self.pipe_2_width = self.pipe_diameter_list[self.first_pipe + 1]
					self.pipe_3_width = self.pipe_diameter_list[self.first_pipe + 2]

					self.chord_length_1 = Functions.chordlength(self.pipe_1_width / 2,
															  ((self.pipe_1_width / 2) - abs(self.x_distance)))
					self.chord_length_2 = Functions.chordlength(self.pipe_2_width / 2,
															  ((self.pipe_2_width / 2) - abs(self.x_distance)))
					self.chord_length_3 = Functions.chordlength(self.pipe_3_width / 2,
															  ((self.pipe_3_width / 2) - abs(self.x_distance)))
					self.chord_remainder_1 = (self.pipe_1_width - self.chord_length_1) / 2
					self.chord_remainder_3 = (self.pipe_3_width - self.chord_length_3) / 2

					self.distance = self.chord_length_2 - (self.chord_remainder_1 + self.chord_remainder_3)

					if self.distance < 0:
						self.distance = 0

					self.length_position = 0
					self.dist_added = 0

		self.first_run = False
		self.on_calculate_click()



if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())
