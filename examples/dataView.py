import forks.objectlistview.ObjectListView as ObjectListView

import wx
import random
 
########################################################################
choices = ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"]
textCatalogue = {i: item for i, item in enumerate(choices)}

class Test():
	"""Pass objects into the list as items."""

	def __init__(self, text = None):
		global choices

		self.stars = random.randrange(0, 5)
		self.text = text or makeText()
		self.text_2 = random.randrange(0, 18)
		self.progress = random.randrange(10, 90)
		self.choice = choices[random.randrange(0, 18)]
		self.spin = random.randrange(0, 55)
		self.bmp = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
		self.check = random.choice([True, False])
		self.icon = makeText()
		self.star_image = wx.ArtProvider.GetBitmap(wx.ART_PLUS)
		self.button = lambda: onPress
		self.file = ["log.txt"]
		self.title = self.text

def onPress(row, column):
	print(f"onPress() from column {column.valueGetter} on item {row.text}")

def makeText():
	return random.choice(choices)

def makeList(leftBound, rightBond = None):
	if (rightBond):
		return [Test() for i in range(random.randrange(leftBound, rightBond))]
	return [Test() for i in range(leftBound)]

def formatStars(value):
	if (value is None):
		return ""
	return "*" * int(value)

def formatStarsGroup(value):
	if (value is None):
		return "No Stars"
	return f"{value} Stars"

def getText_2(row):
	try:
		return textCatalogue[row.text_2]
	except AttributeError:
		return textCatalogue[row["text_2"]] #If you use a dictionary instead of objects, you must access their values like keys

def setText_2(row, value):
	row.text = value

def formatImage(value):
	return [wx.ArtProvider.GetBitmap(wx.ART_PLUS), wx.ArtProvider.GetBitmap(wx.ART_MINUS), wx.ArtProvider.GetBitmap(wx.ART_MINUS)]

def getIcon_2(row):
	if (row.text in ["Lorem", "ipsum", "dolor", "sit", "amet"]):
		return wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_PLUS))

########################################################################

def onGroupSelected(event):
	print(f"Selected Group: {event.group.title}")
	event.Skip()

def onSelectionChanged(event):
	print(f"Selected Row: {event.row.text}")
	event.Skip()

def onRightClick(event):
	print(f"Right Clicked: {event.row.text}")
	event.Skip()

def onDoubleClick(event):
	print(f"Double Clicked: {event.row.text}")
	event.Skip()

def onColumnClick(event):
	print(f"Column Clicked: {event.index}")
	event.Skip()

def onColumnRightClick(event):
	print(f"Column Right Clicked: {event.index}")
	event.Skip()

def onReorder(event):
	print(f"Column Reordered: {event.index}")
	event.Skip()

def onSorting(event):
	print(f"Column Sorting: {event.index}; {event.ascending}")
	event.Skip()

def onSorted(event):
	print(f"Column Sorted: {event.index}; {event.ascending}")
	event.Skip()

def onCollapsing(event):
	print(f"Collapsing: {event.group.title}")
	event.Skip()

def onCollapsed(event):
	print(f"Collapsed: {event.group.title}")
	event.Skip()

def onExpanding(event):
	print(f"Expanding: {event.group.title}")
	event.Skip()

def onExpanded(event):
	print(f"Expanded: {event.group.title}")
	event.Skip()

def onCellEditStarting(event):
	print(f"Starting Edit for Row: {event.row.text}, in column: {event.index}")
	event.Skip()

def onCellEditStarted(event):
	print(f"Started Edit for Row: {event.row.text}, in column: {event.index}")
	event.Skip()

def onCellEditFinishing(event):
	print(f"Finishing Edit for Row: {event.row.text}, with a value of: {event.value}")
	event.Skip()

def onCellEditFinished(event):
	print(f"Finished Edit for Row: {event.row.text}")
	event.Skip()

def myFilter(rows):
	return [item for item in rows if (item.text in ["Lorem", "ipsum", "dolor", "sit", "amet"])]

