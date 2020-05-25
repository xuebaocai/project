#!/usr/bin/expect

#scp无需输入密码发送文件
#v1.0 by mengjun

# argv 0 filename
# mengjun receive username
# 192.168.153.130 receive ip
# 182333 receive password
set timeout 30

set src_file [lindex $argv 0]
spawn scp $src_file mengjun@192.168.153.130:/home/mengjun
 expect {
 "(yes/no)?"
  {
    send "yes\n"
    expect "*assword:" { send "182333\n"}
  }
 "*assword:"
  {
    send "182333\n"
  }
}
expect "100%"
expect eof

