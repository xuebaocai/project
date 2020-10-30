import tkinter
import tkinter.messagebox
from tkinter import *
import json
import xianlu_main,zhanchang_main

class Login(object):
    def __init__(self, root):
        self.reg = ''
        self.root = root
        self.varName = tkinter.StringVar(value='')
        self.varPwd = tkinter.StringVar(value='')

        self.labelName = tkinter.Label(self.root, text='用户名:', justify=tkinter.RIGHT, width=80)
        self.labelPwd = tkinter.Label(self.root, text='密码:', justify=tkinter.RIGHT, width=80)
        self.entryName = tkinter.Entry(self.root, width=80, textvariable=self.varName)
        self.entryPwd = tkinter.Entry(self.root, width=80, show='*', textvariable=self.varPwd)

        self.buttonOk = tkinter.Button(self.root, text='登录', command=self.login)
        self.buttonCancel = tkinter.Button(self.root, text='取消', command=self.cancel)

        # 单选框
        self.v = tkinter.StringVar()
        self.v.set("站场")
        self.r1 = tkinter.Radiobutton(self.root, text="站场", value="站场", variable=self.v)
        self.r2 = tkinter.Radiobutton(self.root, text="线路", value="线路", variable=self.v)



    def arrange(self):  # 用place函数给各个元素定位
        self.labelName.place(x=75, y=50, width=80, height=20)
        self.labelPwd.place(x=75, y=75, width=80, height=20)
        self.entryName.place(x=140, y=50, width=80, height=20)
        self.entryPwd.place(x=140, y=75, width=80, height=20)
        self.buttonOk.place(x=115, y=145, width=50, height=20)
        self.buttonCancel.place(x=175, y=145, width=50, height=20)
        self.r1.place(x=115, y=100, width=50, height=20)
        self.r2.place(x=165, y=100, width=50, height=20)

    def login(self):
        name = self.entryName.get()
        pwd = self.entryPwd.get()
        if name == 'admin' and pwd == 'admin12345':
            tkinter.messagebox.showinfo('提示', '成功登入')
            self.exchange()
        else:
            tkinter.messagebox.showerror('错误', '用户名或密码错误')

    def cancel(self):
        self.varName.set('')
        self.varPwd.set('')

    def disappear(self):  # 删除页面上的所有架构 但保留root
        self.labelName.destroy()
        self.entryName.destroy()
        self.labelPwd.destroy()
        self.entryPwd.destroy()
        self.buttonOk.destroy()
        self.buttonCancel.destroy()
        self.root.destroy()


    def exchange(self):  # 为实现登录注册页面转化而准备的
        self.disappear()
        if self.v.get() == '站场':
            master = Tk()

            # 配置参数文件名
            config_path = 'zhanchang_config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 实例化
            app = zhanchang_main.Window(master, config, config_path)
            master.geometry('900x700')
            master.title("camera_roi")

            master.mainloop()

        elif  self.v.get() == '线路':
            master = Tk()

            # 配置参数文件名
            config_path = 'xianlu_config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 实例化
            app = xianlu_main.Window(master, config, config_path)
            master.geometry('900x700')
            master.title("camera_roi")

            master.mainloop()


def main():
    root = tkinter.Tk()
    root.title('Login')
    root.geometry('400x400')
    root.resizable(1,0)
    root_login = Login(root)
    root_login.arrange()
    root.mainloop()

if __name__ == '__main__':
    main()

