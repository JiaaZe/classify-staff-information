#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   findPicWithFace.py    
# @Modify Time: 2020/5/22 15:30       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:找出所有带人脸的图片 保存在新的文件夹中
import os
import shutil

import math
import numpy as np
import utils

import cv2


def detect_face(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    img = utils.img_resize(img)
    height, width = img.shape[0:2]
    print(height, width)
    print("========== detect face ===========")
    for i in range(3):
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        front_face_detected = frontFaceClassifier.detectMultiScale(img_grey, scaleFactor=1.2,
                                                                   minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)

        if len(front_face_detected) != 0:
            print(path)
            print("rotate " + str(i) + " times")
            print(img.shape)
            for x, y, w, h in front_face_detected:
                print(x, y, w, h)
            #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            # show(img, 0)
            if i != 0:
                cv2.imencode('.jpg', img)[1].tofile(path)
            return True
        else:
            img = utils.rotate_image(img, 90)
    return False


# 保存带有人脸的图片
def save_with_face(path):
    for i in os.listdir(path):
        tmp_path = os.path.join(path, i)
        for pic in os.listdir(tmp_path):
            pic_path = os.path.join(tmp_path, pic)
            if (pic.endswith("png") | pic.endswith("jpg") |
                    pic.endswith("bmp") | pic.endswith("tif") |
                    pic.endswith("PNG") | pic.endswith("JPG") |
                    pic.endswith("BMP") | pic.endswith("TIF")):
                if detect_face(pic_path):
                    face_path = os.path.join(save_path, i)
                    if not os.path.exists(face_path):
                        os.makedirs(face_path)
                    print("复制到：" + os.path.join(face_path, pic))
                    shutil.copy(pic_path, os.path.join(face_path, pic))


def scan_all_pic(path):
    for f in os.listdir(path):
        tmp_path = os.path.join(path, f)
        if os.path.isdir(tmp_path):
            scan_all_pic(tmp_path)
        else:
            print(tmp_path)
            # name 员工姓名
            # filename 图片名称
            name = str(tmp_path.split("\\")[1])
            filename = str(tmp_path.split("\\")[-1])
            # 无命名的图片
            unnamed_file_path = 'E:/KingT/staff/没有子文件夹的文件夹/' + name
            if not os.path.exists(unnamed_file_path):
                os.makedirs(unnamed_file_path)
            # 根据图片命名放入对应文件夹

            id_path = 'E:/KingT/staff/result/身份证/' + name
            graduation_path = 'E:/KingT/staff/result/毕业证/' + name
            degree_path = 'E:/KingT/staff/result/学位证/' + name
            contract_path = 'E:/KingT/staff/result/劳动合同/' + name
            certification_path = 'E:/KingT/staff/result/其他证书/' + name
            studentCard_path = 'E:/KingT/staff/result/学生证&就业协议/' + name

            if not os.path.exists(id_path):
                os.makedirs(id_path)
            if not os.path.exists(graduation_path):
                os.makedirs(graduation_path)
            if not os.path.exists(degree_path):
                os.makedirs(degree_path)
            if not os.path.exists(contract_path):
                os.makedirs(contract_path)
            if not os.path.exists(certification_path):
                os.makedirs(certification_path)
            if not os.path.exists(studentCard_path):
                os.makedirs(studentCard_path)

            # 寻找路径中是否含有关键字   -1 -> 不含有
            if tmp_path.find('身份证') != -1:
                shutil.copy(tmp_path, id_path + "/" + filename)
            elif tmp_path.find('毕业证') != -1:
                shutil.copy(tmp_path, graduation_path + "/" + filename)
            elif tmp_path.find('学位证') != -1:
                shutil.copy(tmp_path, degree_path + "/" + filename)
            elif tmp_path.find('合同') != -1:
                shutil.copy(tmp_path, contract_path + "/" + filename)
            elif (tmp_path.find('级') != -1) | (tmp_path.find('证书') != -1) | (tmp_path.find('师') != -1):
                shutil.copy(tmp_path, certification_path + "/" + filename)
            elif (tmp_path.find('学生证') != -1) | (tmp_path.find('就业协议') != -1):
                shutil.copy(tmp_path, studentCard_path + "/" + filename)
            else:
                shutil.copy(tmp_path, unnamed_file_path + "/" + filename)


if __name__ == '__main__':
    frontalfaceXML = "haarcascade_frontalface_default.xml"
    eyeXML = "haarcascade_eye.xml"
    frontFaceClassifier = cv2.CascadeClassifier(frontalfaceXML)
    eyeClassifier = cv2.CascadeClassifier(eyeXML)

    base_path = "E:/KingT/staff/员工档案"
    simple_path = 'E:/KingT/staff/没有子文件夹的文件夹'
    save_path = "E:/KingT/staff/facePic"
    num = 0
    # 遍历所有图片
    # scan_all_pic(base_path)
    # 找到带有人脸的图片
    # save_with_face(simple_path)
