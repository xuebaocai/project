#V1.0 by mengjun 2020.10.16
#选择站场及其通道，并标定ROI


from tkinter import *
from PIL import Image, ImageTk
import imageio
import cv2
import tkinter as tk
import tkinter.messagebox
from config import zhangchang,zhangchang_ip_channel
import numpy as np
import publish
import json

class Window(Frame):
    def __init__(self, master=None,pub=None):
        Frame.__init__(self, master)

        self.master = master
        self.pos = []
        self.rect = []
        self.master.title("GUI")
        self.counter = 0
        self.running = 1
        self.zl_lb = None
        self.cl_lb = None
        self.zhanchange_index = None
        self.w, self.h = 640, 480
        self.blank_image = np.zeros((self.h, self.w, 4), np.uint8)
        self.ip = None
        self.channel_num = None
        self.pub = pub

        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Open", command=self.zhanchang_list)
        file.add_command(label="Exit", command=self.client_exit)

        analyze = Menu(menu)
        menu.add_cascade(label="Analyze", menu=analyze)
        analyze.add_command(label="Roi", command=self.regionOfInterest)
        analyze.add_command(label="Check", command=self.main_process)
        analyze.add_command(label="Clear", command=self.clear)

        send = Menu(menu)
        menu.add_cascade(label="Send", menu=send)
        send.add_command(label="absence", command=self.model_absence)
        send.add_command(label="intrude", command=self.model_intrude)

        self.filename = "copy.jpg"
        self.imgSize = Image.open(self.filename)
        self.tkimage = ImageTk.PhotoImage(self.imgSize)


        self.canvas = Canvas(master=root, width=self.w, height=self.h)
        self.canvas.create_image(20, 20, image=self.tkimage, anchor='nw')
        self.canvas.grid(row=200, column=200)

    def zhanchang_list(self):
        # 创建一个空列表
        self.zl_lb = tk.Listbox(self.master)
        self.zl_lb.grid(row=0, column=1)
        # 往列表里添加数据
        for item in zhangchang:
            self.zl_lb.insert("end", item)
        #双击打开channel_list
        self.zl_lb.bind('<Double-Button-1>', self.channel_list)

    def channel_list(self,event):
        self.cl_lb = tk.Listbox(self.master)
        self.cl_lb.grid(row=0, column=2)
        #判断站场选择
        self.zhanchange_index = self.zl_lb.curselection()
        self.zhanchange_index = self.zhanchange_index[0]

        if  self.zhanchange_index == 0:
            for item in zhangchang_ip_channel['下沙']['channel']:
                self.cl_lb.insert("end", item)
        elif self.zhanchange_index == 1:
            for item in zhangchang_ip_channel['屠甸']['channel']:
                self.cl_lb.insert("end", item)

        #双击打开channel_select
        self.cl_lb.bind('<Double-Button-1>', self.channel_select)

    def channel_select(self,event):
        # 判断channel选择
        channel_index = self.cl_lb.curselection()
        zhangchang_num = zhangchang[self.zhanchange_index]
        self.channel_num = zhangchang_ip_channel[zhangchang_num]['channel'][channel_index[0]]
        #ip确定
        self.ip = zhangchang_ip_channel[zhangchang_num]['ip']
        #双击start
        self.cl_lb.bind('<Double-Button-1>', self.show_image(event))

    def model_absence(self):
        #判断model选择
        msg = json.dumps({'sub_ip':self.ip,'polygon_vertex': self.rect})
        self.pub.send_msg(topic='zs/polygonvertex/absence/channel{}/out'.format(self.channel_num),
                          msg = msg)
        self.clear()
        tkinter.messagebox.showinfo('提示', '发送成功')

    def model_intrude(self):
        # 判断model选择
        msg = json.dumps({'sub_ip': self.ip, 'polygon_vertex': self.rect})
        self.pub.send_msg(topic='zs/polygonvertex/boundary_intrude/channel{}/out'.format(self.channel_num),
                          msg=msg)
        self.clear()
        tkinter.messagebox.showinfo('提示', '发送成功')

    def show_image(self,event):
        cap = cv2.VideoCapture('rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(self.ip, self.channel_num))
        ret, frame = cap.read()
        if  cap.isOpened():
            frame = cv2.resize(frame, (self.w, self.h))
            orig_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            final = cv2.add(orig_frame, self.blank_image)
            img = Image.fromarray(final)

            self.tkimage = ImageTk.PhotoImage(img)
            self.canvas.destroy()
            self.canvas = Canvas(master=root, width=self.w, height=self.h)
            self.canvas.create_image(0, 0, image=self.tkimage, anchor='nw')
            self.canvas.grid(row=200, column=200)

        else:
            tkinter.messagebox.showerror('错误', '读取视频流错误')


    def regionOfInterest(self):
        root.config(cursor="plus")
        self.canvas.bind("<Button-1>", self.imgClick)



    def imgClick(self, event):

        if self.counter < 4:
            x = int(self.canvas.canvasx(event.x))
            y = int(self.canvas.canvasy(event.y))
            self.rect.append([x, y])
            self.pos.append(self.canvas.create_line(x - 10, y, x + 10, y, fill="yellow", tags="crosshair"))
            self.pos.append(self.canvas.create_line(x , y-10, x , y+10, fill="red", tags="crosshair"))
            self.counter += 1

        if self.counter == 4:
            # unbinding action with mouse-click
            self.canvas.unbind("<Button-1>")
            root.config(cursor="arrow")
            self.counter = 0

    def main_process(self):
        cap = cv2.VideoCapture('rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(self.ip,self.channel_num))
        while cap.isOpened():
            ret, image = cap.read()
            image = cv2.resize(image,(self.w,self.h))
            points = np.array([self.rect[0],self.rect[1],self.rect[2],self.rect[3]], np.int32)
            cv2.polylines(image, [points], True,(0, 255, 0))
            cv2.imshow('channel_{}'.format(self.channel_num), image)
            if cv2.waitKey(1) & 0xFF == ord('q') :
                break
        cv2.destroyAllWindows()


    def clear(self):
        # 清空边界点
        self.rect.clear()
        for i in self.pos:
            self.canvas.delete(i)

    def client_exit(self):
        exit()


root = Tk()

pub = publish.Publish(host='10.150.38.141')
app = Window(root,pub)
root.geometry('900x700')
root.title("camera_roi")

root.mainloop()
