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
		self.gui.close()
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
				self.assertEqual(mySizer.type, GUI_Maker.Types.box)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.BoxSizer)

			with myFrame.addSizerGrid(rows = 2, columns = 3) as mySizer:
				self.assertEqual(mySizer.type, GUI_Maker.Types.grid)
				self.assertEqual(mySizer.rows, 2)
				self.assertEqual(mySizer.columns, 3)
				self.assertIsNone(mySizer.substitute)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.GridSizer)

			with myFrame.addSizerGridFlex(text = "Lorem") as mySizer:
				self.assertEqual(mySizer.type, GUI_Maker.Types.flex)
				self.assertIsNotNone(mySizer.substitute)
				self.assertEqual(mySizer.substitute.type, GUI_Maker.Types.text)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.FlexGridSizer)

			with myFrame.addSizerGridBag() as mySizer:
				self.assertEqual(mySizer.type, GUI_Maker.Types.bag)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.GridBagSizer)

			with myFrame.addSizerWrap() as mySizer:
				self.assertEqual(mySizer.type, GUI_Maker.Types.wrap)
				self.assertIsInstance(mySizer.thing, GUI_Maker.wx.WrapSizer)

			with myFrame.addSizerText() as mySizer:
				self.assertEqual(mySizer.type, GUI_Maker.Types.text)
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
					self.assertEqual(myWidget.type, GUI_Maker.Types.text)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticText)
					self.assertEqual(myWidget.getValue(), "Lorem")
					myWidget.setValue("Sit")
					self.assertEqual(myWidget.getValue(), "Sit")

				with mySizer.addHyperlink() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.hyperlink)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.HyperlinkCtrl)

				with mySizer.addEmpty() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.empty)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticText)

				with mySizer.addLine() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.line)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticLine)

				with mySizer.addProgressBar(myInitial = 0) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.progressbar)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Gauge)
					self.assertEqual(myWidget.getValue(), 0)
					myWidget.setValue(30)
					self.assertEqual(myWidget.getValue(), 30)

				with mySizer.addListDrop(choices = [1, "2", 3]) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.drop)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Choice)
					self.assertEqual(myWidget.getValue(), 1)
					self.assertEqual(myWidget.getAll(), (1, "2", 3))
					myWidget.setSelection("2")
					self.assertEqual(myWidget.getValue(), "2")
					myWidget.setSelection(2)
					self.assertEqual(myWidget.getValue(), 3)
					myWidget.setValue(range(4, 7))
					self.assertEqual(myWidget.getValue(), "6")

				# with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnTitles = {0: "Lorem", 1: "Ipsum"}) as myWidget:
				# 	self.assertEqual(myWidget.type, GUI_Maker.Types.listfull)
				# 	self.assertEqual(myWidget.subType, GUI_Maker.Types.normal)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ListCtrl)
				# 	self.assertEqual(myWidget.getValue(), [["1", "2"]])
				# 	self.assertEqual(myWidget.getAll(), [["1", "2"], ["3", "4"], ["5", ""]])

				# with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnTitles = {0: "Lorem", 1: "Ipsum"}, editable = True) as myWidget:
				# 	self.assertEqual(myWidget.type, GUI_Maker.Types.listfull)
				# 	self.assertEqual(myWidget.subType, GUI_Maker.Types.editable)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ListCtrl)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetList.ListFull_Editable)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.mixins.listctrl.TextEditMixin)
				# 	self.assertEqual(myWidget.getValue(), [["1", "2"]])

				# with mySizer.addListFull(choices = [[1, "2"], range(3, 5), 5], columns = 2, columnTitles = {0: "Lorem", 1: "Ipsum"}, ultimate = True) as myWidget:
				# 	self.assertEqual(myWidget.type, GUI_Maker.Types.listfull)
				# 	self.assertEqual(myWidget.subType, GUI_Maker.Types.ultimate)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetList.ListFull)
				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.agw.ultimatelistctrl.UltimateListCtrl)
				# 	self.assertEqual(myWidget.getValue(), [["1", "2"]])

				with mySizer.addListTree(choices = {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None}) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.tree)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.TreeCtrl)
					self.assertEqual(myWidget.getValue(), None)
					# self.assertEqual(myWidget.getAll(), {"Lorem": [{"Ipsum": "Dolor"}, "Sit"], "Amet": None})
					# myWidget.setSelection("Lorem")


				with mySizer.addInputSlider() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.slider)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Slider)

				with mySizer.addInputBox() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.box)
					self.assertEqual(myWidget.subType, "normal")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.TextCtrl)

				with mySizer.addInputBox(ipAddress = True) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.box)
					self.assertEqual(myWidget.subType, "ipAddress")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.masked.ipaddrctrl.IpAddrCtrl)

				with mySizer.addInputSearch() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.search)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.SearchCtrl)

				with mySizer.addInputSpinner() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.spinner)
					self.assertEqual(myWidget.subType, "normal_base10")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.SpinCtrl)

				with mySizer.addInputSpinner(useFloat = True) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.spinner)
					self.assertEqual(myWidget.subType, "float")
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.agw.floatspin.FloatSpin)

				with mySizer.addButton() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.button)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Button)

				with mySizer.addButtonToggle() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.toggle)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ToggleButton)

				with mySizer.addButtonCheck() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.check)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.CheckBox)

				with mySizer.addButtonCheckList() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.checklist)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.CheckListBox)

				with mySizer.addButtonRadio() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.radio)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.RadioButton)

				with mySizer.addButtonRadioBox() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.radiobox)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.RadioBox)

				# with mySizer.addButtonHelp() as myWidget:
				# 	self.assertEqual(myWidget.type, GUI_Maker.Types.")				# 	self.assertIsInstance(myWidget.thing, GUI_Maker.wx.)

				with mySizer.addButtonImage() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.image)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapButton)

				with mySizer.addButtonImage(toggle = True) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.image)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapToggleButton)

				with mySizer.addButtonImage(text = "Lorem") as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.image)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapTextButton)

				with mySizer.addButtonImage(text = "Ipsum", toggle = True) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.image)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.buttons.GenBitmapTextToggleButton)

				with mySizer.addImage() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.image)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.StaticBitmap)

				with mySizer.addPickerColor() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.color)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.ColourPickerCtrl)

				with mySizer.addPickerFont() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.font)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.FontPickerCtrl)

				with mySizer.addPickerFile() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.file)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.FilePickerCtrl)

				with mySizer.addPickerFile(directoryOnly = True) as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.file)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.DirPickerCtrl)

				with mySizer.addPickerFileWindow() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.filewindow)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.GenericDirCtrl)

				with mySizer.addPickerDate() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.date)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.DatePickerCtrl)

				with mySizer.addPickerDateWindow() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.datewindow)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.adv.CalendarCtrl)

				with mySizer.addPickerTime() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.time)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.lib.masked.TimeCtrl)

				with mySizer.addCanvas() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.canvas)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.Panel)

				with mySizer.addTable() as myWidget:
					self.assertEqual(myWidget.type, GUI_Maker.Types.table)
					self.assertIsInstance(myWidget.thing, GUI_Maker.wx.grid.Grid)
					self.assertIsInstance(myWidget.thing, GUI_Maker.handle_WidgetTable._Table)

	def test_menus(self):
		with self.gui.addWindow() as myFrame:
			with myFrame.addMenu() as myMenu:
				self.assertEqual(myMenu.type, GUI_Maker.Types.menu)
				self.assertIsInstance(myMenu.thing, GUI_Maker.wx.Menu)

				with myMenu.addItem() as myMenuItem:
					self.assertEqual(myMenuItem.type, GUI_Maker.Types.menuitem)
					self.assertEqual(myMenuItem.subType, "normal")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addItem(check = True) as myMenuItem:
					self.assertEqual(myMenuItem.type, GUI_Maker.Types.menuitem)
					self.assertEqual(myMenuItem.subType, "check")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addItem(check = False) as myMenuItem:
					self.assertEqual(myMenuItem.type, GUI_Maker.Types.menuitem)
					self.assertEqual(myMenuItem.subType, "radio")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addSeparator() as myMenuItem:
					self.assertEqual(myMenuItem.type, GUI_Maker.Types.menuitem)
					self.assertEqual(myMenuItem.subType, "separator")
					self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

				with myMenu.addSub() as mySubMenu:
					self.assertEqual(mySubMenu.type, GUI_Maker.Types.menu)
					self.assertIsInstance(mySubMenu.thing, GUI_Maker.wx.Menu)

					with mySubMenu.addItem() as myMenuItem:
						self.assertEqual(myMenuItem.type, GUI_Maker.Types.menuitem)
						self.assertIsInstance(myMenuItem.thing, GUI_Maker.wx.MenuItem)

			with myFrame.addSizerBox() as mySizer:
				with mySizer.addToolBar() as myToolbar:
					self.assertEqual(myToolbar.type, GUI_Maker.Types.toolbar)
					self.assertIsInstance(myToolbar.thing, GUI_Maker.wx.ToolBar)

					with myToolbar.addItem() as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, "normal")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addItem(check = True) as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, "check")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addItem(check = False) as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, "radio")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addStretchableSpace() as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, "stretchable")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addSeparator() as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, "separator")
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)

					with myToolbar.addText() as myToolbarItem:
						self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
						self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.text)
						self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
						self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticText)

	# 				with myToolbar.addHyperlink() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.hyperlink)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.HyperlinkCtrl)

	# 				with myToolbar.addLine() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.line)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticLine)

	# 				with myToolbar.addProgressBar() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.progressbar)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Gauge)

	# 				with myToolbar.addListDrop() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.listdrop)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Choice)

	# 				with myToolbar.addListFull() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.listfull)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ListCtrl)

	# 				with myToolbar.addListTree() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.listtree)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.TreeCtrl)

	# 				with myToolbar.addInputSlider() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.slider)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Slider)

	# 				with myToolbar.addInputBox() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.inputbox)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.TextCtrl)

	# 				with myToolbar.addInputSearch() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.inputsearch)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.SearchCtrl)

	# 				with myToolbar.addInputSpinner() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.inputspinner)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.SpinCtrl)

	# 				with myToolbar.addButton() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.button)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.Button)

	# 				with myToolbar.addButtonToggle() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.buttontoggle)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ToggleButton)

	# 				with myToolbar.addButtonCheck() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.buttoncheck)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.CheckBox)

	# 				with myToolbar.addButtonCheckList() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.checklist)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.CheckListBox)

	# 				with myToolbar.addButtonRadio() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.buttonradio)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.RadioButton)

	# 				with myToolbar.addButtonRadioBox() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.buttonradiobox)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.RadioBox)

	# 				# with myToolbar.addButtonHelp() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 				# 	self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.")	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 				# 	self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.)

	# 				with myToolbar.addButtonImage() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.buttonimage)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.lib.buttons.GenBitmapButton)

	# 				with myToolbar.addImage() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.image)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.StaticBitmap)

	# 				with myToolbar.addPickerColor() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickercolor)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.ColourPickerCtrl)

	# 				with myToolbar.addPickerFont() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickerfont)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.FontPickerCtrl)

	# 				with myToolbar.addPickerFile() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickerfile)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.FilePickerCtrl)

	# 				with myToolbar.addPickerFileWindow() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickerfilewindow)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.GenericDirCtrl)

	# 				with myToolbar.addPickerDate() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickerdate)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.DatePickerCtrl)

	# 				with myToolbar.addPickerDateWindow() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickerdatewindow)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.CalendarCtrl)

	# 				with myToolbar.addPickerTime() as myToolbarItem:
	# 					self.assertEqual(myToolbarItem.type, GUI_Maker.Types.toolbaritem)
	# 					self.assertEqual(myToolbarItem.subType, GUI_Maker.Types.pickertime)
	# 					self.assertIsInstance(myToolbarItem.thing, GUI_Maker.wx.ToolBarToolBase)
	# 					self.assertIsInstance(myToolbarItem.subHandle.thing, GUI_Maker.wx.adv.TimePickerCtrl)

	# Menu Popup
	# Status Bar

	def test_dialogs(self):
		pass

		#Custom dialog
		#status bar
					

if __name__ == '__main__':
	unittest.main()