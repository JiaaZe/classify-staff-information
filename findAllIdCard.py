#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   findAllIdCard.py    
# @Modify Time: 2020/5/27 8:47       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:根据result中身份证文件为空的文件夹中找身份证


# 把从 “没有子文件夹的文件夹”中识别到的身份证放到一个文件夹“leftIdCard”中
# input_path 是result中的身份证文件夹
import os
import shutil

import pytesseract

import editExcel
import utils
import cv2
import numpy as np


# 识别图片信息，根据识别到的文字，判断是那种类型的图片
def recognize_information(path, config):
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    image = utils.img_resize(image, )
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
            # cv2.imencode('.jpg', image)[1].tofile(path)
            # utils.show(img, 1)
            return 1
        elif (text.find("人 力") != -1) | (text.find("资 源") != -1) | (text.find("人 事") != -1) \
                | (text.find("工 作") != -1) | (text.find("甲 方") != -1) | (text.find("劳 动") != -1) \
                | (text.find("双 方") != -1) | (text.find("符 合") != -1) | (text.find("知 识") != -1):
            return 5
        elif (text.find("成 人") != -1) | (text.find("高 等") != -1) | (text.find("毕 业") != -1) \
                | (text.find("合 格") != -1) | (text.find("半 业") != -1) | (text.find("课 程") != -1) \
                | (text.find("单 业") != -1) | (text.find("毗 业") != -1) | (text.find("注 册") != -1):
            print("=====毕业证=====")
            # cv2.imencode('.jpg', image)[1].tofile(path)
            # utils.show(img, 1)
            return 2
        elif text.find("合 同") != -1:
            return 4
        elif (text.find("居 民") != -1) | (text.find("公 民") != -1) | (text.find("民 身") != -1) \
                | (text.find("份 证") != -1) | (text.find("身 休") != -1) | (text.find("休 证") != -1):
            print("=====身份证=====")
            cv2.imencode('.jpg', image)[1].tofile(path)
            utils.show(img, 1)
            return 3
        else:
            image = utils.rotate_image(image, 90)
            utils.show(img, 1)

    print("=====----=====")
    return -1


def id_card_to_one_folder(input_path):
    output_folder = "E:/KingT/staff/leftIdCard/"
    idcard_list = []
    for f in os.listdir(input_path):
        folder_path = os.path.join(input_path, f)
        lens = len(os.listdir(folder_path))
        if lens == 0:
            name = folder_path.split("\\")[1][5:]
            data = [name, "缺"]
            idcard_list.append(data)
    print(idcard_list)
    editExcel.update_excel(idcard_list, 2)
    editExcel.update_excel(idcard_list, 3)
    # if len(os.listdir(folder_path)) == 0:
    #     if f.startswith("JT"):
    #         name = f[5:]
    #     elif f.startswith("！！"):
    #         name = f[2:]
    #     elif f.startswith("实习生"):
    #         name = f[3:]
    #     else:
    #         name = f
    #
    #     scan_folder = os.path.join("E:/KingT/staff/没有子文件夹的文件夹", f)
    #     for pic in os.listdir(scan_folder):
    #         countC = 0
    #         if pic.endswith("jpg") | pic.endswith("tif"):
    #             pic_path = os.path.join(scan_folder, pic)
    #             for i in range(3, 4):
    #                 flag = recognize_information(pic_path, i)
    #                 if flag == 3:
    #                     if countC == 0:
    #                         save_path = output_folder + str(i) + "=" + name + "_身份证." + pic[-3:]
    #                     else:
    #                         save_path = output_folder + str(i) + "=" + name + "_身份证(" + str(countC) + ")." + pic[
    #                                                                                                          -3:]
    #                     countC = countC + 1
    #                     print("save path: " + save_path)
    #                     shutil.copy(pic_path, save_path)
    #                 elif flag != -1:
    #                     break

# id_card_to_one_folder("E:/KingT/staff/result/身份证")
