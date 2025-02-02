'''
Created on 2017. 9. 13.

@author: 이세희
'''

import usingKeras.loadData as ld
import numpy as np
from keras.models import load_model
from PIL import Image

tag = {0:'개선문', 1: '빅 벤', 2: '브란덴부르크 문', 3: '에펠탑'}

def loadKerasModel(modelPath):
    model = load_model(modelPath)
    print('Model Loading Finished!')
    return model

def recognizeImage(model, imgPath):
    im = Image.open(imgPath)
    im.load()
    inputImg = np.asarray(im, dtype='int32')
    inputImg = inputImg.reshape((1, ) +inputImg.shape)
    pred = model.predict_classes(inputImg)
    return tag[pred[0]]
    # print(x_hat.shape)



if __name__ == '__main__':
#     model = load_model
#     train_generator = ld.getTrain_Generator('../images/buildings/train', 2)
    test_generator = ld.getTest_Generator('Graduation_work/made_images/test/', 50)
    #Image generator의 batch_size를 가져옴
    batch_size = test_generator.batch_size
    #Image generator에 있는 모든 image 파일의 수 : n
    n = test_generator.n
    model = load_model('Graduation_work/models/4_classes_building_image.h5')
    
    for i in range(0, int(n/batch_size)):
        x, y = test_generator.next()
        for x_hat, y_hat in zip(x, y):
            # image를 판독하여 출력
            # x_hat의 Dimension을 맞추어줌
            x_hat = x_hat.reshape((1,) + x_hat.shape)

            pred = model.predict_classes(x_hat)
            print('answer : {}, predict : {}'.format(tag[np.argmax(y_hat)], tag[pred[0]]))
            # print('answer : {}, predict : {}'.format((y_hat), (pred)))