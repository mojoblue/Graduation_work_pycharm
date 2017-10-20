import os
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

src = 'Graduation_work/{}'.format('extra_data/')
save_dir = 'Graduation_work/made_images/test/eiffel tower'



if __name__ == '__main__':
    making_value = 5
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.0,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    count = 0
    class_list = ['empty']
    for className in class_list:
        path = src+className
        # print(className)
        for imageName in os.listdir(path):

            imagePath = path+'/'+imageName
            exceptExt = imageName.split(".")[0]
            # print(path)
            img = load_img(imagePath)
            x = img_to_array(img)
            x = x.reshape((1, )+x.shape)
            i = 0
            for batch in datagen.flow(x, batch_size=10, save_to_dir=save_dir,
                                      save_prefix=exceptExt, save_format='jpg'):
                i += 1
                # print(i)
                if i > making_value:
                    break
            count += 1
            print(count)