import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

printData = None
# printData = {'bin': 'source', 'color': True, 'duplex': None, 'file': '', 'vertical': True, 'paperId': 'Letter; 8 1/2 by 11 in', 'paperSize': (215, 279), 'printMode': 'Send to printer', 'printerName': 'PDFCreator', 'quality': 600, 'marginMinimum': True, 'marginLeft': 0, 'marginTop': 0, 'marginRight': 0, 'marginBottom': 0, 'marginLeftMinimum': 0, 'marginTopMinimum': 0, 'marginRightMinimum': 0, 'marginBottomMinimum': 0}

def onPrintText(event):
	global printData
	
	with gui[0].makeDialogPrintPreview(printData = printData, printOverride = {"paperId": "Letter; 8 1/2 by 11 in", 'vertical': True}) as myDialog:
		myDialog.setValue("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam id magna ut lorem euismod iaculis. Nullam pellentesque, mauris eu gravida egestas, lacus ipsum posuere mi, in consectetur eros orci hendrerit purus. Maecenas finibus sed mi semper volutpat. Mauris vel eros nunc. Phasellus efficitur nunc non diam venenatis, sed tempor leo efficitur. Vivamus varius vulputate tellus ut congue. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Aliquam gravida faucibus gravida. Cras sed sem sed libero varius commodo. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent sollicitudin faucibus quam at facilisis. Nullam non turpis lobortis, sodales ligula non, finibus nisl. Proin fringilla scelerisque odio, id dignissim libero ullamcorper id. Morbi vehicula orci odio. Nunc leo enim, eleifend a ultrices vel, malesuada quis felis.
			
			Etiam non consectetur nulla. Suspendisse vehicula vitae erat quis vulputate. Phasellus rutrum massa sed nisi iaculis luctus. Etiam sit amet mi et lacus tristique feugiat. In mollis nisl non volutpat egestas. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sollicitudin sollicitudin semper.
			
			Fusce eu dolor sed nisl rhoncus feugiat. Vivamus id pulvinar lorem. Nulla sit amet laoreet mi. Ut ipsum libero, vehicula vel lobortis eget, iaculis sed mi. Nunc dolor velit, pretium ut libero a, vehicula ullamcorper quam. Phasellus dapibus, est sed fermentum hendrerit, mauris diam cursus diam, sed tincidunt erat neque a ante. Cras pellentesque semper orci eu ultricies. Mauris eu egestas neque. Aenean non arcu arcu.""")
		myDialog.send()

	event.Skip()

def onPrintLabel(event, testPrint = False, debugging = False):
	global printData

	import API_Com as Com
	communication = Com.build()
	barcodeHandle = communication.barcode[0]
	
	with gui[0].makeDialogPrintPreview(printData = printData, printOverride = {"paperId": "Letter; 8 1/2 by 11 in", #'paperSize': (4.25, 6.75),
		'vertical': True, 'marginLeft': 0, 'marginTop': 0, 'marginRight': 0, 'marginBottom': 0}, size = (500, 500)) as myDialog:

		bounds = (0, 10, 270, 455)
		with myDialog.makeCanvas() as myCanvas:
			if (testPrint):
				myCanvas.drawText("Center this Box\non the Label", size = 24, wrap = bounds, align = bounds, x_align = "center", y_align = "center")
				myCanvas.drawRectangle(*bounds)
			else:
				if (debugging):
					myCanvas.drawRectangle(*bounds)

				#Constants
				size_text = 18
				size_title = 0
				padding_text = 12
				padding_logo_x = 5
				padding_logo_y = 10
				padding_title = 10
				line_title = size_title + padding_title
				line_text = size_text + padding_text
				
				size_barcode = [(bounds[2] - bounds[0]) // 2] * 2
				size_logo = [size_barcode[0] - padding_logo_x * 2, (bounds[2] - bounds[0]) // 2 - line_title - padding_logo_y]

				#Draw Barcode
				barcode = barcodeHandle.create("Lorem ipsum dolor sit amet, consectetur adipiscing elit", "qr", borderSize = 0)
				myCanvas.drawImage(barcode, x = bounds[2] - size_barcode[0], y = bounds[1], scale = size_barcode)
				# myCanvas.drawImage("logo.bmp", x = bounds[0] + line_title, y = bounds[1] + padding_logo_x, scale = size_logo, rotate = 90)

				#Draw Text
				# myCanvas.drawText("Test Barcode", 			x = bounds[0], y = bounds[1], size = size_title, align = bounds, y_align = "c", angle = 90)

				myCanvas.drawText("Job #: Lorem", 			x = bounds[0] + line_text * 0 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("ID #: Ipsum", 			x = bounds[0] + line_text * 1 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("Material: Dolor", 		x = bounds[0] + line_text * 2 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("Color: Sit", 			x = bounds[0] + line_text * 3 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("Type: Amet", 			x = bounds[0] + line_text * 4 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("Contact: Consectetur", 	x = bounds[0] + line_text * 5 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)
				myCanvas.drawText("Customer: Adipiscing", 	x = bounds[0] + line_text * 6 + line_title, y_offset = -10, y = bounds[1], size = size_text, align = bounds, y_align = "b", angle = 90)

		myDialog.setValue(myCanvas)
		myDialog.send()

	event.Skip()

def onSetupPrinter(event):
	global printData

	with myFrame.makeDialogPrint(printData = printData) as myDialog:
		if (myDialog.isCancel()):
			return
		printData = myDialog.getValue()

	event.Skip()

def onSetupPaper(event):
	global printData

	with myFrame.makeDialogPrintSetup(printData = printData) as myDialog:
		if (myDialog.isCancel()):
			return
		printData = myDialog.getValue()

		print(printData)

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	#Initialize Frame
	with gui.addWindow(label = 0, title = "Print Preview Example") as myFrame:
		myFrame.setWindowSize((450, 200))
		
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton(text = "Setup Printer", myFunction = onSetupPrinter)
			mySizer.addButton(text = "Setup Paper", myFunction = onSetupPaper)
			mySizer.addButton(text = "Print Test", myFunction = onPrintText)
			mySizer.addButton(text = "Print Label", myFunction = onPrintLabel)

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()