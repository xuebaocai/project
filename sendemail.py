
import smtplib
from email.mime.text import MIMEText



mailto_list = []
mail_host = "smtp.163.com:25"  # 设置服务器
mail_user = "wo19967307259@163.com"  # 发件用户名
mail_pass = "gyr20150306"  # 口令
debug_level = 0  # 是否开启debug


def send_mail(to_list, sub, content):
    me = mail_user
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.set_debuglevel(debug_level)
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print('except:', e)
        return False


if __name__ == '__main__':
    mailto_list = '13223487828@163.com'
    sub = 'alarm'
    content = 'invasion'
    if send_mail(mailto_list, sub, content):
        print("发送成功")
    else:
        print("发送失败")
