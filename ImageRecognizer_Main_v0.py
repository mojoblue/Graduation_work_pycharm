import GUI.makeGUI as GUI
import sys
import os

app = GUI.QApplication(sys.argv)
dialog = GUI.Dialog()
dialog.setModelPath(os.getcwd()+"/models/4_classes_building_image.h5")
dialog.loadModel()
default_image = os.getcwd() + '/GUI/default.jpg'
sampleImgPath = os.getcwd() + '/GUI/sampleImg.jpg'
sampleImgSize = (300, 300)
dialog.makeForm(default_image, sampleImgSize, sampleImgPath)
sys.exit(dialog.exec_())
