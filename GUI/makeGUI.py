import os
import sys

from PIL import Image
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog, QLabel
from PyQt5.QtWidgets import (QDialog,
                             QVBoxLayout)


class Dialog(QDialog):

    def __init__(self):
        super(Dialog, self).__init__()
        default_image  = os.getcwd() + '/default.jpg'
        self.sampleImgPath = './sampleImg.jpg'
        self.sampleImgSize = (300, 300)

        self.resizeImg(default_image, self.sampleImgSize, self.sampleImgPath)
        self.label = QLabel(self)
        self.pixmap = QPixmap('./sampleImg.jpg')
        self.label.setPixmap(self.pixmap)

        loadButton = QPushButton("Load Image")
        recogButton = QPushButton("Recognize")
        loadButton.clicked.connect(self.on_click)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(loadButton)
        self.mainLayout.addWidget(recogButton)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("이미지 인식기")

    def resizeImg(self, imgPath, size, savePath):
        im = Image.open(imgPath)
        im = im.resize(size)
        im.save(savePath)

    # 불러온 이미지를 프로그램에서 보여주기 위한 함수
    def reLoadDialog(self):
        self.pixmap = QPixmap('./sampleImg.jpg')
        self.label.setPixmap(self.pixmap)


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "All Files (*);;JPG Image Files (*.jpg);;PNG Image Files (*.png);;GIF Image Files (*.gif)",
                                                      options=options)
        if fileName:
            self.resizeImg(fileName, self.sampleImgSize, self.sampleImgPath)
            pixmap = QPixmap(self.sampleImgPath)
            self.reLoadDialog()

        # 버튼 클릭시
    @pyqtSlot()
    def on_click(self):
        self.openFileNameDialog()

    @pyqtSlot()
    def on_click_recognition(self):
        print('recognize')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())