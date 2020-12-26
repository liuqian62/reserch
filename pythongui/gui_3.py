#import sys, os
#import plotly.offline
#from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebEngineView
#from PyQt5.QtWidgets import QApplication

import os
import re
#import docx
import pandas as pd
import tkinter as tk
import tkinter.messagebox
#from docx        import Document
from tkinter     import filedialog
#from win32com    import client as wc
#from prettytable import PrettyTable
#from openpyxl    import Workbook
#from openpyxl    import load_workbook


import copy
import numpy as np
import cv2
import pydicom
import SimpleITK as sitk
from mpl_toolkits.mplot3d import Axes3D
import sys
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
import tkinter.messagebox
#from mpl_toolkits.mplot3d.art3d import Poly3DCollection
#from tkinter import filedialog
import skimage
from skimage import measure, feature

from glob import glob
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import scipy.ndimage
from skimage import morphology
from skimage import measure
from skimage.transform import resize
from sklearn.cluster import KMeans
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import *
from PIL import ImageTk,Image

def plotly_3d(verts, faces):
    x,y,z = zip(*verts) 
    
    print ("Drawing")
    
    # Make the colormap single color since the axes are positional not intensity. 
#    colormap=['rgb(255,105,180)','rgb(255,255,51)','rgb(0,191,255)']
    colormap=['rgb(236, 236, 212)','rgb(236, 236, 212)']
    
    fig = FF.create_trisurf(x=x,
                        y=y, 
                        z=z, 
                        plot_edges=False,
                        colormap=colormap,
                        simplices=faces,
                        backgroundcolor='rgb(64, 64, 64)',
                        title="三维交互立体图")
    #plot(fig)
    import sys, os
    import plotly.offline
    from PyQt5.QtCore import QUrl
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWidgets import QApplication

    plotly.offline.plot(fig, filename='diocm_3d.html', auto_open=False)

    app = QApplication(sys.argv)
    web = QWebEngineView()
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "diocm_3d.html"))
    web.load(QUrl.fromLocalFile(file_path))
    web.show()
    sys.exit(app.exec_())

def make_mesh(image, threshold=-300, step_size=1):

    print ("Transposing surface")
    p = image.transpose(2,1,0)
    
    print ("Calculating surface")
    verts, faces, norm, val = measure.marching_cubes_lewiner(p, threshold, step_size=step_size, allow_degenerate=True) 
    return verts, faces
   
def show3d():


 

    global templateImg
    v, f = make_mesh(templateImg, 350, 2)
    plotly_3d(v, f)





def get_image(filename,width,height):
    im = Image.open(filename).resize((width,height))
    return ImageTk.PhotoImage(im)

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
    
def check_shape(rawImg,templateImg):
    if templateImg.shape[0] > rawImg.shape[0]:
        print('raw imag',rawImg.shape,"template",templateImg.shape)
        templateImg = templateImg[:rawImg.shape[0],:]
    else:
        templateImg = templateImg
    return rawImg,templateImg
    
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

    # plt.cla()
    # plt.subplot(2,2,1)
    # plt.imshow(best_frame_raw,cmap='gray')
    # plt.subplot(2,2,2)
    # plt.imshow(best_frame_mirro,cmap='gray')
    # plt.subplot(2,2,3)
    # plt.imshow(sub_img_raw[:,index_raw-150,:],cmap='gray')
    # plt.subplot(2,2,4)
    # plt.imshow(sub_img_mirro[:,index_mirro-150,:],cmap='gray')
    # plt.pause(1)

    # selected_res =tkinter.messagebox.askyesnocancel('提示', '需要保存吗?')

    # if selected_res == True:
        # np.save("./six_2020/2/%s_raw.npy"%(file_num),sub_img_raw)
    # elif selected_res == False:
        # np.save("./six_2020/2/%s_mirror.npy"%(file_num),sub_img_mirro)

    return sub_img_raw,sub_img_mirro
    
