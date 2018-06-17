import unittest
import controller as GUI_Maker


class TestController(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		GUI_Maker.warnings.simplefilter("ignore")

	@classmethod
	def tearDownClass(cls):
		GUI_Maker.warnings.simplefilter("default")

	def setUp(self):
		self.gui = GUI_Maker.build()
		pass

	def tearDown(self):
		pass

	def test_label(self):
		frame_1 = self.gui.addWindow()
		frame_2 = self.gui.addWindow(label = 1)
		frame_3 = self.gui.addWindow(label = "Lorem")

		self.assertEqual(frame_1.label, None)
		self.assertEqual(frame_2.label, 1)
		self.assertEqual(frame_3.label, "Lorem")

	def test_nesting(self):
		with self.gui.addWindow() as myFrame:
			with myFrame.addSizerBox() as mySizer:
				self.assertIn(mySizer, myFrame)

				self.assertEqual(len(mySizer), 0)
				with mySizer.addText("Lorem") as myWidget:
					self.assertIn(myWidget, mySizer)

				self.assertEqual(len(mySizer), 1)
				with mySizer.addText("Ipsum", label = "dolor") as myWidget:
					self.assertIn(myWidget, mySizer)

				self.assertEqual(len(mySizer), 2)

	def test_sizers(self):
		with self.gui.addWindow() as myFrame:
			with myFrame.addSizerBox() as mySizer:
				self.assertEqual(mySizer.type.lower(), "box")
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.BoxSizer)

			with myFrame.addSizerGrid(rows = 2, columns = 3) as mySizer:
				self.assertEqual(mySizer.type.lower(), "grid")
				self.assertEqual(mySizer.rows, 2)
				self.assertEqual(mySizer.columns, 3)
				self.assertIsNone(mySizer.substitute)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.GridSizer)

			with myFrame.addSizerGridFlex(text = "Lorem") as mySizer:
				self.assertEqual(mySizer.type.lower(), "flex")
				self.assertIsNotNone(mySizer.substitute)
				self.assertEqual(mySizer.substitute.type.lower(), "text")
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.FlexGridSizer)

			with myFrame.addSizerGridBag() as mySizer:
				self.assertEqual(mySizer.type.lower(), "bag")
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.GridBagSizer)

			with myFrame.addSizerWrap() as mySizer:
				self.assertEqual(mySizer.type.lower(), "wrap")
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.WrapSizer)

			with myFrame.addSizerText() as mySizer:
				self.assertEqual(mySizer.type.lower(), "text")
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.StaticBoxSizer)

			# addSplitterDouble
			# addSplitterQuad
			# addSplitterPoly

			# addNotebook 
			# addNotebookAui

	def test_widgets(self):
		with self.gui.addWindow() as myFrame:
			with myFrame.addSizerBox() as mySizer:
				with mySizer.addText("Lorem") as myWidget:
					self.assertEqual(myWidget.type.lower(), "text")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticText)
					self.assertEqual(myWidget.getValue(), "Lorem")
					myWidget.setValue("Sit")
					self.assertEqual(myWidget.getValue(), "Sit")

				with mySizer.addHyperlink() as myWidget:
					self.assertEqual(myWidget.type.lower(), "hyperlink")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.HyperlinkCtrl)

				with mySizer.addEmpty() as myWidget:
					self.assertEqual(myWidget.type.lower(), "empty")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticText)

				with mySizer.addLine() as myWidget:
					self.assertEqual(myWidget.type.lower(), "line")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticLine)

				with mySizer.addProgressBar(myInitial = 0) as myWidget:
					self.assertEqual(myWidget.type.lower(), "progressbar")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Gauge)
					self.assertEqual(myWidget.getValue(), 0)
					myWidget.setValue(30)
					self.assertEqual(myWidget.getValue(), 30)

				with mySizer.addListDrop(choices = [1, "2", 3]) as myWidget:
					self.assertEqual(myWidget.type.lower(), "listdrop")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Choice)
					self.assertEqual(myWidget.getValue(), "1")
					self.assertEqual(myWidget.getAll(), ["1", "2", "3"])
					myWidget.setSelection("2")
					self.assertEqual(myWidget.getValue(), "2")
					myWidget.setSelection(2)
					self.assertEqual(myWidget.getValue(), "3")
					myWidget.setValue(range(4, 7))
					self.assertEqual(myWidget.getValue(), "4")

				with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnNames = {0: "Lorem", 1: "Ipsum"}, boldHeader = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "listfull")
					self.assertEqual(myWidget.subType.lower(), "normal")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ListCtrl)
					self.assertEqual(myWidget.getValue(), [["1", "2"]])
					self.assertEqual(myWidget.getAll(), [["1", "2"], ["3", "4"], ["5", ""]])

				with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnNames = {0: "Lorem", 1: "Ipsum"}, editable = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "listfull")
					self.assertEqual(myWidget.subType.lower(), "editable")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ListCtrl)
					self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetList.ListFull_Editable)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.mixins.listctrl.TextEditMixin)
					self.assertEqual(myWidget.getValue(), [["1", "2"]])

				with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnNames = {0: "Lorem", 1: "Ipsum"}, ultimate = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "listfull")
					self.assertEqual(myWidget.subType.lower(), "ultimate")
					self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetList.ListFull)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.agw.ultimatelistctrl.UltimateListCtrl)
					self.assertEqual(myWidget.getValue(), [["1", "2"]])

				with mySizer.addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None}) as myWidget:
					self.assertEqual(myWidget.type.lower(), "listtree")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.TreeCtrl)
					self.assertEqual(myWidget.getValue(), None)
					self.assertEqual(myWidget.getAll(), {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None})
					# myWidget.setSelection("Lorem")


				with mySizer.addInputSlider() as myWidget:
					self.assertEqual(myWidget.type.lower(), "slider")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Slider)

				with mySizer.addInputBox() as myWidget:
					self.assertEqual(myWidget.type.lower(), "inputbox")
					self.assertEqual(myWidget.subType.lower(), "normal")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.TextCtrl)

				with mySizer.addInputBox(ipAddress = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "inputbox")
					self.assertEqual(myWidget.subType.lower(), "ipaddress")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.masked.ipaddrctrl.IpAddrCtrl)

				with mySizer.addInputSearch() as myWidget:
					self.assertEqual(myWidget.type.lower(), "inputsearch")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.SearchCtrl)

				with mySizer.addInputSpinner() as myWidget:
					self.assertEqual(myWidget.type.lower(), "inputspinner")
					self.assertEqual(myWidget.subType.lower(), "normal")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.SpinCtrl)

				with mySizer.addInputSpinner(useFloat = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "inputspinner")
					self.assertEqual(myWidget.subType.lower(), "float")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.agw.floatspin.FloatSpin)

				with mySizer.addButton() as myWidget:
					self.assertEqual(myWidget.type.lower(), "button")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Button)

				with mySizer.addButtonToggle() as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttontoggle")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ToggleButton)

				with mySizer.addButtonCheck() as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttoncheck")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.CheckBox)

				with mySizer.addButtonCheckList() as myWidget:
					self.assertEqual(myWidget.type.lower(), "checklist")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.CheckListBox)

				with mySizer.addButtonRadio() as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonradio")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.RadioButton)

				with mySizer.addButtonRadioBox() as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonradiobox")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.RadioBox)

				# with mySizer.addButtonHelp() as myWidget:
				# 	self.assertEqual(myWidget.type.lower(), "")
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.)

				with mySizer.addButtonImage() as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonimage")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapButton)

				with mySizer.addButtonImage(toggle = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonimage")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapToggleButton)

				with mySizer.addButtonImage(text = "Lorem") as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonimage")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapTextButton)

				with mySizer.addButtonImage(text = "Ipsum", toggle = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "buttonimage")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapTextToggleButton)

				with mySizer.addImage() as myWidget:
					self.assertEqual(myWidget.type.lower(), "image")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticBitmap)

				with mySizer.addPickerColor() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickercolor")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ColourPickerCtrl)

				with mySizer.addPickerFont() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerfont")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.FontPickerCtrl)

				with mySizer.addPickerFile() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerfile")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.FilePickerCtrl)

				with mySizer.addPickerFile(directoryOnly = True) as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerfile")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.DirPickerCtrl)

				with mySizer.addPickerFileWindow() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerfilewindow")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.GenericDirCtrl)

				with mySizer.addPickerDate() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerdate")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.DatePickerCtrl)

				with mySizer.addPickerDateWindow() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickerdatewindow")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.CalendarCtrl)

				with mySizer.addPickerTime() as myWidget:
					self.assertEqual(myWidget.type.lower(), "pickertime")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.TimePickerCtrl)

				with mySizer.addCanvas() as myWidget:
					self.assertEqual(myWidget.type.lower(), "canvas")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Panel)

				with mySizer.addTable() as myWidget:
					self.assertEqual(myWidget.type.lower(), "table")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.grid.Grid)
					self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetTable.Table)

	def test_menus(self):
		with self.gui.addWindow() as myFrame:
			with myFrame.addMenu() as myMenu:
				self.assertEqual(myMenu.type.lower(), "menu")
				self.assertIsInstance(myMenu.thing, GUI_Maker.wx.Menu)

				with myMenu.addItem() as myMenuItem:
					self.assertEqual(myMenuItem.type.lower(), "menuitem")
					self.assertEqual(myMenuItem.subType.lower(), "normal")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addItem(check = True) as myMenuItem:
					self.assertEqual(myMenuItem.type.lower(), "menuitem")
					self.assertEqual(myMenuItem.subType.lower(), "check")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addItem(check = False) as myMenuItem:
					self.assertEqual(myMenuItem.type.lower(), "menuitem")
					self.assertEqual(myMenuItem.subType.lower(), "radio")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addSeparator() as myMenuItem:
					self.assertEqual(myMenuItem.type.lower(), "menuitem")
					self.assertEqual(myMenuItem.subType.lower(), "separator")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addSub() as mySubMenu:
					self.assertEqual(mySubMenu.type.lower(), "menu")
					self.assertIsInstance(mySubMenu.thing, GUI_Maker.wx.Menu)

					with mySubMenu.addItem() as myMenuItem:
						self.assertEqual(myMenuItem.type.lower(), "menuitem")
						self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

			with myFrame.addSizerBox() as mySizer:
				with mySizer.addToolBar() as myToolbar:
					self.assertEqual(myToolbar.type.lower(), "toolbar")
					self.assertIsInstance(myToolbar.thing, GUI_Maker.wx.ToolBar)

					with myToolbar.addItem() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "normal")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addItem(check = True) as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "check")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addItem(check = False) as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "radio")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addStretchableSpace() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "stretchable")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addSeparator() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "separator")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addText() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "text")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticText)

					with myToolbar.addHyperlink() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "hyperlink")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.HyperlinkCtrl)

					with myToolbar.addLine() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "line")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticLine)

					with myToolbar.addProgressBar() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "progressbar")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Gauge)

					with myToolbar.addListDrop() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "listdrop")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Choice)

					with myToolbar.addListFull() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "listfull")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ListCtrl)

					with myToolbar.addListTree() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "listtree")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.TreeCtrl)

					with myToolbar.addInputSlider() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "slider")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Slider)

					with myToolbar.addInputBox() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "inputbox")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.TextCtrl)

					with myToolbar.addInputSearch() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "inputsearch")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.SearchCtrl)

					with myToolbar.addInputSpinner() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "inputspinner")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.SpinCtrl)

					with myToolbar.addButton() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "button")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Button)

					with myToolbar.addButtonToggle() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "buttontoggle")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ToggleButton)

					with myToolbar.addButtonCheck() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "buttoncheck")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.CheckBox)

					with myToolbar.addButtonCheckList() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "checklist")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.CheckListBox)

					with myToolbar.addButtonRadio() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "buttonradio")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.RadioButton)

					with myToolbar.addButtonRadioBox() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "buttonradiobox")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.RadioBox)

					# with myToolbar.addButtonHelp() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
					# 	self.assertEqual(myToolbarItem.subType.lower(), "")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
					# 	self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.)

					with myToolbar.addButtonImage() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "buttonimage")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.lib.buttons.GenBitmapButton)

					with myToolbar.addImage() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "image")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticBitmap)

					with myToolbar.addPickerColor() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickercolor")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ColourPickerCtrl)

					with myToolbar.addPickerFont() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickerfont")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.FontPickerCtrl)

					with myToolbar.addPickerFile() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickerfile")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.FilePickerCtrl)

					with myToolbar.addPickerFileWindow() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickerfilewindow")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.GenericDirCtrl)

					with myToolbar.addPickerDate() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickerdate")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.DatePickerCtrl)

					with myToolbar.addPickerDateWindow() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickerdatewindow")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.CalendarCtrl)

					with myToolbar.addPickerTime() as myToolbarItem:
						self.assertEqual(myToolbarItem.type.lower(), "toolbaritem")
						self.assertEqual(myToolbarItem.subType.lower(), "pickertime")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.TimePickerCtrl)

	# Menu Popup
	# Status Bar

	def test_dialogs(self):
		pass

		#Custom dialog
		#status bar
					

if __name__ == '__main__':
	unittest.main()