'''
Created on 2017. 9. 13.

@author: 이세희
'''
from keras.callbacks import EarlyStopping
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Dropout
from keras.models import Sequential
from keras.optimizers import Adam

import numpy as np
import Graduation_work.usingKeras.loadData as ld

src = 'Graduation_work/made_images/'
if __name__ == '__main__':
    np.random.seed(10)
    test_count = 100
    batch_size = 10
    class_number = 4
    target_size = (150, 150)
    epochs, steps_per_epoch = 50, 2000
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(target_size[0], target_size[1], 3)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Flatten())
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(class_number, activation='softmax'))
    
    train_generator = ld.getTrain_Generator(src+'train', batch_size)
    test_generator = ld.getTest_Generator(src+'test', batch_size)
    model.compile(loss='categorical_crossentropy', 
                  optimizer=Adam(lr=0.0001, decay=1e-6),
                  metrics=['accuracy'])
    model.fit_generator(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs = epochs,
        validation_data=test_generator,
        validation_steps=test_count//batch_size,
        callbacks=[EarlyStopping(min_delta=0.001, patience=10)])
    print('-- Evaluate --')
    scores = model.evaluate_generator(test_generator, steps=10)
    print("{}: {}%".format(model.metrics_names[1], scores[1]*100))
    model.save('Graduation_work/models/4_classes_building_image.h5')
    print("model saved at models/4_classes_building_image.h5")
    