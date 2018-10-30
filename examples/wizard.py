import os
import sys
import time
if (__name__ == "__main__"):
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) #Allows to import from the parent directory

import GUI_Maker

#Create GUI object
gui = GUI_Maker.build()

#Bound Functions
def onShow(event):

	myWizard = gui[1]
	myWizard.start()

	event.Skip()

def onWizard_pageChange(event):
	print("Wizard Page Changed", event.node.handle.__repr__())

	event.Skip()

def onWizard_cancel(event):
	print("Wizard Canceled")

	event.Skip()

flag = False
def onWizard_finish(event):
	global flag
	print("Wizard Finished")

	if (not flag):
		print("Try Again")
		flag = True
		event.Veto()
		return

	event.Skip()

#Construction Functions
def buildWindow():
	"""Creates a simple window."""

	with gui.addWindow(label = 0, title = "Wizard Example") as myFrame:
		with myFrame.addSizerBox() as mySizer:
			mySizer.addButton("Launch Wizard", myFunction = onShow)

	with gui.addWizard(label = 1, title = "My Wizard") as myWizard:
		myWizard.setFunction_pageChange(onWizard_pageChange)
		myWizard.setFunction_cancel(onWizard_cancel)
		myWizard.setFunction_finish(onWizard_finish)
		# myWizard.setWindowSize((500, 300))

		with myWizard.addPage(label = "main", default = True) as myWizardPage:
			myWizardPage.addText(text = "Which Way?")

			with myWizardPage.addPage(text = "North", label = "north") as firstChoice:
				firstChoice.addText(text = "You find a river")

				with firstChoice.addPage(text = "Make Camp", default = True) as secondChoice:
					secondChoice.addText(text = "Good night")

				with firstChoice.addPage(text = "Go Fishing") as secondChoice:
					secondChoice.addText(text = "Fun!")

					with secondChoice.addPage(text = "Make Camp") as thirdChoice:
						thirdChoice.addText(text = "Good night")

			with myWizardPage.addPage(text = "East", label = "east", default = True) as firstChoice:
				firstChoice.addText(text = "You come to a dead end")

			with myWizardPage.addPage(text = "South", label = "south") as firstChoice:
				firstChoice.addText(text = "You find a town")

				with firstChoice.addPage(text = "Sleep", default = True) as secondChoice:
					secondChoice.addText(text = "Good night")

				with firstChoice.addPage(text = "Eat") as secondChoice:
					secondChoice.addText(text = "Yum!")

					with secondChoice.addPage(text = "Sleep") as thirdChoice:
						thirdChoice.addText(text = "Good night")

		with myWizard.addPage(label = "secret") as myWizardPage:
			myWizardPage.addText(text = "Secret Room")

		# import anytree
		# print(anytree.RenderTree(myWizard.pageNode))

		# sys.exit()

#Run Program
if __name__ == '__main__':
	buildWindow()
	gui.centerWindowAll()

	myFrame = gui.getWindow(0)
	myFrame.showWindow()

	gui.finish()