#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   idCardRecognition.py    
# @Modify Time: 2020/5/26 9:56       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:识别身份证图片，抓取身份证号以及到期日，并重新排版
import os
import shutil
import numpy as np
import cv2
import pytesseract
import editExcel
import utils


# 废弃
def crop_all(path):
    for fname in os.listdir(path):
        # folder_path:"E:/KingT/staff/result/身份证/JTXXXXXX"
        folder_path = os.path.join(path, fname)
        for pic in os.listdir(folder_path):
            # pic_path:"E:/KingT/staff/result/身份证/JTXXXXXX/pic"
            pic_path = os.path.join(folder_path, pic)
            if pic_path.endswith("jpg") | pic_path.endswith("tif"):
                crop_main(pic_path)


# 废弃
def crop_main(img_path):
    # base_path=img_path.split("/")
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), 1)
    img = utils.img_resize(img, 900)
    binary_img = utils.getCanny(img, 20, 50, 3, 0)
    # max_contour, max_area = utils.findMaxContour(binary_img)
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        rotate = False
        if area > 5000:
            x, y, w, h = cv2.boundingRect(contours[i])
            if w > h:
                if (w / h < 1) | (w / h > 2):
                    break
                else:
                    print(w, h)
            else:
                if (h / w < 1) | (h / w > 2):
                    break
                else:
                    print(w, h)
                    rotate = True
            image = img[y - 10:y + h + 10, x - 10:x + w + 10]
            print(image.shape)
            if rotate:
                image = utils.rotate_image(image, 90)
            image = cv2.resize(image, (856, 540), interpolation=cv2.INTER_CUBIC)
            print(image.shape)
            if len(image.shape) == 3:
                image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                image_grey = image

            front_face_detected = frontFaceClassifier.detectMultiScale(image_grey, scaleFactor=1.2,
                                                                       minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)

            if len(front_face_detected) != 0:
                for x, y, w, h in front_face_detected:
                    if x < 856 / 2:
                        image = utils.rotate_image(image, 180)
                    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)
            utils.show(image, 1)
            name = img_path.split("\\")[1]
            # 把框出来的身份证图片另存为
            cv2.imencode('.jpg', image)[1].tofile(
                "E:/KingT/staff/test/all身份证/" + name + "_" + str(i) + img_path.split("\\")[2])


# 得到对齐的图片 有小bug
def getAlignedImage(img):
    # for i in range(50, 100):
    #     for j in range(200, 255):
    #         binary_img = getCanny(img, j, i, 3, 0)
    #         print(i, j)
    #         show(binary_img, 10)
    binary_img = utils.getCanny(img, 20, 50, 3, 0)
    # show(binary_img, 0)
    max_contour, max_area = utils.findMaxContour(binary_img)
    h, w = img.shape[:2]
    bg = np.zeros((h, w, 3), np.uint8)
    bg.fill(0)
    cv2.drawContours(bg, max_contour, -1, (0, 0, 255), 1)

    bg = utils.getCanny(bg, 30, 30, 7, 0)
    lines = cv2.HoughLinesP(bg, 1, np.pi / 180, 100, maxLineGap=50)
    # 画出边框线
    # for i in range(len(lines)):
    #     for x1, y1, x2, y2 in lines[i]:
    #         cv2.line(img, (x1, y1), (x2, y2), (112, 255, 0), 2)
    #         show(img,0)
    # 得到四个角坐标
    point = utils.getCornerPoint(lines)
    print(point)
    # boxes = adaPoint(point, ratio)
    boxes = np.trunc(point)
    boxes = utils.orderPoints(boxes)
    warped = utils.warpImage(img, boxes)
    utils.show(warped, 0)
    return warped


