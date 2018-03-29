# NetworkDeviceBackup
AUTHOR: Tuan Hoang

- This python script backup multiple Cisco Router and Switch configuration
- List of devices is stored in hostlist file
	+ device without s : using telnet
	+ device with s: using ssh
- Syntax:
	./backupconfig.py hostlist (need execute permission such as chmod 700)
	or
	python backupconfig.py hostlist

