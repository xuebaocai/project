
#!/bin/bash

#del file or folder after specified time
#v1.0 by mengjun

#当前时间
timecur=$(date "+%Y-%m-%d %H:%M:%S")

function deleteTimeOutFile(){
	local folderFile=$1
	local timeout=$2
	local type=$3
	if [ -d "$folderFile" ] ; then
		local folderFileList=`ls $folderFile`
		for folderFileOne in $folderFileList
		do
			local folderFileNew=$folderFile$folderFileOne
			
			if [ -d "$folderFileNew" ] ; then
				# 是文件夹
				#echo $(date "+%Y-%m-%d %H:%M:%S")" 文件夹："$folderFileNew
				deleteTimeOutFile $folderFileNew"/" $timeout $type
				if [ "`ls -A $folderFileNew`" = "" ]; then
					# type文件夹是否需要删除  0：不删除  1：删除
					if [ $type -eq 1 ]; then	
						rm -rf $folderFileNew
					fi
				fi
					
			elif [ -f "$folderFileNew" ] ; then  # 是文件
				#echo $(date "+%Y-%m-%d %H:%M:%S")" 文件："$folderFileNew
				local filetimestamp=`stat -c %Y $folderFileNew`  # 文件最后修改时间
				local timestamp=`date +%s`  # 当前系统时间
				local timecha=$[$timestamp - $filetimestamp]
				if [ $timecha -gt $timeout ];then
					rm -rf $folderFileNew
				fi	
			fi

		done	
	fi

}
folderFile0=/home/mengjun/mongo/config/encrypt/ # 路径
timeout0=60 # 单位秒
type0=1 # type文件夹是否需要删除  0：不删除  1：删除
deleteTimeOutFile $folderFile0 $timeout0 $type0
