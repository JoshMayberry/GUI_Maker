import wx
 
########################################################################
class RandomPanel(wx.Panel):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self, parent, color):
		"""Constructor"""
		wx.Panel.__init__(self, parent)
		self.SetBackgroundColour(color)
 
########################################################################
class MainPanel(wx.Panel):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self, parent):
		"""Constructor"""
		wx.Panel.__init__(self, parent)
		topSplitter = wx.SplitterWindow(self)





		splitter_1 = wx.SplitterWindow(topSplitter)
		splitter_1.SplitVertically(RandomPanel(splitter_1, "blue"), RandomPanel(splitter_1, "red"))
		splitter_1.SetSashGravity(0.5)

		splitter_2 = wx.SplitterWindow(splitter_1)
		splitter_2.SplitVertically(splitter_1, RandomPanel(splitter_2, "red"))
		splitter_2.SetSashGravity(0.5)
 





		topSplitter.SplitHorizontally(splitter_2, RandomPanel(topSplitter, "green"))
		topSplitter.SetSashGravity(0.5)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(topSplitter, 1, wx.EXPAND)
		self.SetSizer(sizer)
 
########################################################################
class MainFrame(wx.Frame):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, title="Nested Splitters",
						  size=(800,600))
		panel = MainPanel(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = MainFrame()
	app.MainLoop()