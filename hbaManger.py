#-*- coding: utf-8 -*-
## Author               : Mustafa YAVUZ 
## E-mail               : msyavuz@gmail.com
## Version              : 0.2
## Date                 : 19.03.20120
## OS System            : Redhat/Centos 7
## OS User      	    : postgres -> must be
## DB Systems           : Postgresql
## System Requirement   : python 2.6 or above
import os
import sys
import commands
from time import *
import socket
##################PARAMETERS##################
LOG_FILE="hbaManager.log"
SILENT_MODE=False
PG_LOCAL_SERVER_DIR='/pgdata/data/'
PG_REMOTE_SERVER_LIST=[['10.10.10.11','/pgdata/data/'],['10.10.10.12','/pgdata/data/']]
DB_NAME='postgres'
DB_USER='postgres'  ## must be superuser
DB_PASSWORD='********'
DB_PORT='5432'
BIN_DIR='/usr/pgsql-11/bin/'
############################## GENERAL FUNCTION ###########################
def get_datetime():
	my_year=str(localtime()[0])
	my_mounth=str(localtime()[1])
	my_day=str(localtime()[2])
	my_hour=str(localtime()[3])
	my_min=str(localtime()[4])
	my_sec=str(localtime()[5])	
	if(len(str(my_mounth))==1):
		my_mounth="0"+my_mounth		
	if(len(my_day)==1):
		my_day="0"+my_day
	if(len(my_hour)==1):
		my_hour="0"+my_hour
	if(len(my_min)==1):
		my_min="0"+my_min
	if(len(my_sec)==1):
		my_sec="0"+my_sec
	return my_year+"."+my_mounth+"."+my_day+" "+my_hour+":"+my_min+":"+my_sec
def fileAppendWrite(file, writeText):
	try :
		fp=open(file,'ab')
		fp.write('\n'+writeText)
		fp.close()
	except :
		print ('!!! An error is occurred while writing file !!!')
def logWrite(logFile,logText):
	if(SILENT_MODE):
		logText=get_datetime()+' ::: '+logText
		fileAppendWrite(logFile,logText)		
	else:
		print (logText)
		logText=get_datetime()+' ::: '+logText
		fileAppendWrite(logFile,logText)
def validIP(IPaddr):
	try:
		socket.inet_aton(IPaddr)
		return True
	except socket.error:
		return False
############################## AUX FUNCTIONS ##################
def reload_conf(hostIP):
	getStatus,getResponse = commands.getstatusoutput("export PGPASSWORD="+DB_PASSWORD+" ; "+ BIN_DIR+"psql -t -h "+hostIP+" -d "+DB_NAME+" -U "+DB_USER+" -p "+DB_PORT+" -c 'select pg_reload_conf()'")
#	print "status : "+ str (getStatus)
#	print "status : "+ str (getResponse)
	if ( getStatus==0 and getResponse.find('t')>-1 ):
		return True
	else:
		return False
def copy_hba(remoteIP,remoteConfDir): ## OK -> return 0 , Not OK -> return 256
	copy_state=os.system('scp -q -o "StrictHostKeyChecking no" -p '+PG_LOCAL_SERVER_DIR+'pg_hba.conf  postgres@'+remoteIP+':'+remoteConfDir+'pg_hba.conf')
	if ( copy_state==0 ):
		return True
	else:
		return False
def edit_hba(targetDB,userName,clientIP,connType):
		fileAppendWrite(PG_LOCAL_SERVER_DIR+'pg_hba.conf', 'host	'+targetDB+'	'+userName+'	'+clientIP+'/32	'+connType+' 			 ## this record added by hbaManager. Date :'+get_datetime())
#returnVAl=raw_input('\n--------------\n')
############################## AUX FUNCTIONS ##################	

##############################  DECISION PROCESS ##########################
#def hba_manage():
def hba_manage(targetDB,userName,clientIP,connType): ## 
#	targetDB=raw_input('\nPlease Enter Database Name :')
	if( targetDB !=''):
#		userName=raw_input('\nPlease Enter User Name :')
		if( userName !=''):
#			clientIP=raw_input('\nPlease Enter Client IP :')
			if( validIP(str(clientIP))):
#				connType=raw_input('\nPlease Enter Auth Meth. (md5/scram-sha-256/trust) :')
				if( connType=='md5' or connType=='scram-sha-256' or connType=='trust' ):
					edit_hba(targetDB,userName,clientIP,connType)					
					if ( reload_conf("localhost") ):
						logWrite(LOG_FILE,"pg_hba.conf reload succesed on localhost")
					else:
						logWrite(LOG_FILE,"ERROR !!!! while pg_hba.conf reload process on localhost")
					for RemoteHost in PG_REMOTE_SERVER_LIST:
						myResult=copy_hba(RemoteHost[0],RemoteHost[1])
						if ( myResult ):
							logWrite(LOG_FILE,"pg_hba.conf was copied to -> "+RemoteHost[0]+":"+RemoteHost[1])
							if ( reload_conf(RemoteHost[0]) ):
								logWrite(LOG_FILE,"pg_hba.conf reload succesed on ->"+RemoteHost[0])
							else:
								logWrite(LOG_FILE,"ERROR !!!! while pg_hba.conf reload process on ->"+RemoteHost[0])
						else:
							logWrite(LOG_FILE,"ERROR !!! when pg_hba.conf copy to -> "+RemoteHost[0]+":"+RemoteHost[1])
				else:
					logWrite(LOG_FILE,"!!! NOT valid Auth. Type entered\n Auth Meth. must be ->(md5/scram-sha-256/trust) :"+connType)					

			else:
					logWrite(LOG_FILE,"!!! NOT valid IP entered :"+clientIP)
		else:
			logWrite(LOG_FILE,"User Name parameter  canNOT be null !!!")	
	else:
		logWrite(LOG_FILE,"DB Name canNOT be null !!!")
def main():
	try:
#		hba_manage()
		hba_manage(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
	except:
		logWrite(LOG_FILE,"!!! Wrong input : must be that format:\n 'python hbaManager.py [DBName] [userName] [clientIP] [authType(md5/scram-sha-256/trust)]'")
main()