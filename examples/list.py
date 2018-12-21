import os
import sys
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker
import random

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onChange(event):
	myWidget = gui[0]["myList"]
	myWidget.setValue(makeList(4, 7))
	event.Skip()

def onAppend(event):
	myWidget = gui[0]["myList"]
	myWidget.appendValue(makeList(2, 5))
	event.Skip()

def onColor(event):
	myWidget = gui[0]["myList"]
	for i in range(random.randrange(3, 6)):
		myWidget.setRowColor(random.randrange(0, len(myWidget)), (255, 50, 50))
	event.Skip()

def onClick(event):
	myWidget = gui[0][event]
	selection = myWidget.getValue()
	print(selection)
	event.Skip()

def onCheck(event):
	myWidget = gui[0]["myList"]
	selection = myWidget.getChecked()

	for subItem in selection:
		print(subItem.text)
	event.Skip()

def onSort(event):
	myWidget = gui[0]["myList"]

	column = myWidget.getSortColumn()
	print(column)
	if (column == None):
		myWidget.sortBy("text")
	elif (column == "text"):
		myWidget.sortBy("rating")
	else:
		myWidget.sortBy()
	event.Skip()

def onUserSort(event):
	state = gui[0].getValue(event)
	myWidget = gui[0]["myList"]
	myWidget.enableUserSort(state)
		
	event.Skip()

def onAction(event):
	print("ACTION!")
	event.Skip()

def onPrint(event):
	myWidget = gui[0]["myList"]

	value = myWidget.getValue()
	if (isinstance(value, dict)):
		for item in value["group"]:
			print(f"group: {item}")
		for item in value["row"]:
			print(f"row: {item.text}")
	else:
		for item in value:
			print(f"row: {item.text}")

	event.Skip()

def onExpandAll(event):
	myWidget = gui[0]["myList"]
	
	if (gui[0].getValue(event) == "Expand All"):
		myWidget.collapseAll()
	else:
		myWidget.expandAll()

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

#List Items
class Test():
	"""Pass objects into the list as items."""

	def __init__(self):
		self.stars = random.randrange(0, 5)
		self.text = random.choice(["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"])

def makeList(leftBound, rightBond):
	myList = []
	for i in range(random.randrange(leftBound, rightBond)):
		myList.append(Test())
	return myList

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#groups

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Full List Widget") as myFrame:
		myFrame.setWindowSize((800, 300))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 1, columns = 1) as mySizer:
			mySizer.growFlexRowAll()
			mySizer.growFlexColumn(0)

			with mySizer.addListFull(label = "myList", flex = 1, sortable = False) as myWidget:
				myWidget.setColor(even = (200, 200, 200), odd = (250, 180, 180))
				myWidget.enableUserSort(False)

				# myWidget.addImage("bullet", "info", internal = True)
				# myWidget.addImage("good", "lightBulb", internal = True)
				# myWidget.addImage("bad", "error", internal = True)

				# myWidget.addColumn(title = "rating", width = 100, label = "stars", align = "right", image = "bullet", formatter = formatText, groupFormatter = formatGroup)
				# myWidget.addColumn(title = "text", width = -1, label = "text", editable = True, image = getStatus, group = True)
				# myWidget.showGroup(1)
				# # myWidget.addColumnCheck()
				# myWidget.addColumnButton(title = "action", width = 100, label = "button", myFunction = onAction)

				# myWidget.setValue(makeList(4, 7))
				# myWidget.refresh()

				# myWidget.setFunction_click(onClick)

		with myFrame.addSizerBox(vertical = False, flex = 0) as mySizer:
			mySizer.addButton("Change", myFunction = onChange)
			mySizer.addButton("Append", myFunction = onAppend)
			mySizer.addButton("Color", myFunction = onColor)
			mySizer.addButton("Get Checked", myFunction = onCheck)
			mySizer.addButton("Sort", myFunction = onSort)
			mySizer.addButton("Print Selected", myFunction = onPrint)
			mySizer.addButtonToggle("Allow User Sort", myFunction = onUserSort)
			mySizer.addButtonList(["Expand All", "Collapse All"], myFunction = onExpandAll)

	with gui.addWindow(label = 1, title = "Drop List Widgets") as myFrame:
		myFrame.setWindowSize((800, 300))

		#Add Content
		with myFrame.addSizerGridFlex(rows = 1, columns = 5) as mySizer:
			mySizer.growFlexColumnAll()

			with mySizer.addListDrop(choices = ["Lorem", "Ipsum", "Dolor"]) as myWidget:
				pass

			mySizer.addListDrop(choices = ["Lorem", "Ipsum", "Dolor"], check = True, readOnly = True, check_text = "Sit Amet", default = (0, 2))

			with mySizer.addListDrop(check = True, readOnly = True, check_text = "Sit Amet") as myWidget:
				myWidget.setValue(["Lorem", "Ipsum", "Dolor"])
				myWidget.setSelection(("Ipsum",))

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(1)
	myFrame.showWindow()

	gui.finish()