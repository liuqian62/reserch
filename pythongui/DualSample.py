
import numpy as np
import cv2
import SimpleITK as sitk
from mpl_toolkits.mplot3d import Axes3D
import os
import sys
from matplotlib import pyplot as plt
import tkinter
import tkinter.messagebox
import re
filename = "E:\\FractureData\\2020_Dicomdata\\six\\2\\"
template = "E:\\FractureData\\2017_Dicomdata\\template\\1\\"


####################################
#   载入单个文件
####################################

def loadFlile(filename):
    ds =sitk.ReadImage(filename)
    img_array = sitk.GetArrayFromImage(ds)
    frame_num,width,height = img_array.shape
    return img_array,frame_num,width,height

####################################
#   载文件序列
####################################
def loadSerise(filename,id):
    reader = sitk.ImageSeriesReader()#读取dicom序列
    reader.MetaDataDictionaryArrayUpdateOn()#这一步是加载公开的元信息
    reader.LoadPrivateTagsOn()#这一步是加载私有的元信息
    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(filename)#根据文件夹获取序列ID,一个文件夹里面通常是一个病人的所有切片，会分为好几个序列

    dicom_names = reader.GetGDCMSeriesFileNames(filename,series_IDs[id])#选取其中一个序列ID,获得该序列的若干文件名
    reader.SetFileNames(dicom_names)#设置文件名
    image3D = reader.Execute()#读取dicom序列
    imgArray=sitk.GetArrayFromImage(image3D)#转换为numpy数据
    print('shape ',imgArray.shape)
    return imgArray.astype(np.float32)

def NormMinandMax(npdarr, min=0, max=1):
    """"
    将数据npdarr 归一化到[min,max]区间的方法
    返回 副本
    """
    arr = npdarr.flatten()
    Ymax = np.max(arr)  # 计算最大值
    Ymin = np.min(arr)  # 计算最小值
    k = (max - min) / (Ymax - Ymin)
    last = min + k * (arr - Ymin)

    return last
####################################
#   检查模板大小
####################################
def check_shape(rawImg,templateImg):
    if templateImg.shape[0] > rawImg.shape[0]:
        print('raw imag',rawImg.shape,"template",templateImg.shape)
        templateImg = templateImg[:rawImg.shape[0],:]
    else:
        templateImg = templateImg
    return rawImg,templateImg

def limitedEqualize(img_array, limit = 4.0):
   img_array_list = []
   clahe = cv2.createCLAHE(clipLimit = limit, tileGridSize = (8,8))
   for img in img_array:
       plt.hist(img.ravel(),256,[0,256])
       plt.show()
       temp = clahe.apply(img)
       img_array_list.append(temp)
   img_array_limited_equalized = np.array(img_array_list)
   return img_array_limited_equalized

####################################
#   遍历目录下的文件夹
####################################
def find_file_name(file_name):
    l = []
    for root,dirs,files in os.walk(file_name):
        for dir in dirs:
            l.append(os.path.join(root,dir))
    return l


def find_best_frame(rawImg,templateImg,templateImg_mirro):
    list_raw = []
    list_mirro = []
    list_flag = []
    temp_img = rawImg[:,1,:]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    for i in range(rawImg.shape[1]):
        if(450>i>200):
            temp_img = rawImg[:,i,:]/2
            cv2.normalize(temp_img, temp_img, 0, 255, cv2.NORM_MINMAX)

            temp_img_left = temp_img[:,:256]
            temp_img_right = temp_img[:,256:]
            # temp_img =  clatch.apply(temp_img.astype(np.uint8))


            res = cv2.matchTemplate(temp_img_left,templateImg,cv2.TM_CCOEFF_NORMED)
            res1 = cv2.matchTemplate(temp_img_right,templateImg_mirro,cv2.TM_CCOEFF_NORMED)
            # plt.cla()
            # plt.imshow(temp_img)
            # plt.pause(0.1)

            #   TM_CCOEFF_NORMED
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
            min_val1,max_val1,min_loc,max_loc = cv2.minMaxLoc(res1)

            list_mirro.append(max_val1-min_val1)
            list_raw.append(max_val-min_val)

    index_raw = np.argmax(np.array(list_raw))

    index_mirro = np.argmax(np.array(list_mirro))
    
    list_raw[index_raw] = 0
    list_raw[index_mirro] = 0

    index_raw = np.argmax(np.array(list_raw))
    index_mirro = np.argmax(np.array(list_mirro))


    return index_raw+200,index_mirro+200