# 得到有效期区块的截图
def getExpDateCrop(img):
    # img = getAlignedImage(img)
    back = False
    image_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    front_face_detected = frontFaceClassifier.detectMultiScale(image_grey, scaleFactor=1.2,
                                                               minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)

    if len(front_face_detected) != 0:
        back = True
    binary_img = utils.getCanny(img, 100, 200, 20, 0)

    # for i in range(180,200):
    #     for j in range(350,400):
    #         binary_img = utils.getCanny(img, j, i, 15, 0)
    #         print(i, j)
    #         utils.show(binary_img, 1)

    # utils.show(binary_img, 0)
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    recList = []
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        area = w * h
        if (area > 1000) & (h < 80) & (y > 300) & (x > 280) & (x < 400):
            recList.append(x)
            recList.append(y)
            recList.append(w)
            recList.append(h)
            # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)  # 绿色
            # utils.show(img, 0)

    # 对轮廓坐标进行排序
    if len(recList) != 0:
        recArray = np.array(recList).reshape(-1, 4)
        idex = np.lexsort([recArray[:, 0], recArray[:, -1]])
        sorted_data = recArray[idex, :]
        # print(sorted_data)
        # utils.show(img, 0)
        # 找到期限的坐标
        # for i in range(len(sorted_data)):
        x, y, w, h = sorted_data[0]
        print(x, y, w, h)
        # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)  # 红色
        # utils.show(img, 0)
        return img[y:y + h, x:x + w], back
    else:
        print("?????")
        return "", back


# 识别得到的区域图片 crop
def detect_target(path):
    number = []
    exp_date = []
    for i in os.listdir(path):
        pic_path = os.path.join(path, i)
        print(pic_path)
        img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), 1)
        crop, back = getExpDateCrop(img)
        if crop != "":
            # utils.show(crop, 0)
            crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
            # retval, crop = cv2.threshold(crop, 120, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(crop, lang='eng')
        # shutil.copy(pic_path,"E:/KingT/staff/test/all身份证/"+pic)
        # print(pic_path)

        fname = i.split("_")[0]
        if fname.startswith("JT"):
            employee_id = fname[0:5]
            employee_name = fname[5:]
        elif fname.startswith("！！"):
            employee_id = "-"
            employee_name = fname[2:]
        elif fname.startswith("实习生"):
            employee_id = "-"
            employee_name = fname[3:]
        else:
            employee_id = "-"
            employee_name = fname
        print(employee_name, text)

        if back:
            number.append([employee_name, text])
        else:
            exp_date.append([employee_name, text])
    return number, exp_date


# 处理身份证图片 输入个人文件夹 里面的身份证有的是正反合一 有的是分开
def deal_idcard(folder):
    pic_list = os.listdir(folder)
    print()
    print("pic num=", str(len(pic_list)))
    #  正反合一的情况
    if len(pic_list) == 1:
        image_path = os.path.join(folder, pic_list[0])
        # 国徽面，人像面
        front, back = detect_one(image_path)
        print("front")
        utils.show(front, 0)
        print("back")
        utils.show(back, 0)
        return front, back, 2, 3
        output, deal_number, deal_exp_date = recognize_concat(front, back)
        return output, deal_number, deal_exp_date
    # 正反分开
    elif len(pic_list) == 2:
        image_path1 = os.path.join(folder, pic_list[0])
        image_path2 = os.path.join(folder, pic_list[1])
        front, back = detect_two(image_path1, image_path2)
        print("front")
        utils.show(front, 90)
        print("back")
        utils.show(back, 90)
        return front, back, 2, 3
        output, deal_number, deal_exp_date = recognize_concat(front, back)
        return output, deal_number, deal_exp_date
    else:
        print(pic_list)
        print("=========== no idcard picture ==========")
        return np.ones((1, 1, 3), dtype=np.uint8), np.ones((1, 1, 3), dtype=np.uint8), 2, 3


