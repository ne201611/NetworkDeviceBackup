#!/usr/bin/python
#coding:utf-8
#python2.7下运行正常
import sys, os, telnetlib, csv, paramiko, subprocess
import datetime, time, socket

#####VARIABLE#####
logfile="/home/ceadmin/script/success.log"
errorlogfile="/home/ceadmin/script/error.log"
tftproot="/tftproot/ConfigurationArchive"
telnetport=23
telnettimeout=6
readtimeout=6
#####END OF VARIABLE######

#check open port
def checkport(host,port):
	proc=subprocess.Popen(["nmap","-p",port,host, "| grep",port],stdout=subprocess.PIPE)
#	proc=subprocess.Popen(['nmap','-p',port,host,'| grep',port,'| awk','{print $2}'],stdout=subprocess.PIPE)

#	for line in proc.communicate()[0].split('\n'):
	


#function to get config using ssh
def getconfigbyssh(host,username,password,enablepass):
	try:
		conn=paramiko.SSHClient()
		conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		conn.connect(host,username=username,password=password,look_for_keys=False,allow_agent=False)
		shell=conn.invoke_shell()
		time.sleep(2)
#		shell.send("\n")
		sshoutput=shell.recv(50000)
#		print sshoutput
		if sshoutput[-1:]==">":
#			print sshoutput
			shell.send("enable\n")
			time.sleep(1)
			shell.send(enablepass+"\n")
#			shell.recv(1000)
		shell.send("terminal length 0\n")
		shell.send("show run\n")
		time.sleep(4)
		sshoutput=shell.recv(60000)
	except KeyboardInterrupt:
		print("Stopping...")
		sys.exit(0)
	except:
		sshoutput = "Error: "+str(sys.exc_info()[1])
	return sshoutput

#function to get config using telnet 
def getconfigbytelnet(host,username,password,enablepass):
	try:
		tn = telnetlib.Telnet()
		tn.open(host,telnetport,telnettimeout)
		tn.read_until("Username:",readtimeout)
		tn.write(username+"\n")
		tn.read_until("Password:",readtimeout)
		tn.write(password+"\n")
		output=tn.expect([">"],readtimeout)
		#print output
		if output[0] == 0:
			tn.write("enable\n")
			time.sleep(1)
			tn.write(enablepass+"\n")
		tn.write("terminal length 0"+"\n")
		tn.write("sh run"+"\n")
		tn.write("exit"+"\n")
		telnetoutput=tn.read_all()
	except KeyboardInterrupt:
		print("Stopping...")
		sys.exit(0)
	except:
#	except socket.error as e:
		telnetoutput= "Error: "+str(sys.exc_info()[1])
	return telnetoutput

#function write config to file
def writeconfigtofile(config,filename,group,date):
	try:
		if not os.path.exists(tftproot+"/"+group+"/"+date):
			os.makedirs(tftproot+"/"+group+"/"+date)
		fp=open(tftproot+"/"+group+"/"+date+"/"+filename,"w")
		fp.write(config)
		fp.close()
		#success
		return 1
	except:
		print("Some error {0}".format(sys.exc_info()[1]))
		#failure
		return 0

#function write log to log file
def writelogtofile(msg,filename):
	try:
		fp=open(filename,"a")
		fp.write("{0}\n".format(msg))
		fp.close()
	except:
		print("Some error {0}".format(sys.exc_info()[1]))


def main():

	if len(sys.argv) != 2:
		print("Usage: {} <device file>".format(sys.argv[0]))
		sys.exit(1)
	try:
		#Read devices file 
		csvfile=sys.argv[1]
		srcfile = open(csvfile,"rt")
		reader = csv.DictReader(srcfile)

		#Log Starting Backup
		startbackup=datetime.datetime.now()
		msg = "\n" + 20*"#"+" "+str(startbackup)+" STARTING BACKUP "+ 20*"#"
		writelogtofile(msg,logfile)
	except:
		msg = str(datetime.datetime.now())+": "+str(sys.exc_info()[1])
		print(msg)
		writelogtofile(str(sys.exc_info()[1]),logfile)
		sys.exit(1)


	#run through list of devices to get config
	for row in reader:
		if row["Type"][:1]  != "#":
			now = datetime.datetime.now()
			configfile = "%s.%.i-%.2i-%.2i.%.2i:%.2i:%.2i" % (row["Name"],now.year,now.month,now.day,now.hour,now.minute,now.second)

			if row["Type"] == "s":
				output = getconfigbyssh(row["Host"],row["Username"],row["Password"],row["Enable"])
			else:
				output = getconfigbytelnet(row["Host"],row["Username"],row["Password"],row["Enable"])
			date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
			if output[:5] == "Error" or output[:4] == "Stop" :
#				now = datetime.datetime.now()

				msg = "{0}: {1}: {2}: ".format(row["Name"],row["Host"],output)
				print(msg)
				writelogtofile(msg,logfile)
			elif writeconfigtofile(output,configfile,row["Group"],date):
				msg = "{0}: {1}: Successful!".format(row["Name"],row["Host"])
				print(msg)
				writelogtofile(msg,logfile)
	
	#Log Backup Done
	stopbackup=datetime.datetime.now()
	msg = 20*"#" + " " + str(stopbackup) + " BACKUP DONE in "+ str(stopbackup-startbackup) + " " + 20*"#"
	writelogtofile(msg,logfile)
	#close CSV File
	srcfile.close()

if __name__ =='__main__':
	main()
