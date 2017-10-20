'''
Created on 2017. 9. 13.

@author: 이세희
'''
from keras.preprocessing.image import ImageDataGenerator

size = 150

def getTrain_Generator(path, batchsize=5):
    
    train_datagen = ImageDataGenerator(rescale=1./255)
    train_generator = train_datagen.flow_from_directory(
        path, 
        target_size=(size, size), 
        batch_size=batchsize,
        class_mode='categorical',
        shuffle=True)
    
    return train_generator

def getTest_Generator(path, batchsize=5):
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
            path, 
            target_size=(size, size), 
            batch_size=batchsize,
            class_mode='categorical',
            shuffle=True)
    # for f in test_generator.filenames:
    #     print(f)
    return test_generator

if __name__ == '__main__':
    getTrain_Generator('../images/buildings/train')
    getTest_Generator('../images/buildings/test')
    