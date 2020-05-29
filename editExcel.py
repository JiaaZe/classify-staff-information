#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File:   editExcel.py    
# @Modify Time: 2020/5/25 13:59       
# @Author: JiaZe
# @Version: 1.0    
# @Desciption:对excel进行操作

import os
import shutil

import pandas as pd
import xlrd
from xlutils.copy import copy


# 根据身份证文件夹 把工号 姓名填入excel
def fill_id_name(path):
    j = 1
    for i in os.listdir(path):
        data = pd.read_excel("E:/KingT/staff/result/员工信息new.xls")
        if i.startswith("JT"):
            employee_id = i[0:5]
            employee_name = i[5:]
        elif i.startswith("！！"):
            employee_id = "-"
            employee_name = i[2:]
        elif i.startswith("实习生"):
            employee_id = "-"
            employee_name = i[3:]
        else:
            employee_id = "-"
            employee_name = i
        data.loc[j] = [employee_id, employee_name, "-", "-", "-", "-"]
        j = j + 1
        print(j)
        pd.DataFrame(data).to_excel('E:/KingT/staff/result/员工信息new.xls', sheet_name='Sheet1', index=False, header=True)
    data = pd.read_excel("E:/KingT/staff/result/员工信息new.xls")
    print(data)


# 更新毕业证，学位证栏位
def update_excel_graduation_degree(path, excel_path, column, index):
    rb = xlrd.open_workbook(excel_path)  # 打开weng.xls文件
    wb = copy(rb)  # 利用xlutils.copy下的copy函数复制
    ws = wb.get_sheet(0)  # 获取表单0
    # path:E:/KingT/staff/result/毕业证
    target_path = os.path.join(path, column)
    for fname in os.listdir(target_path):
        # f:E:/KingT/staff/result/毕业证/JT000小明
        folder = os.path.join(target_path, fname)

        if fname.startswith("JT"):
            employee_name = fname[5:]
        elif fname.startswith("！！"):
            employee_name = fname[2:]
        elif fname.startswith("实习生"):
            employee_name = fname[3:]
        else:
            employee_name = fname
        if len(os.listdir(folder)) != 0:
            # 没有图片
            for i in range(rb.sheets()[0].nrows):
                if employee_name == rb.sheets()[0].cell(i, 1).value:
                    ws.write(i, index, '有')  # 改变（0,0）的值
    wb.save(excel_path)


# 传入list类型的资料，更新 第index栏 位
def update_excel(excel_path, data_list, index):
    rb = xlrd.open_workbook(excel_path)  # 打开weng.xls文件
    wb = copy(rb)  # 利用xlutils.copy下的copy函数复制
    ws = wb.get_sheet(0)  # 获取表单0
    for l in data_list:
        name = l[0]
        data = l[1]
        print(name, data)
        for i in range(rb.sheets()[0].nrows):
            if name == rb.sheets()[0].cell(i, 1).value:
                if data != "":
                    ws.write(i, index, data)  # 改变（0,0）的值
    wb.save(excel_path)


# 改编文件夹布局,重命名文件
def reconstruction(path):
    for fname in os.listdir(path):
        folder_path = os.path.join(path, fname)
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
        new_picname = employee_id + "-" + employee_name + "-" + path[-3:] + "书.jpg"
        save_path = os.path.join(path, new_picname)
        for pic in os.listdir(folder_path):
            pic_path = os.path.join(folder_path, pic)
            shutil.copy(pic_path, save_path)


# 找出excel中缺失身份证资料的人，并把他的原始身份证图片复制到新的文件夹中，集中再识别
def check_pick_non(path):
    global front_list
    global back_list
    rb = xlrd.open_workbook(path)  # 打开weng.xls文件
    for i in range(rb.sheets()[0].nrows):
        name = rb.sheets()[0].cell(i, 1).value
        id_number = rb.sheets()[0].cell(i, 2).value
        id_exp_date = rb.sheets()[0].cell(i, 3).value.replace("—", "-")
        edit_front_flag = False
        edit_back_flag = False
        if id_number == "缺":
            edit_back_flag = False
        elif len(id_number) != 18:
            edit_back_flag = True
        elif (id_number[6] != "1") | (not id_number[:17].isdigit()):
            edit_back_flag = True

        if id_exp_date == "缺":
            edit_front_flag = False
        elif len(id_exp_date) != 21:
            edit_front_flag = True
        elif id_exp_date[10] != "-":
            edit_front_flag = True
        else:
            start = id_exp_date.split("-")[0]
            end = id_exp_date.split("-")[1]
            if (start[3:] != end[3:]) | (start[:2] != end[:2]):
                edit_front_flag = True

        if edit_back_flag:
            print("back %s %s" % (name, id_number))
            for pic in os.listdir(from_path):
                if (pic.find(name) != -1) & (pic.find("back") != -1):
                    shutil.copy(os.path.join(from_path, pic), os.path.join(to_path, pic))
        if edit_front_flag:
            print("front %s %s" % (name, id_exp_date))
            for pic in os.listdir(from_path):
                if (pic.find(name) != -1) & (pic.find("front") != -1):
                    shutil.copy(os.path.join(from_path, pic), os.path.join(to_path, pic))


excel_path = 'E:/KingT/staff/result/员工信息new.xls'
from_path = 'E:/KingT/staff/result/身份证test'
to_path = 'E:/KingT/staff/result/身份证newnew'

front_list = []
back_list = []

if __name__ == '__main__':
    check_pick_non(excel_path)
# fill_id_name("E:/KingT/staff/员工档案")
# update_excel_graduation_degree('E:/KingT/staff/result',"毕业证",4)
# update_excel_graduation_degree('E:/KingT/staff/result',"学位证",5)
# reconstruction("E:/KingT/staff/result/学位证")
