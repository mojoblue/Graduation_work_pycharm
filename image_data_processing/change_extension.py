import os

from PIL import Image as image
import shutil

#src : 원본 파일 source 경로
#move_src : 원본 파일 이동시킬 위치
def changeToJPG(src, move_src):
    image_dir = os.listdir(src)
    for dir in image_dir:
        #save_dir : 파일을 저장시킬 위치 및 원본 파일 위치
        #image_list : 원본 파일 위치에서의 파일 이름 리스트
        save_dir = src + '/' + dir
        image_list = os.listdir(save_dir)
        for name in image_list:
            #원본 파일 경로
            filePath = src + '/' + dir + '/' + name
            #이동할 파일 경로
            movePath = move_src + dir.split('_')[0] + '_' + name
            if '.gif' in name:
                #파일을 .jpg 파일로 변경
                convertImg(filePath, '.jpg', save_dir)
                #movePath로 파일을 이동
                shutil.move(filePath, movePath)
            if '.png' in name:
                convertImg(filePath, '.jpg', save_dir)
                shutil.move(filePath, movePath)

def convertImg(filePath, extension, savePath):
    filename = filePath.split('/')[-1].split('.')[0]
    print('source File :', filePath)
    im = image.open(filePath)
    rgb_im = im.convert('RGB')
    rgb_im.save(savePath+'/'+filename+extension)
    # print(filename+extension)
    print('changed File', savePath+'/'+filename+extension)

def copyImage(src, dest):
    print(dest)
    print(src)

# arc de Triomphe 1129
# big ben 1294
if __name__ == '__main__':
    src = 'Graduation_work/images'
    move_src = 'Graduation_work/mv_pngORgif/'
    copy_src = 'Graduation_work/cp_'
    # changeToJPG(src, move_src)
    # for dir in os.listdir(src): #건물 이름 dir
    #     sub_src = src + '/' + dir
    #     for imageName in os.listdir(sub_src):
    #         print(sub_src + '/' + imageName)