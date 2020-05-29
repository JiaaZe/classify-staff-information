#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   copyNullPic.py
# @Modify Time: 2020/5/28 10:45
# @Author: JiaZe
# @Version: 1.0
# @Desciption:
import os
import cv2
import numpy as np
import pytesseract

import editExcel
import utils
from idCardRecognition import getAlignedImage
import shutil


# 检测人脸
def detect_face(img):
    image_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # utils.show(image_grey, 0)
    front_face_detected = frontFaceClassifier.detectMultiScale(image_grey, scaleFactor=1.2,
                                                               minNeighbors=2,
                                                               flags=cv2.CASCADE_SCALE_IMAGE)
    print(len(front_face_detected))
    if len(front_face_detected) != 0:
        for x, y, w, h in front_face_detected:
            print(x, y, w, h)
            # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # utils.show(img, 0)
            if (w < 100) | (y < 100):
                return False, img
            if x < 428:
                img = utils.rotate_image(img, 180)
                print("rotate")
            return True, img
    return False, img


# 调整身份证的正反面 180度旋转
def justify_front_back(path1, path2):
    global nonface_list
    img1 = cv2.imdecode(np.fromfile(path1, dtype=np.uint8), 1)
    img2 = cv2.imdecode(np.fromfile(path2, dtype=np.uint8), 1)
    img1 = cv2.resize(img1, (856, 540), interpolation=cv2.INTER_CUBIC)
    img2 = cv2.resize(img2, (856, 540), interpolation=cv2.INTER_CUBIC)
    print(path1)
    flag1, img1 = detect_face(img1)
    print(path2)
    flag2, img2 = detect_face(img2)

    if not (flag1 | flag2):
        nonface_list.append(path1)
        cv2.imencode('.jpg', img1)[1].tofile(path1)
        cv2.imencode('.jpg', img2)[1].tofile(path2)
        return img1, img2

    elif flag1 & flag2:
        cv2.imencode('.jpg', img1)[1].tofile(path1)
        cv2.imencode('.jpg', img2)[1].tofile(path2)
        return img1, img2

    elif flag1:
        assert not flag2
        f = img2
        b = img1
        if path2.find("front") == -1:
            print("change")
            # path2 是back
            cv2.imencode('.jpg', f)[1].tofile(path1)
            cv2.imencode('.jpg', b)[1].tofile(path2)
        ...
    elif flag2:
        assert not flag1
        f = img1
        b = img2
        if path1.find("front") == -1:
            print("change")
            # path1 是back
            cv2.imencode('.jpg', b)[1].tofile(path1)
            cv2.imencode('.jpg', f)[1].tofile(path2)
    print()
    return f, b
    # return 1, 2


# 处理剩余的图
def deal_rest():
    path = "E:/KingT/staff/result/身份证test"
    in_path = "E:/KingT/staff/result/身份证"
    nolist = []
    for fname in os.listdir(in_path):
        flag = False
        if fname.startswith("JT"):
            employee_name = fname[5:]
        elif fname.startswith("！！"):
            employee_name = fname[2:]
        elif fname.startswith("实习生"):
            employee_name = fname[3:]
        else:
            employee_name = fname

        for pic in os.listdir(path):
            name = pic.split("-")[1]
            if name == employee_name:
                flag = True
                break
        if not flag:
            print(len(os.listdir(os.path.join(in_path, fname))))
            nolist.append(employee_name)
    print(nolist)
    print(len(nolist))


# 调整国徽面的方向
def justify_front(path):
    print(path)
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)

    # for i in range(100, 200):
    #     for j in range(50, 200):
    #         binary_img = utils.getCanny(img, i, j, 15, 0)
    #         print(i, j)
    #         utils.show(binary_img, 1)

    binary_img = utils.getCanny(img, 100, 150, 15, 0)
    # utils.show(binary_img, 0)
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    flag = False
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        area = w * h
        if (area > 20000) & (abs(w - h) < 20):
            if (x > 400) & (y > 270):
                print(path)
                flag = True
            # print(x, y, w, h)
            # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # utils.show(img, 0)

    if flag:
        img = utils.rotate_image(img, 180)
        utils.show(img, 1)
        cv2.imencode('.jpg', img)[1].tofile(path)


