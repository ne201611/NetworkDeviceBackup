# NetworkDeviceBackup
AUTHOR: Tuan Hoang

- This python script backups configuration of multiple Cisco Routers and Switches
- List of devices is stored in hostlist file:
	+ device without s : using telnet
	+ device with s: using ssh
- Syntax:
	./backupconfig.py hostlist (need execute permission such as chmod 700)
	or
	python backupconfig.py hostlist