def myCompare(item1, item2, column, ascending):
	#Override column as example
	value1 = item1.text
	value2 = item2.text

	if ((value1 is None, value1) > (value2 is None, value2)):
		return (1, -1)[ascending]
	elif ((value1 is None, value1) < (value2 is None, value2)):
		return (-1, 1)[ascending]
	else:
		return 0

def onMenuCreate(event):
	if (event.row == None):
		print(f"Creating Menu: {event.menu}; for column: {event.column.title}")
	else:
		print(f"Creating Menu: {event.menu}; for row: {event.row.text}")
	event.Skip()

def onMenuSelect(event):
	if (event.row == None):
		print(f"Selected Menu Item: {event.item}; for column: {event.column.title}")
	else:
		print(f"Selected Menu Item: {event.item}; for row: {event.row.text}")
	event.Skip()

def menuFunction(row, column, item):
	if (row == None):
		print(f"Special function triggered by {item.GetLabel()}; for column: {column.title}")
	else:
		print(f"Special function triggered by {item.GetLabel()}; for row: {row.text}")

def menuCheckState(row, column):
	return column.GetIndex() % 2

def formatMenu(row, column):
	return f"!! {row.text} !!"

########################################################################
class MainPanel(wx.Panel):
	#----------------------------------------------------------------------
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.products = makeList(20000)
		# self.products = makeList(20, 22)
		# self.products = [Test("2"), Test("3"), Test("4"), Test("1"), Test("5"), Test("6")]
 
		self.dataOlv = ObjectListView.DataObjectListView(self, wx.ID_ANY, hideFirstIndent = True, singleSelect = False)#, showGroups = True)
		# self.dataOlv = ObjectListView.DataObjectListView(self, wx.ID_ANY, useWeakRefs = False)# If you use dictionaries instead of objects, you useWeakRefs must be false

		self.dataOlv.Bind(ObjectListView.EVT_DATA_GROUP_SELECTED, onGroupSelected)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_SELECTION_CHANGED, onSelectionChanged)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_RIGHT_CLICK, onRightClick)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_ACTIVATED, onDoubleClick)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_COLUMN_HEADER_LEFT_CLICK, onColumnClick)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_COLUMN_HEADER_RIGHT_CLICK, onColumnRightClick)

		self.dataOlv.Bind(ObjectListView.EVT_DATA_REORDER, onReorder)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_SORTING, onSorting)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_SORTED, onSorted)

		self.dataOlv.Bind(ObjectListView.EVT_DATA_COLLAPSING, onCollapsing)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_COLLAPSED, onCollapsed)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_EXPANDING, onExpanding)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_EXPANDED, onExpanded)

		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_EDIT_STARTING, onCellEditStarting)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_EDIT_STARTED, onCellEditStarted)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_EDIT_FINISHING, onCellEditFinishing)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_CELL_EDIT_FINISHED, onCellEditFinished)

		self.dataOlv.Bind(ObjectListView.EVT_DATA_MENU_CREATING, onMenuCreate)
		self.dataOlv.Bind(ObjectListView.EVT_DATA_MENU_ITEM_SELECTED, onMenuSelect)

		# self.dataOlv.Bind(ObjectListView.EVT_DATA_UNDO_FIRST, self.onEnableUndo)
		# self.dataOlv.Bind(ObjectListView.EVT_DATA_UNDO_EMPTY, lambda event: self.onEnableUndo(event, False))
		# self.dataOlv.Bind(ObjectListView.EVT_DATA_REDO_FIRST, self.onEnableRedo)
		# self.dataOlv.Bind(ObjectListView.EVT_DATA_REDO_EMPTY, lambda event: self.onEnableRedo(event, False))
		self.setBooks()
		self.dataOlv.SetAlwaysGroupByColumn(2)

		self.dataOlv.showContextMenu = True
		self.dataOlv.contextMenu.AddItem("Lorem")
		self.dataOlv.contextMenu.AddItem("ipsum", function = menuFunction)
		self.dataOlv.contextMenu.AddItem()
		self.dataOlv.contextMenu.AddItem("Check 1", check = True)
		self.dataOlv.contextMenu.AddItem("Check 2", check = "check")
		self.dataOlv.contextMenu.AddItem("Check 3", check = menuCheckState)
		self.dataOlv.contextMenu.AddItem(formatMenu)
		self.dataOlv.contextMenu.AddItem("I only show up for this row", row = self.products[1])
		self.dataOlv.contextMenu.AddItem("I only show up for this column", column = 1)
		self.dataOlv.contextMenu.AddItem("I only show up for this row and column", row = self.products[0], column = 0)

		# self.dataOlv.showColumnContextMenu = True
		# self.dataOlv.columnContextMenu.AddItem("Lorem")
		# self.dataOlv.columnContextMenu.AddItem("Ipsum", function = menuFunction)


		#Create an update button
		updateBtn = wx.Button(self, wx.ID_ANY, "Add More")
		updateBtn.Bind(wx.EVT_BUTTON, self.updateControl)

		filterBtn = wx.Button(self, wx.ID_ANY, "Toggle Filter")
		filterBtn.Bind(wx.EVT_BUTTON, self.filterControl)

		compareBtn = wx.Button(self, wx.ID_ANY, "Toggle Compare")
		compareBtn.Bind(wx.EVT_BUTTON, self.compareControl)

		menuBtn = wx.Button(self, wx.ID_ANY, "Toggle Context Menu")
		menuBtn.Bind(wx.EVT_BUTTON, self.menuControl)

		self.undoBtn = wx.Button(self, wx.ID_ANY, "Undo")
		self.undoBtn.Bind(wx.EVT_BUTTON, self.undoControl)
		self.undoBtn.Enable(False)

		self.redoBtn = wx.Button(self, wx.ID_ANY, "Redo")
		self.redoBtn.Bind(wx.EVT_BUTTON, self.redoControl)
		self.redoBtn.Enable(False)
 
		#Create some sizers
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		buttonSizer = wx.WrapSizer(wx.HORIZONTAL)
 
		mainSizer.Add(self.dataOlv, 1, wx.ALL|wx.EXPAND, 5)
		buttonSizer.Add(updateBtn, 1, wx.ALL|wx.CENTER, 5)
		buttonSizer.Add(filterBtn, 1, wx.ALL|wx.CENTER, 5)
		buttonSizer.Add(compareBtn, 1, wx.ALL|wx.CENTER, 5)
		buttonSizer.Add(menuBtn, 1, wx.ALL|wx.CENTER, 5)
		buttonSizer.Add(self.undoBtn, 1, wx.ALL|wx.CENTER, 5)
		buttonSizer.Add(self.redoBtn, 1, wx.ALL|wx.CENTER, 5)
		mainSizer.Add(buttonSizer, 0, wx.ALL|wx.CENTER, 5)
		self.SetSizer(mainSizer)
 
	#----------------------------------------------------------------------
	def updateControl(self, event):
		print ("Updating...")
		self.products.extend(makeList(20, 22))
		self.dataOlv.SetObjects(self.products)
		self.Refresh()
		event.Skip()

	def filterControl(self, event):
		if (not self.dataOlv.filter):
			print ("Filtering...")
			self.dataOlv.SetFilter(myFilter)
		else:
			print ("Unfiltering...")
			self.dataOlv.SetFilter(None)
		self.Refresh()
		event.Skip()

	def compareControl(self, event):
		if (not self.dataOlv.compareFunction):
			print ("Custom Comparing...")
			self.dataOlv.SetCompareFunction(myCompare)
		else:
			print ("Default Comparing...")
			self.dataOlv.SetCompareFunction(None)
		self.Refresh()
		event.Skip()

	def menuControl(self, event):
		if (not self.dataOlv.showContextMenu):
			print ("Applying Context Menu...")
			self.dataOlv.showContextMenu = True
		else:
			print ("Unapplying Context Menu...")
			self.dataOlv.showContextMenu = False
		self.Refresh()
		event.Skip()

	def onEnableUndo(self, event, state = True):
		self.undoBtn.Enable(state)
		event.Skip()

	def onEnableRedo(self, event, state = True):
		self.redoBtn.Enable(state)
		event.Skip()

	def undoControl(self, event):
		self.dataOlv.Undo()
		event.Skip()

	def redoControl(self, event):
		self.dataOlv.Redo()
		event.Skip()

	#----------------------------------------------------------------------
	def setBooks(self, data=None):
		self.dataOlv.SetColumns([
			ObjectListView.DataColumnDefn(title = "Text 1",		align = "right", 	width = -1, valueGetter = "text"),#, 		isSpaceFilling = True),
			ObjectListView.DataColumnDefn(title = "Text 2",		align = "left", 	width = -1, valueGetter = getText_2, 	valueSetter = setText_2),
			ObjectListView.DataColumnDefn(title = "Stars 1",	align = "right", 	width = 50, valueGetter = "stars", 		stringConverter = formatStars, groupKeyConverter = formatStarsGroup),
			ObjectListView.DataColumnDefn(title = "Stars 2",	align = "left", 	width = 50, valueGetter = "stars", 		renderer = "multi_bmp", 	rendererArgs = ["star_image"]),
			ObjectListView.DataColumnDefn(title = "Choice 1",	align = "right", 	width = 50, valueGetter = "choice",		renderer = "choice", 		rendererArgs = [choices]),
			ObjectListView.DataColumnDefn(title = "Image 1",	align = "left", 	width = 50, valueGetter = "bmp",		renderer = "bmp"),
			ObjectListView.DataColumnDefn(title = "Image 2",	align = "right", 	width = 50, 							renderer = "multi_bmp", 	rendererArgs = [formatImage]),
			ObjectListView.DataColumnDefn(title = "Progress",	align = "left", 	width = 50, valueGetter = "progress",	renderer = "progress"),
			ObjectListView.DataColumnDefn(title = "Icon 1",		align = "left", 	width = 50, valueGetter = "icon",		renderer = "icon", 			rendererArgs = [wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_MINUS))]),
			ObjectListView.DataColumnDefn(title = "Icon 2",		align = "right", 	width = 50, valueGetter = "text",		renderer = "icon", 			rendererArgs = [getIcon_2]),
			ObjectListView.DataColumnDefn(title = "Spin",		align = "left", 	width = 50, valueGetter = "spin",		renderer = "spin", 			rendererArgs = [0, 55]),
			ObjectListView.DataColumnDefn(title = "Check",		align = "left", 	width = 50, valueGetter = "check",		renderer = "check"),
			ObjectListView.DataColumnDefn(title = "Button",		align = "left", 	width = 80, valueGetter = "button",		renderer = "button", 		rendererKwargs = {"enabled": True, "text": "Press Me"}),
			ObjectListView.DataColumnDefn(title = "File",		align = "left", 	width = 80, valueGetter = "file",		renderer = "file", 			isSpaceFilling = True),
		])
 
		self.dataOlv.SetObjects(self.products)

########################################################################
class MainFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, 
						  title="ObjectListView Demo", size=(800,600))
		panel = MainPanel(self)
 
########################################################################
class GenApp(wx.App):
 
	#----------------------------------------------------------------------
	def __init__(self, redirect=False, filename=None):
		wx.App.__init__(self, redirect, filename)
 
	#----------------------------------------------------------------------
	def OnInit(self):
		# create frame here
		frame = MainFrame()
		frame.Show()
		return True
 
#----------------------------------------------------------------------
def main():
	"""
	Run the demo
	"""
	app = GenApp()
	app.MainLoop()
 
if __name__ == "__main__":
	main()