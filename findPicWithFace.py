#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   findPicWithFace.py    
# @Modify Time: 2020/5/22 15:30       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:找出所有带人脸的图片 保存在新的文件夹中
import os
import shutil
import numpy as np
from PIL import Image

import cv2


def img_resize(image, height=700):
    h, w = image.shape[:2]
    pro = height / h
    size = (int(w * pro), int(height))
    img = cv2.resize(image, size)
    return img


def show(img, key):
    cv2.imshow("img", img)
    cv2.waitKey(key)


def detect_face(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
    img = img_resize(img)
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    front_face_detected = frontFaceClassifier.detectMultiScale(img_grey, scaleFactor=1.2,
                                                               minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)
    if len(front_face_detected) != 0:
        for (x, y, w, h) in front_face_detected:
            print(w, h)
            print(path)
            print(img.shape)
            print("=====================")
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        show(img, 5)


def save_with_face(path):
    for i in os.listdir(path):
        tmp_path = os.path.join(path, i)
        for pic in os.listdir(tmp_path):
            pic_path = os.path.join(tmp_path, pic)
            if (pic.endswith("png") | pic.endswith("jpg") |
                    pic.endswith("bmp") | pic.endswith("tif") |
                    pic.endswith("PNG") | pic.endswith("JPG") |
                    pic.endswith("BMP") | pic.endswith("TIF")):
                detect_face(pic_path)


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

            if not os.path.exists(id_path):
                os.makedirs(id_path)
            if not os.path.exists(graduation_path):
                os.makedirs(graduation_path)
            if not os.path.exists(degree_path):
                os.makedirs(degree_path)
            if not os.path.exists(contract_path):
                os.makedirs(contract_path)

            # 寻找图片名称是否含有关键字   -1 -> 不含有
            if filename.find('身份证') != -1:
                shutil.copy(tmp_path, id_path + "/" + filename)
            elif filename.find('毕业证') != -1:
                shutil.copy(tmp_path, graduation_path + "/" + filename)
            elif filename.find('学位证') != -1:
                shutil.copy(tmp_path, degree_path + "/" + filename)
            elif filename.find('合同') != -1:
                shutil.copy(tmp_path, contract_path + "/" + filename)
            else:
                shutil.copy(tmp_path, unnamed_file_path + "/" + filename)


if __name__ == '__main__':
    frontalfaceXML = "haarcascade_frontalface_default.xml"
    eyeXML = "haarcascade_eye.xml"
    frontFaceClassifier = cv2.CascadeClassifier(frontalfaceXML)
    eyeClassifier = cv2.CascadeClassifier(eyeXML)

    base_path = "E:/KingT/staff/员工档案"
    simple_path = 'E:/KingT/staff/没有子文件夹的文件夹'
    num = 0
    scan_all_pic(base_path)
    # save_with_face(simple_path)
    print(num)
