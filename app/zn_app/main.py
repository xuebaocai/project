#V1.0 by mengjun 2020.10.16
#选择站场及其通道，并标定ROI

from tkinter import *
from PIL import Image, ImageTk
import imageio
import cv2
import tkinter as tk
import tkinter.messagebox
import numpy as np
import publish
import json


# 弹窗1
#mqtt服务器地址修改
class Mqtt_config(tk.Toplevel):
  def __init__(self):
    super().__init__()
    self.title('设置mqtt服务器地址')
    # 弹窗界面
    self.setup_UI()
  def setup_UI(self):
    # 一行（两行两列）
    row1 = tk.Frame(self)
    row1.pack(fill="x")
    tk.Label(row1, text='mqtt_pub：', width=8).pack(side=tk.LEFT)
    self.mqtt_pub = tk.StringVar()
    tk.Entry(row1, textvariable=self.mqtt_pub, width=20).pack(side=tk.LEFT)
    row3 = tk.Frame(self)
    row3.pack(fill="x")
    tk.Button(row3, text="取消", command=self.cancel).pack(side=tk.RIGHT)
    tk.Button(row3, text="确定", command=self.ok).pack(side=tk.RIGHT)
  def ok(self):
    self.userinfo = [self.mqtt_pub.get()] # 设置数据
    self.destroy() # 销毁窗口
  def cancel(self):
    self.userinfo = None # 空！
    self.destroy()

# 弹窗2
#站场及其通道数的增加
class Zhangchang_config(tk.Toplevel):
  def __init__(self):
    super().__init__()
    self.title('增加站场')
    # 弹窗界面
    self.setup_UI()
  def setup_UI(self):
    # 第一行（四行两列）
    row1 = tk.Frame(self)
    row1.pack(fill="x")
    tk.Label(row1, text='站场:', width=8).pack(side=tk.LEFT)
    self.zhanchang_name = tk.StringVar()
    tk.Entry(row1, textvariable=self.zhanchang_name, width=20).pack(side=tk.LEFT)
    #第二行
    row2 = tk.Frame(self)
    row2.pack(fill="x")
    tk.Label(row2, text='站场ip:', width=8).pack(side=tk.LEFT)
    self.zhanchang_ip = tk.StringVar()
    tk.Entry(row2, textvariable=self.zhanchang_ip, width=20).pack(side=tk.LEFT)
    # 第三行
    row3 = tk.Frame(self)
    row3.pack(fill="x", ipadx=1, ipady=1)
    tk.Label(row3, text='通道:', width=8).pack(side=tk.LEFT)
    self.channel = tk.StringVar()
    tk.Entry(row3, textvariable=self.channel, width=20).pack(side=tk.LEFT)
    # 第四行
    row4 = tk.Frame(self)
    row4.pack(fill="x")
    tk.Button(row4, text="取消", command=self.cancel).pack(side=tk.RIGHT)
    tk.Button(row4, text="确定", command=self.ok).pack(side=tk.RIGHT)
  def ok(self):
    self.userinfo = [self.zhanchang_name.get(),self.zhanchang_ip.get(),self.channel.get()] # 设置数据
    self.destroy() # 销毁窗口
  def cancel(self):
    self.userinfo = None # 空！
    self.destroy()

# 弹窗3
#通道数的增减
class Channel_add(tk.Toplevel):
  def __init__(self):
    super().__init__()
    self.title('增加channel')
    # 弹窗界面
    self.setup_UI()
  def setup_UI(self):
    # 一行（两行两列）
    row1 = tk.Frame(self)
    row1.pack(fill="x")
    tk.Label(row1, text='channel：', width=8).pack(side=tk.LEFT)
    self.channel = tk.StringVar()
    tk.Entry(row1, textvariable=self.channel, width=20).pack(side=tk.LEFT)
    row3 = tk.Frame(self)
    row3.pack(fill="x")
    tk.Button(row3, text="取消", command=self.cancel).pack(side=tk.RIGHT)
    tk.Button(row3, text="确定", command=self.ok).pack(side=tk.RIGHT)
  def ok(self):
    self.userinfo = [self.channel.get()] # 设置数据
    self.destroy() # 销毁窗口
  def cancel(self):
    self.userinfo = None # 空！
    self.destroy()