# 输入一张图片，返回正反面
def detect_one(path):
    print("=====detect one=====")
    print(path)
    global null_list
    null_flag = False
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)

    # for i in range(10, 50):
    #     for j in range(0, 20):
    #         binary_img = utils.getCanny(img, i, j, 3, 0)
    #         print(i, j)
    #         utils.show(utils.img_resize(binary_img), 10)

    binary_img = utils.getCanny(img, 20, 60, 20, 0)
    # utils.show(utils.img_resize(binary_img), 0)
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    img_list = []
    for i in range(len(contours)):
        rotate = False
        x, y, w, h = cv2.boundingRect(contours[i])
        # print(x, y, w, h)
        # m = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
        # utils.show(utils.img_resize(m), 0)
        if (w * h > 25000) & (w > 100) & (h > 100) & (x > 0) & (y > 0):
            if w > h:
                if (w / h < 1) | (w / h > 2):
                    break
                else:
                    ...
                    # print(w, h)
            else:
                if (h / w < 1) | (h / w > 2):
                    break
                else:
                    # print(w, h)
                    rotate = True
            if (y - 10 > 0) & (x - 10 > 0):
                image = img[y - 10:y + h + 10, x - 10:x + w + 10]
            else:
                image = img[y:y + h, x:x + w]
            if rotate:
                image = utils.rotate_image(image, 90)
            image = cv2.resize(image, (856, 540), interpolation=cv2.INTER_CUBIC)
            img_list.append(image)

    while len(img_list) < 2:
        print(str(len(img_list)), path)
        null_flag = True
        print("null")
        null_list.append(path)
        img_list.append(np.zeros((540, 856, 3), dtype=np.uint8))

    fname = path.split("\\")[1]
    pic_name = path.split("\\")[2]
    out_folder_path = "E:/KingT/staff/result/身份证null/" + fname
    if null_flag:
        if not os.path.exists(out_folder_path):
            os.mkdir(out_folder_path)
        # shutil.copy(path, out_folder_path + "/" + pic_name)
    else:
        if os.path.exists(out_folder_path):
            # ...
            shutil.rmtree(out_folder_path)
    # 检测[0]是否有人脸
    for i in range(2):
        image_grey = cv2.cvtColor(img_list[0], cv2.COLOR_BGR2GRAY)
        front_face_detected = frontFaceClassifier.detectMultiScale(image_grey, scaleFactor=1.25,
                                                                   minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)
        if len(front_face_detected) != 0:
            for x, y, w, h in front_face_detected:
                # print(x, y, w, h)
                if (w > 120) & (x > 300):
                    # cv2.rectangle(img_list[0], (x, y), (x + w, y + h), (0, 255, 255), 2)
                    # utils.show(img_list[1], 200)
                    # utils.show(img_list[0], 200)
                    return img_list[1], img_list[0]
                else:
                    if i == 1:
                        return img_list[0], img_list[1]
                    else:
                        img_list[0] = utils.rotate_image(img_list[0], 180)

        else:
            if i == 1:
                return img_list[0], img_list[1]
            else:
                img_list[0] = utils.rotate_image(img_list[0], 180)


