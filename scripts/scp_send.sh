#!/usr/bin/expect

# argv 0 filename

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