#窗口类
class Window(Frame):
    def __init__(self, master=None,config=None,config_path=None):
        Frame.__init__(self, master)
        '''
        :param master:窗口
        :param config:配置数据
        :param config_path: 配置文件名    

        '''
        self.master = master
        self.pos = []
        self.rect = []
        self.master.title("GUI")
        self.counter = 0
        self.running = 1
        self.zl_lb = None
        self.cl_lb = None
        self.zhanchange_index = None
        self.config_path = config_path
        self.w, self.h = 640, 480
        self.blank_image = np.zeros((self.h, self.w, 4), np.uint8)
        self.ip = None
        self.channel_num = None
        self.zhanchang,self.zhanchang_ip_channel = config['zhanchang'],config['zhanchang_ip_channel']
        self.pub = publish.Publish(host=config['mqtt_pub'])
        menu = Menu(self.master)
        self.master.config(menu=menu)

        #打开、退出菜单
        file = Menu(menu)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Open", command=self.zhanchang_list)
        file.add_command(label="Exit", command=self.client_exit)

        #坐标标定、清除以及视频核对菜单
        analyze = Menu(menu)
        menu.add_cascade(label="Analyze", menu=analyze)
        analyze.add_command(label="Roi", command=self.regionOfInterest)
        analyze.add_command(label="Check", command=self.check_process)
        analyze.add_command(label="Clear", command=self.clear)

        #信息按照不同类型发送菜单
        send = Menu(menu)
        menu.add_cascade(label="Send", menu=send)
        send.add_command(label="absence", command=self.model_absence)
        send.add_command(label="intrude", command=self.model_intrude)

        #mqtt服务器地址，站场的增加菜单
        config_ = Menu(menu)
        menu.add_cascade(label="Config", menu=config_)
        config_.add_command(label="mqtt_pub", command=self.setup_mqtt_config)
        config_.add_command(label="add", command=self.setup_zhanchang_config)

        #刷新菜单
        refresh = Menu(menu)
        menu.add_cascade(label="Refresh", menu=refresh)
        refresh.add_command(label="refresh", command=self.refresh_window)

        self.filename = "logo.jpg"
        self.imgSize = Image.open(self.filename)
        self.tkimage = ImageTk.PhotoImage(self.imgSize)

        self.canvas = Canvas(master=root, width=self.w, height=self.h)
        self.canvas.create_image(20, 20, image=self.tkimage, anchor='nw')
        self.canvas.grid(row=200, column=200)

    #创建站场列表函数
    def zhanchang_list(self):
        # 创建一个空列表
        self.zl_lb = tk.Listbox(self.master)
        self.zl_lb.grid(row=0, column=1)
        # 往列表里添加数据
        for item in self.zhanchang:
            self.zl_lb.insert("end", item)

        #双击打开channel_list
        self.zl_lb.bind('<Double-Button-1>', self.channel_list)

    #创建通道列表函数
    def channel_list(self,event):

        self.cl_lb = tk.Listbox(self.master)
        self.cl_lb.grid(row=0, column=2)
        #判断站场选择
        self.zhanchange_index = self.zl_lb.curselection()
        self.zhanchange_index = self.zhanchange_index[0]
        if self.zhanchange_index >=0:
            for item in set(self.zhanchang_ip_channel[self.zhanchang[self.zhanchange_index]]['channel']):
                self.cl_lb.insert("end", item)

        delButton = tk.Button(self.master, text="删除", command=self.channel_del)
        delButton.grid(row=1, column=2)

        addButton = tk.Button(self.master, text="增加", command=self.channel_add)
        addButton.grid(row=2, column=2)

        #双击打开channel_select
        self.cl_lb.bind('<Double-Button-1>', self.channel_select)

    #确定通道选择函数
    def channel_select(self,event):
        # 判断channel选择
        channel_index = self.cl_lb.curselection()
        zhanchang_num = self.zhanchang[self.zhanchange_index]
        self.channel_num = self.zhanchang_ip_channel[zhanchang_num]['channel'][channel_index[0]]
        #ip确定
        self.ip = self.zhanchang_ip_channel[zhanchang_num]['ip']
        #双击左键start
        self.show_image()

    #删除已经添加好的通道函数
    def channel_del(self):
        # 判断channel选择
        channel_index = self.cl_lb.curselection()
        self.cl_lb.delete(channel_index[0])
        channel_list = []
        for item in self.cl_lb.get(0,self.cl_lb.size()):
            channel_list.append(item)

        self.write_channel_json(channel_list)

    #添加通道函数
    def channel_add(self):
        channel = self.setup_channel_config()
        channel = channel.split(',')
        for item in channel:
            if int(item) not in self.zhanchang_ip_channel[self.zhanchang[self.zhanchange_index]]['channel']:
                self.zhanchang_ip_channel[self.zhanchang[self.zhanchange_index]]['channel'].append(int(item))

        self.zhanchang_ip_channel[self.zhanchang[self.zhanchange_index]]['channel'].sort()
        self.write_channel_json(self.zhanchang_ip_channel[self.zhanchang[self.zhanchange_index]]['channel'])

    #离岗消息发送函数
    def model_absence(self):
        #判断model选择

        msg = json.dumps({'sub_ip':self.ip,'polygon_vertex': self.rect})
        try:
            print('zs/polygonvertex/absence/{}/channel{}/out'.format(self.zhanchang[self.zhanchange_index],self.channel_num))
            self.pub.send_msg(topic='zs/polygonvertex/absence/{}/channel{}/out'.format(self.zhanchang[self.zhanchange_index],self.channel_num),
                              msg = msg)
            tkinter.messagebox.showinfo('提示', '发送成功')
        except:
            tkinter.messagebox.showerror('错误', '发送失败')
        self.clear()

    #入侵消息发送函数
    def model_intrude(self):
        # 判断model选择
        msg = json.dumps({'sub_ip': self.ip, 'polygon_vertex': self.rect})

        try:
            self.pub.send_msg(topic='zs/polygonvertex/boundary_intrude/{}/channel{}/out'.format(self.zhanchang[self.zhanchange_index],self.channel_num),
                          msg=msg)
            tkinter.messagebox.showinfo('提示', '发送成功')
        except:
            tkinter.messagebox.showerror('错误', '发送失败')
        self.clear()

    #视频流读取函数
    def cap_read(self):

        # 殳山 百步 大华摄像头
        if self.ip == "10.164.29.77" or self.ip == "10.164.29.78":

            cap = cv2.VideoCapture(
                'rtsp://admin:admin12345@{}:554/cam/realmonitor?channel={}&subtype=0'.format(self.ip,
                                                                                             self.channel_num))
            if cap.isOpened():
                return cap
            else:
                return None

        # 海康摄像头
        else:
            cap = cv2.VideoCapture(
                'rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(self.ip,
                                                                                self.channel_num))
            if cap.isOpened():
                return cap
            else:
                return None


    #展示读取的第一帧函数
    def show_image(self):
        cap = self.cap_read()
        if cap == None:
            tkinter.messagebox.showerror('错误', '连接超时')


        if cap != None:
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

    #roi调用函数
    def regionOfInterest(self):
        root.config(cursor="plus")
        self.canvas.bind("<Button-1>", self.imgClick)

    #roi画框函数
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

    #实时视频流检查已经画好的roi
    def check_process(self):
        cap = self.cap_read()
        while cap.isOpened():
            ret, image = cap.read()
            image = cv2.resize(image,(self.w,self.h))
            points = np.array([self.rect[0],self.rect[1],self.rect[2],self.rect[3]], np.int32)
            cv2.polylines(image, [points], True,(0, 255, 0))
            cv2.imshow('channel_{}'.format(self.channel_num), image)
            if cv2.waitKey(1) & 0xFF == ord('q') :
                break
        cv2.destroyAllWindows()



    #刷新配置参数
    def refresh_window(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        self.zhanchang, self.zhanchang_ip_channel = config['zhanchang'], config['zhanchang_ip_channel']

    #写入mqtt服务器地址以及站场、通道配置参数
    def write_json(self,*args):
        if len(args) == 1:
            config['mqtt_pub'] = args[0]
            with open(self.config_path, 'w') as f:
                json.dump(config, f, ensure_ascii=False)

        if len(args) == 3:
            #zhangchang添加
            item_list = []
            with open(self.config_path, 'r') as f:
                load_dict = json.load(f)
                zhanchang = load_dict['zhanchang']

            if args[0] not in zhanchang:
                zhanchang.append(args[0])
                load_dict['zhanchang'] = zhanchang

                #zhangchang_ip_channel添加

                channel_num = args[2].split(',')
                channel_list = []
                for num in channel_num:
                    #if int(num) not in load_dict['zhanchang_ip_channel'][args[0]]['channel']:
                    channel_list.append(int(num))
                load_dict['zhanchang_ip_channel'].setdefault('{}'.format(args[0]),
                                                             {'ip': '{}'.format(args[1]), 'channel': channel_list})

            with open(self.config_path, 'w') as f2:
                json.dump(load_dict, f2, ensure_ascii=False)

    #写入通道配置参数
    def write_channel_json(self,channel_list):
        with open(self.config_path, 'r') as f:
            load_dict = json.load(f)
        load_dict['zhanchang_ip_channel'][self.zhanchang[self.zhanchange_index]]['channel'] = channel_list

        with open(self.config_path, 'w') as f2:
            json.dump(load_dict, f2, ensure_ascii=False)

    # 设置弹窗1参数
    def setup_mqtt_config(self):
        # 接收弹窗的数据
        res = self.ask_mqtt_userinfo()
        # print(res)
        if res is None: return
        # 更改参数
        self.mqtt_pub = res[0]
        self.write_json(self.mqtt_pub)


    # 弹窗1
    def ask_mqtt_userinfo(self):
        inputDialog = Mqtt_config()
        self.wait_window(inputDialog)
        return inputDialog.userinfo


    # 设置弹窗2参数
    def setup_zhanchang_config(self):
        # 接收弹窗的数据
        res = self.ask_zhangchang_userinfo()
        # print(res)
        if res is None: return
        # 更改参数
        self.zhanchang_name,self.zhanchang_ip,self.channel = res[0],res[1],res[2]
        self.write_json(self.zhanchang_name,self.zhanchang_ip,self.channel)

    # 弹窗2
    def ask_zhangchang_userinfo(self):
        inputDialog = Zhangchang_config()
        self.wait_window(inputDialog)
        return inputDialog.userinfo

    # 设置弹窗3参数
    def setup_channel_config(self):
        # 接收弹窗的数据
        res = self.ask_channel_userinfo()
        # print(res)
        if res is None: return
        # 更改参数
        self.channel = res[0]
        return self.channel

    # 弹窗3
    def ask_channel_userinfo(self):
        inputDialog = Channel_add()
        self.wait_window(inputDialog)
        return inputDialog.userinfo

    #清空输入的标记点
    def clear(self):
        # 清空边界点
        self.rect.clear()
        for i in self.pos:
            self.canvas.delete(i)

    #窗口退出函数
    def client_exit(self):
        exit()


root = Tk()

#配置参数文件名
config_path = 'config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

#实例化
app = Window(root,config,config_path)
root.geometry('900x700')
root.title("camera_roi")

root.mainloop()