def find_subImg(rawImg,mirroImg,templateImg,templateImg_mirro,oldImg,file_num,index_raw,index_mirro):
    h,w = templateImg.shape[:2]

    best_frame_raw = rawImg 
    best_frame_mirro = mirroImg

    res_raw = cv2.matchTemplate(best_frame_raw,templateImg,cv2.TM_CCOEFF_NORMED)

    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res_raw)
    left_top = max_loc
    right_bottom = (left_top[0]+w,left_top[1]+h)
    cv2.rectangle(best_frame_raw,left_top,right_bottom,(255,0,0),2)
###############################################################################
    res_mirro = cv2.matchTemplate(best_frame_mirro,templateImg_mirro,cv2.TM_CCOEFF_NORMED)
    min_val1,max_val1,min_loc1,max_loc1 = cv2.minMaxLoc(res_mirro)
    left_top1 = max_loc1
    right_bottom1 = (left_top1[0]+w,left_top1[1]+h)
    cv2.rectangle(best_frame_mirro,left_top1,right_bottom1,(255,0,0),2)

    oldImg_raw = oldImg[:,:,:256]
    oldImg_mirro = oldImg[:,:,256:]

    sub_img_raw = oldImg_raw[left_top[1]:left_top[1]+h,150:450,left_top[0]:left_top[0]+w]
    
    sub_img_mirro = oldImg_mirro[left_top1[1]:left_top1[1]+h,150:450,left_top1[0]:left_top1[0]+w]

    plt.cla()
    plt.subplot(2,2,1)
    plt.imshow(best_frame_raw,cmap='gray')
    plt.subplot(2,2,2)
    plt.imshow(best_frame_mirro,cmap='gray')
    plt.subplot(2,2,3)
    plt.imshow(sub_img_raw[:,index_raw-150,:],cmap='gray')
    plt.subplot(2,2,4)
    plt.imshow(sub_img_mirro[:,index_mirro-150,:],cmap='gray')
    plt.pause(1)

    selected_res =tkinter.messagebox.askyesnocancel('提示', '需要保存吗?')

    if selected_res == True:
        np.save("./six_2020/2/%s_raw.npy"%(file_num),sub_img_raw)
    elif selected_res == False:
        np.save("./six_2020/2/%s_mirror.npy"%(file_num),sub_img_mirro)

    return best_frame_raw,best_frame_mirro

def main():
    files = find_file_name(filename)

    # rawImg = loadSerise(filename,2)

    templateImg = loadSerise(template,0)
    # templateImg[50:110,252,100:310] =0
    templateImg_match = templateImg[:,252,175:310]

    # templateImg = templateImg[50:120,252,200:310]

    rows, cols = templateImg_match.shape

    M = cv2.getRotationMatrix2D(((cols - 1) / 2.0, (rows - 1) / 2.0), 4, 1)  # 旋转中心x,旋转中心y，旋转角度，缩放因子
    templateImg_match = cv2.warpAffine(templateImg_match, M, (cols, rows))  #在内存里完成了旋转

    # cv2.normalize(templateImg, templateImg, 0, 255, cv2.NORM_MINMAX)
    cv2.normalize(templateImg_match, templateImg_match, 0, 255, cv2.NORM_MINMAX)

    templateImg_match = templateImg_match/10

    for i in files:
        res_num =re.findall(r'\b\d+\b', i)
        print('当前目录是：',res_num)
        try:
            rawImg = loadSerise(i,0)
        except IOError: 
            pass
        # rawImg_left,tempImg = check_shape(rawImg,templateImg) #模板处理，防止模板过大
        _,tempImg_match =check_shape(rawImg,templateImg_match)
        # templateImg_mirro = cv2.flip(tempImg,1)
        templateImg_match_mirro = cv2.flip(tempImg_match,1)

        index_raw ,index_mirro = find_best_frame(rawImg,tempImg_match,templateImg_match_mirro)

        print('raw frame',index_raw,'mirro_frame',index_mirro)

        best_frame, best_frame1 = find_subImg(rawImg[:,index_raw,:256],rawImg[:,index_mirro,256:],tempImg_match,templateImg_match_mirro,rawImg,res_num[1],index_raw,index_mirro)
        # np.save("./data/%d.npy"%index,sub3DImg)



if __name__ == "__main__":
    main()