#!/usr/bin/env python3

"""

simple server usage monitoring, writing json to stdout.

usage: nohup python3 monitor_usage.py 3 > /var/log/usage.log &

"""

import sys
import psutil
import json
import time
import subprocess

try:
    interval = int(sys.argv[1])
except IndexError:
    interval = 1

disk_bytes_read_last = disk_bytes_write_last = 0
net_bytes_read_last = net_bytes_write_last = 0
iowait_last = 0

while True:
    disk = psutil.disk_io_counters()
    disk_bytes_read, disk_bytes_write = disk.read_bytes, disk.write_bytes
    net = psutil.net_io_counters()
    net_bytes_read, net_bytes_write = net.bytes_recv, net.bytes_sent
    iowait = psutil.cpu_times().iowait
    disks = [d.mountpoint for d in psutil.disk_partitions()]
    disks_usage = [psutil.disk_usage(d) for d in disks]
    disks_used = sum(d.used for d in disks_usage)
    disks_total = sum(d.total for d in disks_usage)
    usage = json.dumps({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'cache_percent': round(psutil.virtual_memory().cached / psutil.virtual_memory().total * 100, 1),
        'slab_percent': round(psutil.virtual_memory().slab / psutil.virtual_memory().total * 100, 1),
        'swap_percent': psutil.swap_memory().percent,
        'disk_percent': round((disks_used / disks_total * 100), 2),
        'iowait_percent': round((iowait - iowait_last) / psutil.cpu_count() * 100, 1),
        'net_read_mb_s': '{:,}'.format(int((net_bytes_read - net_bytes_read_last) / 1024 / 1024)),
        'net_write_mb_s': '{:,}'.format(int((net_bytes_write - net_bytes_write_last) / 1024 / 1024)),
        'disk_read_mb_s': '{:,}'.format(int((disk_bytes_read - disk_bytes_read_last) / 1024 / 1024)),
        'disk_write_mb_s': '{:,}'.format(int((disk_bytes_write - disk_bytes_write_last) / 1024 / 1024)),
        'lsof': '{:,}'.format(int(subprocess.check_output('lsof | wc -l', shell=True).decode())),
        'net_fds': '{:,}'.format(len(psutil.net_connections())),
        'pids': '{:,}'.format(len(psutil.pids())),
    })
    print(usage)
    time.sleep(interval)
    net_bytes_read_last, net_bytes_write_last = net_bytes_read, net_bytes_write
    disk_bytes_read_last, disk_bytes_write_last = disk_bytes_read, disk_bytes_write
    iowait_last = iowait