# 识别图片文字，返回值： 拼接后的图片 身份证号 到期日
def recognize_concat(front_path, back_path, concat):
    if concat:
        front = cv2.imdecode(np.fromfile(front_path, dtype=np.uint8), 1)
        back = cv2.imdecode(np.fromfile(back_path, dtype=np.uint8), 1)
        front = cv2.resize(front, (856, 540), interpolation=cv2.INTER_CUBIC)
        back = cv2.resize(back, (856, 540), interpolation=cv2.INTER_CUBIC)

        bg = np.ones((1110, 876, 3), dtype=np.uint8) * 255
        bg[10:550, 10:866] = front
        bg[560:1100, 10:866] = back
        output_path = "E:/KingT/staff/result/身份证new/" + front_path.split("_")[0].split("\\")[1] + ".jpg"
        # cv2.imencode('.jpg', bg)[1].tofile(output_path)

    global number_list
    global exp_date_list
    global non_detect_list
    for path in [front_path, back_path]:
        if path == "":
            break
        print(path)
        name = path.split("-")[1]
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
        img = cv2.resize(img, (856, 540), interpolation=cv2.INTER_CUBIC)

        # for i in range(180,240):
        #     for j in range(100, 500):
        #         binary_img = utils.getCanny(img, i, j, 15, 0)
        #         print(i, j)
        #         utils.show(binary_img, 1)

        binary_img = utils.getCanny(img, 180, 170, 15, 0)
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        global nonList
        recList = []
        flag1 = False
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            if (x > 100) & (x < 500) & (w > 300) & (y > 300) & (h > 30) & (y < 500):
                recList.append(x)
                recList.append(y)
                recList.append(w)
                recList.append(h)
        recArray = np.array(recList).reshape(-1, 4)
        idex = np.lexsort([recArray[:, 2], recArray[:, 1]])
        # 从大到小排
        idex = np.flip(idex)
        sorted_data = recArray[idex, :]
        for data in sorted_data:
            x, y, w, h = data[0:4]
            if (h < 70) & (w > 200) & (w < 600) & (y + h < 520) & (y + h > 420):
                print(path)
                print("find1: %d %d %d %d" % (x, y, w, h))

                crop = img[y:y + h, x:x + w]
                imagegray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)

                # for i in range(300):
                #     retval, imagebin = cv2.threshold(imagegray, i, 255, cv2.THRESH_BINARY+cv2.THRESH_TRUNC)
                #     utils.show(imagebin, 1)
                #     text = pytesseract.image_to_string(imagebin, lang='eng')
                #     print(i, text)

                retval, imagebin = cv2.threshold(imagegray, 20, 255, cv2.THRESH_BINARY + cv2.THRESH_TRUNC)
                text = pytesseract.image_to_string(imagebin, lang='eng')

                if len(text) == 0:
                    text = pytesseract.image_to_string(crop, lang='eng')

                if len(text) != 0:
                    if path.find("front") != -1:
                        text = text.replace("=", "-").replace("~", "-").replace(" ", "") \
                            .replace(",", ".").replace(":", ".").replace("::", ".").replace("+", ".").replace(";", ".")
                        exp_date_list.append([name, text])
                    else:
                        text = text.replace("$", "3").replace(" ", "")
                        number_list.append([name, text])
                    print(text)
                else:
                    non_detect_list.append(path)
                print()
                # 红色 第一次找到
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                flag1 = True
                utils.show(img, 1)
                break
        if not flag1:
            utils.show(binary_img, 1)

            # for i in range(100, 500):
            #     for j in range(0, 900):
            #         binary_img = utils.getCanny(img, i, j, 15, 0)
            #         print(i, j)
            #         utils.show(binary_img, 1)

            binary_img = utils.getCanny(img, 200, 300, 18, 0)
            contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            recList = []
            flag2 = False
            for i in range(len(contours)):
                x, y, w, h = cv2.boundingRect(contours[i])
                if (x > 100) & (x < 500) & (w > 300) & (y > 300) & (h > 30) & (y < 500):
                    recList.append(x)
                    recList.append(y)
                    recList.append(w)
                    recList.append(h)
            recArray = np.array(recList).reshape(-1, 4)
            idex = np.lexsort([recArray[:, 2], recArray[:, 1]])
            # 从大到小排
            idex = np.flip(idex)
            sorted_data = recArray[idex, :]
            for data in sorted_data:
                x, y, w, h = data[0:4]
                if (h < 70) & (w > 200) & (w < 600) & (y + h < 520) & (y + h > 420):
                    print(path)
                    print("find2: %d %d %d %d" % (x, y, w, h))

                    crop = img[y:y + h, x:x + w]
                    imagegray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
                    retval, imagebin = cv2.threshold(imagegray, 20, 255, cv2.THRESH_BINARY + cv2.THRESH_TRUNC)
                    text = pytesseract.image_to_string(imagebin, lang='eng')

                    if len(text) == 0:
                        text = pytesseract.image_to_string(crop, lang='eng')

                    if len(text) != 0:
                        if path.find("front") != -1:
                            text = text.replace("=", "-").replace("~", "-").replace(" ", "") \
                                .replace(",", ".").replace(":", ".").replace("::", ".").replace("+", ".").replace(";",
                                                                                                                  ".")
                            exp_date_list.append([name, text])
                        else:
                            text = text.replace("$", "3").replace(" ", "")
                            number_list.append([name, text])
                        print(text)
                    else:
                        non_detect_list.append(path)
                    # 绿色 第二次找到
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    flag2 = True
                    utils.show(img, 1)
                    break
                else:
                    print(x, y, w, h)
                    # 蓝色 找到 但是不对
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    utils.show(img, 1)
            if not flag2:
                nonList.append(path)
                print(nonList)
                utils.show(binary_img, 1)

            #
            # for i in range(len(contours)):
            #     x, y, w, h = cv2.boundingRect(contours[i])
            #     if (x > 190) & (y > 400) & (h < 90) & (w > 200) & (w < 500):
            #         print(path)
            #         print("find2: %d %d %d %d" % (x, y, w, h))
            #         print()
            #         img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #         flag = True
            #         utils.show(img, 0)
            #         break
            #     else:
            #         print(x, y, w, h)
            #         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #         utils.show(img, 0)
            # if not flag:
            #     nonList.append(path)
            #     print(nonList)
            #     utils.show(binary_img, 0)


