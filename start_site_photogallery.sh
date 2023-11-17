#!/bin/sh

### BEGIN INIT INFO
# Provides:     test
# Required-Start:  $remote_fs $syslog
# Required-Stop:   $remote_fs $syslog
# Default-Start:   2 3 4 5
# Default-Stop:   0 1 6
# Short-Description: start test
# Description:    start test
# 放入/etc/init.d文件夹, 随系统自启动进行部署
### END INIT INFO

sudo uwsgi /root/web/PhotoGallery/uwsgi_conf.ini   #uwsgi_conf.xml配置文件的具体位置
exit 0