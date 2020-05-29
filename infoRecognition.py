#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   infoRecognition.py    
# @Modify Time: 2020/5/25 8:19       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:识别未命名的图片，透过识别出来的关键字判断属于哪种类型 身份证 学位证 毕业证，剩余的手动修改

import shutil

import pytesseract
import cv2
import numpy as np
import utils
import os


def recognize_all_image(path):
    for i in os.listdir(path):
        if i.startswith("JT"):
            name = i[5:]
        elif i.startswith("！！"):
            name = i[2:]
        elif i.startswith("实习生"):
            name = i[3:]
        else:
            name = i

        countA = 0
        countB = 0
        countC = 0
        countD = 0
        tmp_path = os.path.join(path, i)
        for pic in os.listdir(tmp_path):
            pic_path = os.path.join(tmp_path, pic)
            flag = recognize_information(pic_path, 1)
            if flag == 1:
                if countA == 0:
                    save_path = 'E:/KingT/staff/test/学位证/' + name + "_学位证.jpg"
                else:
                    save_path = 'E:/KingT/staff/test/学位证/' + name + "_学位证(" + str(countA) + ").jpg"
                countA = countA + 1
                print("save path: " + save_path)
                shutil.copy(pic_path, save_path)

            elif flag == 2:
                if countB == 0:
                    save_path = 'E:/KingT/staff/test/毕业证/' + name + "_毕业证.jpg"
                else:
                    save_path = 'E:/KingT/staff/test/毕业证/' + name + "_毕业证(" + str(countB) + ").jpg"
                countB = countB + 1
                print("save path: " + save_path)
                shutil.copy(pic_path, save_path)

            elif flag == 3:
                if countC == 0:
                    save_path = 'E:/KingT/staff/test/身份证/' + name + "_身份证.jpg"
                else:
                    save_path = 'E:/KingT/staff/test/身份证/' + name + "_身份证(" + str(countC) + ").jpg"
                countC = countC + 1
                print("save path: " + save_path)
                shutil.copy(pic_path, save_path)

            elif flag == 4:
                if countD == 0:
                    save_path = 'E:/KingT/staff/test/nothing/' + name + "_nothing.jpg"
                else:
                    save_path = 'E:/KingT/staff/test/nothing/' + name + "_nothing(" + str(countD) + ").jpg"
                countD = countD + 1
                print("save path: " + save_path)
                shutil.copy(pic_path, save_path)


def recognize_nothing_img(path):
    countD = 0
    countC = 0
    for pic in os.listdir(path):
        name = pic.split("_")[0]
        pic_path = os.path.join(path, pic)
        flag = recognize_information(pic_path, 3)
        if flag == 1:
            save_path = 'E:/KingT/staff/test/学位证/' + name + "_学位证.jpg"
            print("save path: " + save_path)
            shutil.copy(pic_path, save_path)

        elif flag == 2:
            save_path = 'E:/KingT/staff/test/毕业证/' + name + "_毕业证.jpg"
            print("save path: " + save_path)
            shutil.copy(pic_path, save_path)

        elif flag == 3:
            if countC == 0:
                save_path = 'E:/KingT/staff/test/身份证/' + name + "_身份证.jpg"
            else:
                save_path = 'E:/KingT/staff/test/身份证/' + name + "_身份证(" + str(countC) + ").jpg"
                countC = 0
            print("save path: " + save_path)
            shutil.copy(pic_path, save_path)

        elif flag == 4:
            if countD == 0:
                save_path = 'E:/KingT/staff/test/nothing3/' + name + "_nothing.jpg"
            else:
                save_path = 'E:/KingT/staff/test/nothing3/' + name + "_nothing(" + str(countD) + ").jpg"
            countD = countD + 1
            print("save path: " + save_path)
            shutil.copy(pic_path, save_path)


