import  tkinter  as  tk   #导入Tkinter
import HP_web as hweb

if __name__=="__main__":
    root=tk.Tk()
    root.title('Tkinter中网页浏览演示') 
    root.geometry('{}x{}+{}+{}'.format(800, 600, 100, 200))
    web=hweb.BrowserFrame(root)
    web.pack(fill=tk.BOTH, expand=1)
    root.mainloop()