if __name__ == '__main__':
    # deal_rest()
    idcard_path = "E:/KingT/staff/result/身份证test"
    # idcard_path = "E:/KingT/staff/result/身份证new"
    # output_target = "E:/KingT/staff/result/身份证new"
    frontalfaceXML = "haarcascade_frontalface_default.xml"
    frontFaceClassifier = cv2.CascadeClassifier(frontalfaceXML)
    nonface_list = []
    nonList = []
    number_list = []
    exp_date_list = []
    non_detect_list = []
    idcard_list = os.listdir(idcard_path)
    lens = len(idcard_list)
    newnew_path = 'E:/KingT/staff/result/身份证newnew'
    for pic in os.listdir(newnew_path):
        pic_path = os.path.join(newnew_path, pic)
        recognize_concat(pic_path, "", False)

    # lens = len(rest_list)
    # for i in range(int(lens / 2)):
    #     pic1 = rest_list[i * 2]
    #     pic1_path = os.path.join(idcard_path, pic1)
    #
    #     pic2 = rest_list[i * 2 + 1]
    #     pic2_path = os.path.join(idcard_path, pic2)
    #
    #     recognize_concat(pic2_path, pic1_path, concat=False)

    # for i in range(int(lens / 2)):
    #     pic1 = idcard_list[i * 2]
    #     pic1_path = os.path.join(idcard_path, pic1)
    #
    #     pic2 = idcard_list[i * 2 + 1]
    #     pic2_path = os.path.join(idcard_path, pic2)
    #
    #     recognize_concat(pic2_path, pic1_path,concat=True)
    print(nonList)
    print(len(nonList))
    print(number_list)
    print(exp_date_list)

    excel_path = 'E:/KingT/staff/result/员工信息new.xls'
    editExcel.update_excel(excel_path, number_list, 2)
    editExcel.update_excel(excel_path, exp_date_list, 3)

    # name = pic1.split("-")[1]
    # front, back = justify_front_back(pic1_path, pic2_path)

    # 调整正反面的方向
    # for i in range(int(lens / 2)):
    #     pic1 = idcard_list[i * 2]
    #     pic1_path = os.path.join(idcard_path, pic1)
    #
    #     pic2 = idcard_list[i * 2 + 1]
    #     pic2_path = os.path.join(idcard_path, pic2)
    #
    #     name = pic1.split("-")[1]
    #     front, back = justify_front_back(pic1_path, pic2_path)

    # 调整正面的方向
    # for pic in idcard_list:
    #     if pic.find("front") != -1:
    #         front_path = os.path.join(idcard_path, pic)
    #         justify_front(front_path)