def recognize_information(path, config):
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    image = utils.img_resize(image)
    print("\n-----------------------------------")
    print(path)
    print(image.shape)
    for i in range(3):
        print("+++" + str(i) + "+++")
        if config == 1:
            imagegray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            retval, img = cv2.threshold(imagegray, 120, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        elif config == 2:
            img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif config == 3:
            img = image
        utils.show(img, 1)
        text = pytesseract.image_to_string(img, lang='chi_sim')
        print(text)
        if (text.find("学 位") != -1) | (text.find("学 士") != -1):
            print("=====学位证=====")
            cv2.imencode('.jpg', image)[1].tofile(path)
            utils.show(img, 1)
            return 1
        elif (text.find("成 人") != -1) | (text.find("高 等") != -1) | (text.find("毕 业") != -1) \
                | (text.find("合 格") != -1) | (text.find("半 业") != -1) | (text.find("课 程") != -1) \
                | (text.find("单 业") != -1) | (text.find("毗 业") != -1) | (text.find("注 册") != -1):
            print("=====毕业证=====")
            cv2.imencode('.jpg', image)[1].tofile(path)
            utils.show(img, 1)
            return 2
        if text.find("合 同") != -1:
            return 4
        elif (text.find("居 民") != -1) | (text.find("公 民") != -1) | (text.find("民 身") != -1) \
                | (text.find("份 证") != 1) | (text.find("身 休") != -1) | (text.find("休 证") != -1):
            print("=====身份证=====")
            cv2.imencode('.jpg', image)[1].tofile(path)
            utils.show(img, 1)
            return 3
        else:
            image = utils.rotate_image(image, 90)
            utils.show(img, 1)
    print("=====----=====")
    return 4


def classify_folder(path, target_path):
    # f: 文件夹名称 身份证 学位证 毕业证
    for f in os.listdir(path):
        if not f.startswith("nothing"):
            folder_path = os.path.join(path, f)
            target_folder_path = os.path.join(target_path, f)
            # 文件夹下的图片名称  人名_类型
            for pic in os.listdir(folder_path):
                name = pic.split("_")[0]
                pic_path = os.path.join(folder_path, pic)
                # target_path: E:/KingT/staff/result/毕业证
                # target_fname = JTxxx小明
                for target_fname in os.listdir(target_folder_path):
                    if target_fname.find(name) != -1:
                        # target_folder: E:/KingT/staff/result/毕业证/JTxxx小明
                        target_folder = os.path.join(target_folder_path, target_fname)
                        result_path = os.path.join(target_folder, str(name) + "-" + f + ".jpg")
                        print(pic_path, result_path)
                        cv2.waitKey(0)
                        shutil.copy(pic_path, result_path)


def classify_spec_folder(path):
    for i in os.listdir(path):
        if i.startswith("JT"):
            name = i[5:0]
        elif i.startswith("！！"):
            name = i[2:]
        elif i.startswith("实习生"):
            name = i[3:]
        else:
            name = i
        folder_path = os.path.join(path, i)
        countC = 0
        for pic in os.listdir(folder_path):
            pic_path = os.path.join(folder_path, pic)
            print(pic_path)
            if pic_path.endswith("jpg"):
                flag = recognize_information(pic_path, 1)
                if flag == 3:
                    if countC == 0:
                        save_path = 'E:/KingT/staff/test/身份证3/' + name + "_身份证.jpg"
                        countC = countC + 1
                    else:
                        save_path = 'E:/KingT/staff/test/身份证3/' + name + "_身份证(" + str(countC) + ").jpg"
                        countC = countC + 1
                    print("save path: " + save_path)
                    shutil.copy(pic_path, save_path)


img_path = 'E:/KingT/staff/facePic'
nothing_path = 'E:/KingT/staff/test/nothing2'
# recognize_all_image(img_path)
# recognize_information(img_path)
# recognize_nothing_img(nothing_path)
# classify_folder('E:/KingT/staff/test', 'E:/KingT/staff/result')
# classify_spec_folder('E:/KingT/staff/没有子文件夹的文件夹')
