import copy
import numpy as np
import cv2
import pydicom
import SimpleITK as sitk
from mpl_toolkits.mplot3d import Axes3D
import os
import sys
from matplotlib import pyplot as plt
import tkinter
import tkinter.messagebox
import tkinter as tk
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from tkinter import filedialog
import skimage
from skimage import measure, feature

'''打开选择文件夹对话框'''
root = tk.Tk()
root.withdraw()

filename = filedialog.askdirectory() #获得选择好的文件夹

def loadSerise(filename,id):
    reader = sitk.ImageSeriesReader()#读取dicom序列
    reader.MetaDataDictionaryArrayUpdateOn()#这一步是加载公开的元信息
    reader.LoadPrivateTagsOn()#这一步是加载私有的元信息
    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(filename)#根据文件夹获取序列ID,一个文件夹里面通常是一个病人的所有切片，会分为好几个序列

    dicom_names = reader.GetGDCMSeriesFileNames( filename,series_IDs[id])#选取其中一个序列ID,获得该序列的若干文件名
    reader.SetFileNames(dicom_names)#设置文件名
    image3D = reader.Execute()#读取dicom序列
    imgArray=sitk.GetArrayFromImage(image3D)#转换为numpy数据
    return imgArray.astype(np.float32)
def plot_3d(image, threshold=-300):
    
    # Position the scan upright, 
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2,1,0)
    
    verts, faces = skimage.measure.marching_cubes_classic(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha=0.70)
    face_color = [0.45, 0.45, 0.75]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])

    plt.show()
    

def main():
    templateImg = loadSerise(filename,0)
    print(templateImg.shape)
    plt.imshow(templateImg[20,:,:], cmap='gray')
    plt.show()
    best_frame_raw = templateImg[:,220,:]
    #plt.cla()
    plt.imshow(best_frame_raw,cmap='gray')
    plt.imshow(templateImg[:,220,:], cmap='gray')
    plt.show()
    plt.imshow(templateImg[:,:,250], cmap='gray')
    plt.show()
    plot_3d(templateImg, 300)



if __name__ == "__main__":
    main()
