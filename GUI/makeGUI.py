import os
import sys

from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import usingKeras.loadModel as uk
import TextAbstraction.TextModuleVer2 as textModule
class Dialog(QDialog):

    def __init__(self):
        super(Dialog, self).__init__()
        self.modelPath = self.setModelPath('../models/4_classes_building_image.h5')


    def makeForm(self, default_image, sampleImgSize, sampleImgPath):
        self.default_image, self.sampleImgSize, self.sampleImgPath\
            = default_image, sampleImgSize, sampleImgPath
        self.loadFileName = default_image
        self.resizeImg(default_image, sampleImgSize, sampleImgPath)
        self.label = QLabel(self)
        self.pixmap = QPixmap(sampleImgPath)
        self.label.setPixmap(self.pixmap)

        #Image Load용 버튼
        loadButton = QPushButton("Load Image")
        #Image 인식용 버튼
        recogButton = QPushButton("Recognize")
        #버튼 클릭시 기능을 추가
        loadButton.clicked.connect(self.on_click)
        recogButton.clicked.connect(self.on_click_recognition)
        #레이아웃 생성 및 항목 추가
        layout = QFormLayout()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(loadButton)
        self.mainLayout.addWidget(recogButton)

        #인식결과 출력 label
        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setText("")
        self.text_label.setFixedSize(300, 100)
        self.mainLayout.addWidget(self.text_label)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("이미지 관련 키워드 추출기")

    def setModelPath(self, path):
        self.modelPath = path

    def setSampleImagePath(self, path):
        self.sampleImgPath = path

    # 모델을 불러오는 함수
    def loadModel(self):
        self.model = uk.load_model(self.modelPath)

    def resizeImg(self, imgPath, size, savePath):
        im = Image.open(imgPath)
        im = im.resize(size)
        im.save(savePath)

    # 불러온 이미지를 프로그램에서 보여주기 위한 함수
    def reLoadDialog(self):
        self.pixmap = QPixmap(self.sampleImgPath)
        self.label.setPixmap(self.pixmap)

    # 파일 선택기 함수
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "All Files (*);;JPG Image Files (*.jpg);;PNG Image Files (*.png);;GIF Image Files (*.gif)",
                                                      options=options)
        # print(fileName)
        if fileName:
            self.loadFileName = fileName
            self.resizeImg(fileName, self.sampleImgSize, self.sampleImgPath)
            pixmap = QPixmap(self.sampleImgPath)
            self.reLoadDialog()

        # 버튼 클릭시
    @pyqtSlot()
    def on_click(self):
        self.openFileNameDialog()

    @pyqtSlot()
    def on_click_recognition(self):
        resizedLoadImagePath = './resizedLoadImg.jpg'
        self.resizeImg(self.loadFileName, (150, 150), resizedLoadImagePath)
        pred = uk.recognizeImage(self.model, resizedLoadImagePath)
        # keyword_str = "keyword"
        keyword_str = textModule.makeResult(pred)
        # print(keyword_str)
        # self.text_label.setText("인식 결과 : {}".format(pred))
        # print(pred)

        # print(keyword_str)
        self.text_label.setText("키워드 : \n{}".format(keyword_str))


        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.setModelPath('../models/4_classes_building_image.h5')
    dialog.loadModel()
    default_image = os.getcwd() + '/default.jpg'
    sampleImgPath = './sampleImg.jpg'
    sampleImgSize = (300, 300)
    dialog.makeForm(default_image, sampleImgSize, sampleImgPath)
    sys.exit(dialog.exec_())
