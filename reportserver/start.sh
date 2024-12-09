 #!/bin/bash
# 查询进程
process=`netstat -tulnp | grep ':5050' | awk '{print $7}' | cut -d'/' -f1`
#重启flask服务
# 如果进程存在，则结束该进程
case "$1" in
    start)
        if [[ -n "$process" ]]; then
	    kill $process
            #systemctl start /etc/systemd/system/apitest.service
	   # /usr/local/python3/Python-3.7.9/bin/python3 /usr/local/project/api_test/reportserver/app.py  runserver -h=0.0.0.0 -p=5050 >/usr/local/project/api_test/reportserver/run.log 2>&1 &
	fi
        systemctl start apitest.service
	echo "启动成功"
    ;;
    stop)
       if [[ -n "$process" ]]; then
	    kill $process
	fi
	echo "停止成功"
    ;;
    restart)
        if [[ -n "$process" ]]; then
	    kill $process
            #systemctl start /etc/systemd/system/apitest.service
	    #/usr/local/python3/Python-3.7.9/bin/python3 /usr/local/project/api_test/reportserver/app.py  runserver -h=0.0.0.0 -p=5050 >/usr/local/project/api_test/reportserver/run.log 2>&1 &
	fi
        systemctl start apitest.service
	echo "重启成功"
    ;;
    *)
        echo "输入错误"
esac
