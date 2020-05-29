#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   utils.py    
# @Modify Time: 2020/5/25 8:21       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:
import cv2
import math
import numpy as np


def img_resize(image, height=700):
    h, w = image.shape[:2]
    pro = height / h
    size = (int(w * pro), int(height))
    img = cv2.resize(image, size)
    return img


def show(img, key):
    cv2.imshow("img", img)
    cv2.waitKey(key)


# 透视变换
def warpImage(image, box):
    # 身份证尺寸 856*540
    dst_rect = np.array([[0, 0],
                         [856, 0],
                         [856, 540],
                         [0, 540]], dtype='float32')
    M = cv2.getPerspectiveTransform(box, dst_rect)
    warped = cv2.warpPerspective(image, M, (856, 540))
    return warped


def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # 计算变换矩阵，参数一次表示(旋转中心，旋转角度，缩放因子)，其中旋转角度正为逆时针
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)

    # 为了使旋转后的图片完全显示，所以需要调整输出图片的大小
    nH = int(abs(h * math.cos(math.radians(angle))) + abs(w * math.sin(math.radians(angle))))
    nW = int(abs(h * math.sin(math.radians(angle))) + abs(w * math.cos(math.radians(angle))))

    # 调整旋转矩阵以考虑旋转
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # 计算旋转后的图片并输出
    return cv2.warpAffine(image, M, (nW, nH))


# 边缘检测
def getCanny(image, s1, s2, k1, k2):
    # 高斯模糊
    binary = cv2.GaussianBlur(image, (3, 3), 2, 2)
    # 边缘检测
    binary = cv2.Canny(binary, s1, s2, apertureSize=3)
    # 膨胀操作，尽量使边缘闭合
    kernel1 = np.ones((k1, k1), np.uint8)
    binary = cv2.dilate(binary, kernel1, iterations=1)
    # 侵蚀操作
    kernel2 = np.ones((k2, k2), np.uint8)
    binary = cv2.erode(binary, kernel2, iterations=1)
    return binary


# 求出面积最大的轮廓
def findMaxContour(image):
    # 寻找边缘
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 计算面积
    max_area = 0.0
    max_contour = []
    for contour in contours:
        currentArea = cv2.contourArea(contour)
        if currentArea > max_area:
            max_area = currentArea
            max_contour = contour
    return max_contour, max_area


# 多边形拟合凸包的四个顶点
def getBoxPoint(contour):
    # 多边形拟合凸包
    hull = cv2.convexHull(contour)
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(hull, epsilon, True)
    approx = approx.reshape((len(approx), 2))
    return approx


def getCornerPoint(lines):
    point = []
    verticalLine = []
    horizontalLine = []

    for i in range(len(lines)):
        x1 = lines[i][0][0]
        y1 = lines[i][0][1]
        x2 = lines[i][0][2]
        y2 = lines[i][0][3]
        if (x1 - x2 != 0) & (y1 - y2 != 0):
            k = (y1 - y2) / (x1 - x2)
            print(x1, y1, x2, y2, k)
            b = y1 - k * x1
            if abs(k) > 1:
                horizontalLine.append([k, b])
            else:
                verticalLine.append([k, b])

    xmin = 20000
    xmax = 0
    ymin = 20000
    ymax = 0
    bg = np.zeros((1000, 1000, 3), np.uint8)
    bg.fill(0)

    for i in range(len(verticalLine)):
        for j in range(len(horizontalLine)):
            line1 = verticalLine[i]
            line2 = horizontalLine[j]
            k1 = line1[0]
            b1 = line1[1]

            k2 = line2[0]
            b2 = line2[1]

            pointx = int((b1 - b2) / (k2 - k1))
            pointy = int(k2 * pointx + b2)

            cv2.line(bg, (int(-b1 / k1), 0), (int((1000 - b1) / k1), 1000), (0, 255, 0))
            cv2.line(bg, (0, int(k2 * 0 + b2)), (1000, int(k2 * 1000 + b2)), (255, 0, 0))
            cv2.circle(bg, (pointx, pointy), 5, (0, 255, 0))
            show(bg, 1)
            if pointx > xmax:
                xmax = pointx
            if pointx < xmin:
                xmin = pointx

            if pointy > ymax:
                ymax = pointy
            if pointy < ymin:
                ymin = pointy
            point.append([pointx, pointy])

    xmid = (xmin + xmax) / 2
    ymid = (ymin + ymax) / 2

    topLeftP = []
    topRightP = []
    bottomLeftP = []
    bottomRightP = []
    for p in point:
        px = p[0]
        py = p[1]
        if (px < xmid) & (py < ymid):
            topLeftP.append(p)
        elif (px > xmid) & (py < ymid):
            topRightP.append(p)
        elif (px < xmid) & (py > ymid):
            bottomLeftP.append(p)
        elif (px > xmid) & (py > ymid):
            bottomRightP.append(p)

    topLeftP = np.trunc((np.array(topLeftP).mean(axis=0))).tolist()
    topRightP = np.trunc(np.array(topRightP).mean(axis=0)).tolist()
    bottomLeftP = np.trunc(np.array(bottomLeftP).mean(axis=0)).tolist()
    bottomRightP = np.trunc(np.array(bottomRightP).mean(axis=0)).tolist()
    point = [topLeftP, topRightP, bottomLeftP, bottomRightP]
    print(point)
    for p in point:
        print(p)

    for i in range(4):
        for j in range(2):
            print(point[i][j])
            # point[i][j] = int(point[i][j])
    return point


# 适配原四边形点集
def adaPoint(box, pro):
    box_pro = box
    if pro != 1.0:
        box_pro = box / pro
    box_pro = np.trunc(box_pro)
    return box_pro


# 四边形顶点排序，[top-left, top-right, bottom-right, bottom-left]
def orderPoints(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect
