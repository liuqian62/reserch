import os
import re
#import docx
import pandas as pd
import tkinter as tk
#from docx        import Document
from tkinter     import filedialog
#from win32com    import client as wc
#from prettytable import PrettyTable
from openpyxl    import Workbook
from openpyxl    import load_workbook
from PIL import ImageTk,Image

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
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from tkinter import filedialog
import skimage
from skimage import measure, feature



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



    if v4==0:
        plt.close('all')
        #global canvas
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        #plt.imshow(templateImg[20,:,:], cmap='gray')
        plt.imshow(templateImg[5,:,:], cmap='gray')
        plt.axis('off')
    if v4==1:
        s1=int(z)
        plt.close('all')
        #global canvas
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        #plt.imshow(templateImg[20,:,:], cmap='gray')
        plt.imshow(templateImg[s1,:,:], cmap='gray')
        plt.axis('off')


        canvas11=FigureCanvasTkAgg(fig1,winNew)
        canvas11.draw()  #以前的版本使用show()方法，matplotlib 2.2之后不再推荐show（）用draw代替，但是用show不会报错，会显示警告
            #canvas1.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
        canvas11.get_tk_widget().place(relx=0, rely=0, width=350, height=300)

def show2(z):
    global templateImg
    global winNew
    global v4


    if v4==0:
        plt.close('all')
        #global canvas
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        #plt.imshow(templateImg[20,:,:], cmap='gray')
        plt.imshow(templateImg[:,200,:], cmap='gray')
        plt.axis('off')
    if v4==1:
        s1=int(z)
        plt.close('all')
        #global canvas
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        plt.imshow(templateImg[:,s1,:], cmap='gray')
        plt.axis('off')


    canvas22=FigureCanvasTkAgg(fig1,winNew)
    canvas22.draw()
    canvas22.get_tk_widget().place(relx=0.4, rely=0, width=350, height=300)

def show3(z):
    global templateImg
    global winNew
    global v4


    if v4==0:
        plt.close('all')
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        plt.imshow(templateImg[:,:,300], cmap='gray')
        plt.axis('off')
    if v4==1:
        s1=int(z)
        plt.close('all')
        #global canvas
        matplotlib.use('TkAgg') #使用组件
        fig1=plt.figure(1)
        plt.imshow(templateImg[:,:,s1], cmap='gray')
        plt.axis('off')


        canvas33=FigureCanvasTkAgg(fig1,winNew)
        canvas33.draw()
        canvas33.get_tk_widget().place(relx=0, rely=0.5, width=350, height=300)
def show():
    global templateImg
    global winNew
    global fig1
    global fig2
    global fig3
    global fig4

    global canvas11
    global canvas22
    global canvas33
    global canvas44
    global v4

    s1=v1.get()
    s2=v2.get()
    s3=v3.get()

        

    print (s1,s2,s3)
    print (v4)
    plt.close('all')
    #global canvas
    matplotlib.use('TkAgg') #使用组件
    if v4==0:
        fig1=plt.figure(1)
        #plt.imshow(templateImg[20,:,:], cmap='gray')
        plt.imshow(templateImg[100,:,:], cmap='gray')
        #plt.show()
        #best_frame_raw = templateImg[:,220,:]
        #plt.cla()
        
        fig2=plt.figure(2)
        #plt.imshow(best_frame_raw,cmap='gray')
        #plt.imshow(templateImg[:,510,:], cmap='gray')
        plt.imshow(templateImg[:,200,:], cmap='gray')
        #plt.show()
        fig3=plt.figure(3)
        #plt.imshow(templateImg[:,:,510], cmap='gray')
        plt.imshow(templateImg[:,:,300], cmap='gray')
        #plt.show()
        
        fig4=plt.figure(4)
        four= plt.imread(r'C:\Users\Administrator\Desktop\keyan\pythongui\Figure_2.png')
        plt.imshow(four)
        
        canvas11=FigureCanvasTkAgg(fig1,winNew)
        canvas11.draw()  #以前的版本使用show()方法，matplotlib 2.2之后不再推荐show（）用draw代替，但是用show不会报错，会显示警告
            #canvas1.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
        canvas11.get_tk_widget().place(relx=0, rely=0, width=350, height=300)
            
        canvas22=FigureCanvasTkAgg(fig2,winNew)
        canvas22.draw()
        canvas22.get_tk_widget().place(relx=0.4, rely=0, width=350, height=300)
            #canvas2.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
            
        canvas33=FigureCanvasTkAgg(fig3,winNew)
        canvas33.draw()
        canvas33.get_tk_widget().place(relx=0, rely=0.5, width=350, height=300)
            #canvas3.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
            
        canvas44=FigureCanvasTkAgg(fig4,winNew)
        canvas44.draw()
        canvas44.get_tk_widget().place(relx=0.4, rely=0.5, width=350, height=300)
    if v4==1:
        
        fig1=plt.figure(1)
        #plt.imshow(templateImg[20,:,:], cmap='gray')
        plt.imshow(templateImg[s1,:,:], cmap='gray')
        plt.axis('off')
        #plt.show()
        #best_frame_raw = templateImg[:,220,:]
        #plt.cla()
        
        fig2=plt.figure(2)
        #plt.imshow(best_frame_raw,cmap='gray')
        #plt.imshow(templateImg[:,510,:], cmap='gray')
        plt.imshow(templateImg[:,s2,:], cmap='gray')
        plt.axis('off')
        #plt.show()
        fig3=plt.figure(3)
        #plt.imshow(templateImg[:,:,510], cmap='gray')
        plt.imshow(templateImg[:,:,s3], cmap='gray')
        plt.axis('off')
        #plt.show()
        
        fig4=plt.figure(4)
        four= plt.imread(r'C:\Users\Administrator\Desktop\keyan\pythongui\Figure_2.png')
        plt.imshow(four)
        plt.axis('off')


        
        canvas11=FigureCanvasTkAgg(fig1,winNew)
        canvas11.draw()  #以前的版本使用show()方法，matplotlib 2.2之后不再推荐show（）用draw代替，但是用show不会报错，会显示警告
            #canvas1.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
        canvas11.get_tk_widget().place(relx=0, rely=0, width=350, height=300)
            
        canvas22=FigureCanvasTkAgg(fig2,winNew)
        canvas22.draw()
        canvas22.get_tk_widget().place(relx=0.4, rely=0, width=350, height=300)
            #canvas2.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
            
        canvas33=FigureCanvasTkAgg(fig3,winNew)
        canvas33.draw()
        canvas33.get_tk_widget().place(relx=0, rely=0.5, width=350, height=300)
            #canvas3.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
            
        canvas44=FigureCanvasTkAgg(fig4,winNew)
        canvas44.draw()
        canvas44.get_tk_widget().place(relx=0.4, rely=0.5, width=350, height=300)

def main():

    filename = filedialog.askdirectory() #获得选择好的文件夹
    global templateImg
    global winNew
    global v4


    v4=0
    
    templateImg = loadSerise(filename,0)
    winNew = tk.Toplevel(w)
    winNew.geometry('1200x800')
    winNew.title('三维显示')
    
    
    
    print(templateImg.shape)
    
    matplotlib.use('TkAgg') #使用组件
    fig1=plt.figure(1)
    #plt.imshow(templateImg[20,:,:], cmap='gray')
    plt.imshow(templateImg[100,:,:], cmap='gray')
    #plt.show()
    #best_frame_raw = templateImg[:,220,:]
    #plt.cla()
    
    fig2=plt.figure(2)
    #plt.imshow(best_frame_raw,cmap='gray')
    #plt.imshow(templateImg[:,510,:], cmap='gray')
    plt.imshow(templateImg[:,200,:], cmap='gray')
    #plt.show()
    fig3=plt.figure(3)
    #plt.imshow(templateImg[:,:,510], cmap='gray')
    plt.imshow(templateImg[:,:,300], cmap='gray')
    #plt.show()
    
    fig4=plt.figure(4)
    four= plt.imread(r'C:\Users\Administrator\Desktop\keyan\pythongui\Figure_2.png')
    plt.imshow(four)
    
    canvas11=FigureCanvasTkAgg(fig1,winNew)
    canvas11.draw()  #以前的版本使用show()方法，matplotlib 2.2之后不再推荐show（）用draw代替，但是用show不会报错，会显示警告
        #canvas1.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
    canvas11.get_tk_widget().place(relx=0, rely=0, width=350, height=300)
        
    canvas22=FigureCanvasTkAgg(fig2,winNew)
    canvas22.draw()
    canvas22.get_tk_widget().place(relx=0.4, rely=0, width=350, height=300)
        #canvas2.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
        
    canvas33=FigureCanvasTkAgg(fig3,winNew)
    canvas33.draw()
    canvas33.get_tk_widget().place(relx=0, rely=0.5, width=350, height=300)
        #canvas3.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
        
    canvas44=FigureCanvasTkAgg(fig4,winNew)
    canvas44.draw()
    canvas44.get_tk_widget().place(relx=0.4, rely=0.5, width=350, height=300)
    global photo
    #image = Image.fromarray(templateImg[:,:,200])
    photo = ImageTk.PhotoImage(Image.fromarray(templateImg[100,:,:]))
    pic_lb=tk.Label(winNew, image=photo)
    pic_lb.place(relx=0.4, rely=0.5,)


    
    #pic_lb=tk.Label(winNew, image=photo).grid(row=1, column=1)
    #photo.pack()
    
    #canvas4.get_tk_widget().pack(side=tk.TOP, expand = 0.5)
    
    #把matplotlib绘制图形的导航工具栏显示到tkinter窗口上
    #toolbar =NavigationToolbar2Tk(canvas1, winNew) #matplotlib 2.2版本之后推荐使用NavigationToolbar2Tk，若使用NavigationToolbar2TkAgg会警告
    #toolbar.update()
    #canvas1._tkcanvas.place(relx=0.5, rely=0.9)
    
    t1=tk.Entry(winNew,width=20,textvariable=v1)
    t1.place(relx=0.25,rely=0.4,relwidth=0.05,relheight=0.05)
    
    lb1 = tk.Label(winNew,text='')
    lb1.place(relx=0.75,rely=0.05)
    lb1.config(text='您选择的路径是：'+str(filename))
    text = tk.Text(winNew, width=25, height=15)
    text.place(relx=0.75,rely=0.1)
    text.insert(tk.INSERT, '分析结果是：'+'\n')
    

    
    t2=tk.Entry(winNew,width=20,textvariable=v2)
    t2.place(relx=0.63,rely=0.4,relwidth=0.05,relheight=0.05)
    #lb2 = tk.Label(winNew,text='y')
    #lb2.place(relx=0.4,rely=0.05)
    
    t3=tk.Entry(winNew,width=20,textvariable=v3)
    t3.place(relx=0.25,rely=0.9,relwidth=0.05,relheight=0.05)
    #lb3 = tk.Label(winNew,text='z')
    #lb3.place(relx=0.6,rely=0.05)
    
    scl = tk.Scale(winNew,orient="horizontal",length=200,from_=1,to=245,label='x',tickinterval=244,resolution=1,variable=v1,command=show1)
    scl.place(relx=0.05,rely=0.38)
    sc2 = tk.Scale(winNew,orient="horizontal",length=200,from_=1,to=512,label='y',tickinterval=511,resolution=1,variable=v2,command=show2)
    sc2.place(relx=0.45,rely=0.38)
    sc3 = tk.Scale(winNew,orient="horizontal",length=200,from_=1,to=512,label='z',tickinterval=511,resolution=1,variable=v3,command=show3)
    sc3.place(relx=0.05,rely=0.88)

    btClose=tk.Button(winNew,text='关闭',command=winNew.destroy)
    btClose.place(relx=0.9,rely=0.9)
    btn = tk.Button(winNew,text="OK",command=show)
    btn.place(relx=0.8,rely=0.9)
    v4=1

    
    #plt.subplot(224)
    #plot_3d(templateImg, 300)

        
        
    
w=tk.Tk() 
w.geometry('1000x600') 
w.title("智能骨折分析系统") 
l = tk.Label(w, width=50, text='')
l.pack()
canvas_root = tkinter.Canvas(w,width= 800,height=600)
im_root =get_image(r'C:\Users\Administrator\Desktop\keyan\pythongui\Figure_2.png',800,600)
canvas_root.create_image(400,300,image=im_root)
#canvas_root.pack()
canvas_root.place(relx=0,rely=0)
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
fmenu.add_command(label="按文件分类",command=main) 
fmenu.add_command(label="按数量分类",command=main) 
fmenu.add_command(label="按元件分类",command=main)
fmenu.add_command(label="多条件查询",command=main)
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