def find_frame():
    global templateImg
    global left_raw
    global right_raw
    
    templateImg1 = loadSerise(template,0)
    # templateImg[50:110,252,100:310] =0
    templateImg_match = templateImg1[:,252,175:310]

    # templateImg = templateImg[50:120,252,200:310]

    rows, cols = templateImg_match.shape

    M = cv2.getRotationMatrix2D(((cols - 1) / 2.0, (rows - 1) / 2.0), 4, 1)  # 旋转中心x,旋转中心y，旋转角度，缩放因子
    templateImg_match = cv2.warpAffine(templateImg_match, M, (cols, rows))  #在内存里完成了旋转

    # cv2.normalize(templateImg, templateImg, 0, 255, cv2.NORM_MINMAX)
    cv2.normalize(templateImg_match, templateImg_match, 0, 255, cv2.NORM_MINMAX)

    templateImg_match = templateImg_match/10

    # for i in files:
        # res_num =re.findall(r'\b\d+\b', i)
        # print('当前目录是：',res_num)
        # try:
            # rawImg = loadSerise(i,0)
        # except IOError: 
            # pass
        # # rawImg_left,tempImg = check_shape(rawImg,templateImg) #模板处理，防止模板过大
    _,tempImg_match =check_shape(templateImg,templateImg_match)
        # templateImg_mirro = cv2.flip(tempImg,1)
    templateImg_match_mirro = cv2.flip(tempImg_match,1)

    index_raw ,index_mirro = find_best_frame(templateImg,tempImg_match,templateImg_match_mirro)

    print('raw frame',index_raw,'mirro_frame',index_mirro)

    left_raw, right_raw = find_subImg(templateImg[:,index_raw,:256],templateImg[:,index_mirro,256:],tempImg_match,templateImg_match_mirro,templateImg,res_num[1],index_raw,index_mirro)
        # np.save("./data/%d.npy"%index,sub3DImg)

def plot_3d(image, threshold=-300):
    
    # Position the scan upright, 
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2,1,0)
    
    verts, faces = skimage.measure.marching_cubes_classic(p, threshold)
    #verts, faces = measure.marching_cubes(p, threshold)
    plt.subplot(224)
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
def show1(z):
    global templateImg
    global winNew
    global v4
    global photo1




    if v4==1:
        s1=int(z)
        # img=templateImg[s1,:,:]
        # row_size= img.shape[0]
        # col_size = img.shape[1]
        
        # mean = np.mean(img)
        # std = np.std(img)
        # img = img-mean
        # img = img/std
        # # Find the average pixel value near the lungs
        # # to renormalize washed out images
        # middle = img[int(col_size/5):int(col_size/5*4),int(row_size/5):int(row_size/5*4)] 
        # mean = np.mean(middle)  
        # max = np.max(img)
        # min = np.min(img)
        # # To improve threshold finding, I'm moving the 
        # # underflow and overflow on the pixel spectrum
        # img[img==max]=mean
        # img[img==min]=mean
        # #
        # # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air)
        # #
        # kmeans = KMeans(n_clusters=2).fit(np.reshape(middle,[np.prod(middle.shape),1]))
        # centers = sorted(kmeans.cluster_centers_.flatten())
        # threshold = np.mean(centers)
        # thresh_img = np.where(img<threshold,1.0,0.0)  # threshold the image

        # # First erode away the finer elements, then dilate to include some of the pixels surrounding the lung.  
        # # We don't want to accidentally clip the lung.

        # eroded = morphology.erosion(thresh_img,np.ones([3,3]))
        # dilation = morphology.dilation(eroded,np.ones([8,8]))

        # labels = measure.label(dilation) # Different labels are displayed in different colors
        # label_vals = np.unique(labels)
        # regions = measure.regionprops(labels)
        # good_labels = []
        # for prop in regions:
            # B = prop.bbox
            # if B[2]-B[0]<row_size/10*9 and B[3]-B[1]<col_size/10*9 and B[0]>row_size/5 and B[2]<col_size/5*4:
                # good_labels.append(prop.label)
        # mask = np.ndarray([row_size,col_size],dtype=np.int8)
        # mask[:] = 0

        # #
        # #  After just the lungs are left, we do another large dilation
        # #  in order to fill in and out the lung mask 
        # #
        # for N in good_labels:
            # mask = mask + np.where(labels==N,1,0)
        # mask = morphology.dilation(mask,np.ones([10,10])) # one last dilation

        
        img1=Image.fromarray(templateImg[s1,:,:])

        # img1=Image.fromarray(mask*img)
        
        photo1 = ImageTk.PhotoImage(img1.resize((400,400)))
        pic1_lb = tk.Label(winNew,image=photo1)
        pic1_lb.place(relx=0,rely=0)

