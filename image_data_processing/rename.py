import os

base_dir = "./Graduation_work/images"
D_base_dir = 'D:/ML_images'

#파일 이름이 겹치지 않게 (_크롤링포털)을 붙여서 이름을 바꾸어줌
def renaming(base_dir):
    dir_list = os.listdir(base_dir)
    print(dir_list)
    for dir in dir_list:
        # print(dir.split('_'))
        if len(dir.split('_')) < 2:
            continue
        tag = dir.split('_')[1]
        for filename in os.listdir(base_dir + '/' + dir):
            if ('_google' in filename) or ('_baidu' in filename) or ('_bing' in filename):
                continue
            now_dir = base_dir + '/' + dir
            new_name = filename[:6] + '_' + tag + filename[6:]
            os.rename(now_dir + '/' + filename, now_dir + '/' + new_name)


if __name__ == '__main__':
    renaming(D_base_dir)
