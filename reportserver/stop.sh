#!/bin/bash
# 查询进程
process=`netstat -tulnp | grep ':5050' | awk '{print $7}' | cut -d'/' -f1`
#重启flask服务
# 如果进程存在，则结束该进程
if [[ -n "$process" ]]; then
	kill $process
fi