def show2(z):
    global templateImg
    global winNew
    global v4
    global photo2


    if v4==1:
        s2=int(z)
        img2=Image.fromarray(templateImg[:,s2,:])
        photo2 = ImageTk.PhotoImage(img2.resize((400,230)))
        pic2_lb = tk.Label(winNew,image=photo2)
        pic2_lb.place(relx=0,rely=0.6)

def show3(z):
    global templateImg
    global winNew
    global v4
    global photo3


    if v4==1:
        s3=int(z)
        img3=Image.fromarray(templateImg[:,:,s3])
        photo3 = ImageTk.PhotoImage(img3.resize((400,230)))
        pic3_lb = tk.Label(winNew,image=photo3)
        pic3_lb.place(relx=0.33,rely=0.6)
def show():
    global templateImg
    global winNew
    global v4
    global photo1
    global photo2
    global photo3

    s1=v1.get()
    s2=v2.get()
    s3=v3.get()

        

    print (s1,s2,s3)
    print (v4)


    if v4==1:
        
        img1=Image.fromarray(templateImg[s1,:,:])
        photo1 = ImageTk.PhotoImage(img1.resize((400,400)))
        pic1_lb = tk.Label(winNew,image=photo1)
        pic1_lb.place(relx=0,rely=0)
        
        img2=Image.fromarray(templateImg[:,s2,:])
        photo2 = ImageTk.PhotoImage(img2.resize((400,230)))
        pic2_lb = tk.Label(winNew,image=photo2)
        pic2_lb.place(relx=0,rely=0.6)
        
        img3=Image.fromarray(templateImg[:,:,s3])
        photo3 = ImageTk.PhotoImage(img3.resize((400,230)))
        pic3_lb = tk.Label(winNew,image=photo3)
        pic3_lb.place(relx=0.33,rely=0.6)        
        