# 输入两张图片，返回正反面
def detect_two(path1, path2):
    global null_list
    print("=====detect two=====")
    print(path1)
    print(path2)
    null_flag = False
    img1 = cv2.imdecode(np.fromfile(path1, dtype=np.uint8), 1)
    img2 = cv2.imdecode(np.fromfile(path2, dtype=np.uint8), 1)
    img_list = []
    for img in [img1, img2]:

        # img = utils.img_resize(img)
        # for i in range(0, 100):
        #     for j in range(0, 100):
        #         binary_img = utils.getCanny(img, i, j, 6, 0)
        #         print(i, j)
        #         utils.show(binary_img, 10)

        binary_img = utils.getCanny(img, 20, 60, 20, 0)
        # utils.show(utils.img_resize(binary_img), 0)
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in range(len(contours)):
            rotate = False
            x, y, w, h = cv2.boundingRect(contours[i])
            # print(x, y, w, h)
            # m = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # utils.show(utils.img_resize(m), 0)
            if (w * h > 25000) & ((w > 275) | (h > 275)) & (x > 0) & (y > 0):
                if w > h:
                    if (w / h < 1) | (w / h > 2):
                        break
                    else:
                        print(w, h)
                else:
                    if (h / w < 1) | (h / w > 2):
                        break
                    else:
                        print(w, h)
                        rotate = True
                if (y - 10 > 0) & (x - 10 > 0):
                    image = img[y - 10:y + h + 10, x - 10:x + w + 10]
                else:
                    image = img[y:y + h, x:x + w]
                if rotate:
                    image = utils.rotate_image(image, 90)
                image = cv2.resize(image, (856, 540), interpolation=cv2.INTER_CUBIC)
                # utils.show(image, 0)
                img_list.append(image)

    while len(img_list) < 2:
        print(str(len(img_list)), path1, path2)
        print("null")
        null_flag = True
        null_list.append(path1)
        img_list.append(np.zeros((540, 856, 3), dtype=np.uint8))

    fname = path1.split("\\")[1]
    out_folder_path = "E:/KingT/staff/result/身份证null/" + fname
    if null_flag:
        pic_name1 = path1.split("\\")[2]
        pic_name2 = path2.split("\\")[2]
        if not os.path.exists(out_folder_path):
            os.mkdir(out_folder_path)
        # shutil.copy(path1, out_folder_path + "/" + pic_name1)
        # shutil.copy(path2, out_folder_path + "/" + pic_name2)
    else:
        if os.path.exists(out_folder_path):
            # ...
            shutil.rmtree(out_folder_path)
    # 检测人脸
    for i in range(2):
        image_grey = cv2.cvtColor(img_list[0], cv2.COLOR_BGR2GRAY)
        front_face_detected = frontFaceClassifier.detectMultiScale(image_grey, scaleFactor=1.25,
                                                                   minNeighbors=5,
                                                                   flags=cv2.CASCADE_SCALE_IMAGE)
        if len(front_face_detected) != 0:
            for x, y, w, h in front_face_detected:
                # print(x, y, w, h)
                if (w > 120) & (x > 300):
                    # cv2.rectangle(img_list[0], (x, y), (x + w, y + h), (0, 255, 255), 2)
                    # utils.show(img_list[1], 200)
                    # utils.show(img_list[0], 200)
                    return img_list[1], img_list[0]
                else:
                    if i == 1:
                        return img_list[0], img_list[1]
                    else:
                        img_list[0] = utils.rotate_image(img_list[0], 180)

        else:
            return img_list[0], img_list[1]


if __name__ == '__main__':
    null_list = []
    excel_path = 'E:/KingT/staff/result/员工信息new.xls'
    frontalfaceXML = "haarcascade_frontalface_default.xml"
    frontFaceClassifier = cv2.CascadeClassifier(frontalfaceXML)
    base_path = "E:/KingT/staff/result/身份证"
    id_number = []
    id_exp_date = []
    test_path = "E:/KingT/staff/result/身份证null"
    # for fname in os.listdir(base_path):
    for fname in os.listdir(test_path):
        folder_path = os.path.join(test_path, fname)
        if fname.startswith("JT"):
            employee_id = fname[0:5]
            employee_name = fname[5:]
        elif fname.startswith("！！"):
            employee_id = "工号"
            employee_name = fname[2:]
        elif fname.startswith("实习生"):
            employee_id = "工号"
            employee_name = fname[3:]
        else:
            employee_id = "工号"
            employee_name = fname
        # img, number, exp_date = deal_idcard(folder_path)
        out_path = "E:/KingT/staff/result/身份证test/" + employee_id + "-" + employee_name + "-身份证"
        f, b, _, _ = deal_idcard(folder_path)
        cv2.imencode('.jpg', f)[1].tofile(out_path + "_front.jpg")
        cv2.imencode('.jpg', b)[1].tofile(out_path + "_back.jpg")
        print(null_list)
    # id_number.append([employee_name, number])
    # id_exp_date.append([employee_name, exp_date])
    # output_path = "E:/KingT/staff/result/身份证new/" + employee_id + "-" + employee_name + "-身份证.jpg"
    # cv2.imencode('.jpg', img)[1].tofile(output_path)

    # 裁剪出身份证区域
    # crop_all(base_path)
    # id_number存放身份证号码的list id_exp_date存放有效期的list
    # id_number, id_exp_date = detect_target("E:/KingT/staff/test/all身份证")
    # print(id_number, id_exp_date)
    # editExcel.update_excel(excel_path,id_number, 2)
    # editExcel.update_excel(excel_path,id_exp_date, 3)
