import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker
import random

#Create GUI object
gui = GUI_Maker.build()

def makeList(leftBound, rightBond):
	myList = []
	for i in range(random.randrange(leftBound, rightBond)):
		myList.append([random.randrange(0, 5), random.choice(["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"])])
	return myList

#Bound Functions
def onChange(event):
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]
		myWidget.setValue(makeList(4, 7))
	event.Skip()

def onAppend(event):
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]
		myWidget.appendValue(makeList(2, 5))
	event.Skip()

def onColor(event):
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]
		for i in range(random.randrange(3, 6)):
			myWidget.setRowColor(random.randrange(0, len(myWidget)), (255, 50, 50))
	event.Skip()

def onClick(event):
	myWidget = gui[0][event]
	selection = myWidget.getValue()

	for item in selection:
		print(item.text)
	event.Skip()

def onCheck(event):
	
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]
		selection = myWidget.getChecked()

		for subItem in selection:
			print(subItem.text)
	event.Skip()

def onSort(event):
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]

		if (myWidget.getSortColumn() == None):
			myWidget.sortBy("text")
		elif (myWidget.getSortColumn() == "text"):
			myWidget.sortBy("rating")
		else:
			myWidget.sortBy()
	event.Skip()

def onUserSort(event):
	state = gui[0].getValue(event)
	for item in ["list_1", "list_2"]:
		myWidget = gui[0][item]
		myWidget.enableUserSort(state)
		
	event.Skip()

#Manipulator Functions
def getStatus(item):
	if (item.text in ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed"]):
		return "good"
	return "bad"

def formatText(value):
	if (value is None):
		return ""
	return "*" * int(value)

def formatGroup(value):
	if (value is None):
		return "No Stars"
	return f"{value} Stars"

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#groups

	#Initialize Frame
	with gui.addWindow(label = 0, title = "List Widget") as myFrame:
		# myFrame.setWindowSize((400, 300))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 3, columns = 1) as mySizer:
			mySizer.growFlexRowAll()
			mySizer.growFlexColumn(0)

			with mySizer.addListFull(label = "list_1", choices = makeList(4, 7), columns = 2, columnLabels = {1: "text"}, columnFormatter = {0: formatText}, 
				check = 2, group = {1: True}, groupFormatter = {0: formatGroup}, columnTitles = {0: "rating", 1: "text", 2: "select"}, sortable = False,
				columnWidth = {0: 100}, editable = {1: True}, columnImage = {0: "bullet", 1: getStatus}) as myWidget:

				myWidget.addImage("bullet", "info", internal = True)
				myWidget.addImage("good", "lightBulb", internal = True)
				myWidget.addImage("bad", "error", internal = True)
				myWidget.showGroup(1)
				myWidget.refreshColumns()
				myWidget.refresh()

				myWidget.setFunction_click(onClick)

			with mySizer.addListFull(label = "list_2") as myWidget:
				myWidget.setColor(even = (200, 200, 200), odd = (250, 180, 180))
				myWidget.enableUserSort(False)

				myWidget.addImage("bullet", "info", internal = True)
				myWidget.addImage("good", "lightBulb", internal = True)
				myWidget.addImage("bad", "error", internal = True)

				myWidget.addColumn(title = "rating", width = 100, align = "right", image = "bullet", formatter = formatText, groupFormatter = formatGroup)
				myWidget.addColumn(title = "text", width = -1, label = "text", editable = True, image = getStatus, group = True)
				myWidget.showGroup(1)
				myWidget.addColumnCheck()
				myWidget.setValue(makeList(4, 7))
				myWidget.refresh()

				myWidget.setFunction_click(onClick)

		with myFrame.addSizerBox(vertical = False, flex = 0) as mySizer:
			mySizer.addButton("Change", myFunction = onChange)
			mySizer.addButton("Append", myFunction = onAppend)
			mySizer.addButton("Color", myFunction = onColor)
			mySizer.addButton("Get Checked", myFunction = onCheck)
			mySizer.addButton("Sort", myFunction = onSort)
			mySizer.addButtonToggle("Allow User Sort", myFunction = onUserSort)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()