def main():

    filename = filedialog.askdirectory() #获得选择好的文件夹
    global templateImg
    global winNew
    global v4
    global photo1
    global photo2
    global photo3

    v4=0
    
    templateImg = loadSerise(filename,0)
    winNew = tk.Toplevel(w)
    winNew.geometry('1200x750')
    winNew.title('三维显示')
    
    
    

    

    img1=Image.fromarray(templateImg[100,:,:])
    photo1 = ImageTk.PhotoImage(img1.resize((400,400)))
    pic1_lb = tk.Label(winNew,image=photo1)
    pic1_lb.place(relx=0,rely=0)
    
    img2=Image.fromarray(templateImg[:,200,:])
    photo2 = ImageTk.PhotoImage(img2.resize((400,230)))
    pic2_lb = tk.Label(winNew,image=photo2)
    pic2_lb.place(relx=0,rely=0.6)
    
    img3=Image.fromarray(templateImg[:,:,300])
    photo3 = ImageTk.PhotoImage(img3.resize((400,230)))
    pic3_lb = tk.Label(winNew,image=photo3)
    pic3_lb.place(relx=0.35,rely=0.6)

    
    

    
    lb1 = tk.Label(winNew,text='')
    lb1.place(relx=0.40,rely=0.05)
    lb1.config(text='您选择的路径是：'+str(filename))
    text = tk.Text(winNew, width=30, height=20)
    text.place(relx=0.40,rely=0.1)
    text.insert(tk.INSERT, '分析结果是：'+'\n')
    
    # t1=tk.Entry(winNew,width=20,textvariable=v1)
    # t1.place(relx=0.2,rely=0.53,relwidth=0.05,relheight=0.05)
    
    # t2=tk.Entry(winNew,width=20,textvariable=v2)
    # t2.place(relx=0.2,rely=0.9,relwidth=0.05,relheight=0.05)
    # #lb2 = tk.Label(winNew,text='y')
    # #lb2.place(relx=0.4,rely=0.05)
    
    # t3=tk.Entry(winNew,width=20,textvariable=v3)
    # t3.place(relx=0.6,rely=0.9,relwidth=0.05,relheight=0.05)
    # #lb3 = tk.Label(winNew,text='z')
    # #lb3.place(relx=0.6,rely=0.05)
    
    #scl = tk.Scale(winNew,orient="horizontal",length=200,from_=1,to=244,label='x',tickinterval=243,resolution=1,variable=v1,command=show1)
    scl = tk.Scale(winNew,orient="horizontal",length=400,from_=1,to=244,width=5,bd=10,troughcolor='red',fg='blue',resolution=1,variable=v1,command=show1)    
    scl.place(relx=0.0,rely=0.52)
    #sc2 = tk.Scale(winNew,orient="horizontal",length=400,from_=1,to=511,label='y',tickinterval=510,resolution=1,variable=v2,command=show2)
    sc2 = tk.Scale(winNew,orient="horizontal",length=400,from_=1,to=511,width=5,bd=10,troughcolor='yellow',fg='blue',resolution=1,variable=v2,command=show2)
    sc2.place(relx=0.0,rely=0.9)
    #sc3 = tk.Scale(winNew,orient="horizontal",length=400,from_=1,to=511,label='z',tickinterval=510,resolution=1,variable=v3,command=show3)
    sc3 = tk.Scale(winNew,orient="horizontal",length=400,from_=1,to=511,width=5,bd=10,troughcolor='green',fg='blue',resolution=1,variable=v3,command=show3)
    sc3.place(relx=0.33,rely=0.9)

    btClose=tk.Button(winNew,text='关闭',command=winNew.destroy)
    btClose.place(relx=0.9,rely=0.9)
    btfind=tk.Button(winNew,text='裁剪',command=find_frame)
    btfind.place(relx=0.85,rely=0.9)
    btn = tk.Button(winNew,text="绘制立体图",command=show3d)
    btn.place(relx=0.8,rely=0.9)
    
    me=tk.Menu(winNew) 
    winNew.config(menu=me) 
    insesrtmenu=tk.Menu(me) 
    me.add_cascade(label="导入文件",menu=insesrtmenu) 
    insesrtmenu.add_command(label=" 选择文件夹",command=main)
    fmenu=tk.Menu(me) 
    me.add_cascade(label="分析",menu=fmenu) 
    fmenu.add_command(label="显示骨头",command=main) 
    fmenu.add_command(label="分析",command=main) 
    fmenu.add_command(label="分类",command=main)
    fmenu.add_command(label="查询",command=main)
    fmenu1=tk.Menu(me) 
    me.add_cascade(label="设置",menu=fmenu1) 
    fmenu1.add_command(label="显示骨头",command=main) 
    fmenu1.add_command(label="分析",command=main) 

    v4=1

    
    #plt.subplot(224)
    #plot_3d(templateImg, 300)

        
        
    
w=tk.Tk() 
w.geometry('1000x600') 
w.title("智能骨折分析系统") 
l = tk.Label(w, width=50, text='')
l.pack()
#canvas_root = tkinter.Canvas(w,width= 800,height=600)
#im_root =get_image(r'‪D:\keyan\pythongui\Figure_2.png',800,600)
#canvas_root.create_image(400,300,image=im_root)
#canvas_root.pack()
#canvas_root.place(relx=0,rely=0)
wClose=tk.Button(w,text='关闭',command=w.destroy)
wClose.place(relx=0.9,rely=0.9)
dcm_open=tk.Button(w,text='选择文件',command=main)
dcm_open.place(relx=0.82,rely=0.9)
m=tk.Menu(w) 
w.config(menu=m) 
insesrtmenu=tk.Menu(m) 
m.add_cascade(label="导入文件",menu=insesrtmenu) 
insesrtmenu.add_command(label=" 选择文件夹",command=main)

fmenu=tk.Menu(m) 
m.add_cascade(label="分析",menu=fmenu) 
fmenu.add_command(label="文件",command=main) 
fmenu.add_command(label="数量",command=main) 
fmenu.add_command(label="元件",command=main)
fmenu.add_command(label="条件",command=main)
#templateImg=tk.Variable()
v1=tk.Variable()
v2=tk.Variable()
v3=tk.Variable()
v4=tk.Variable()
if v4==1:
    show()
#winNew=tk.Variable()

#tk.mainloop()
if __name__ == "__main__":
    if v4==1:
        show()



