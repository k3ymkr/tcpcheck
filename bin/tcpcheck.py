#!/usr/bin/env python

#Include networking, system, regular expressions, time and datetime
import socket,sys,re,time,datetime,argparse,random


#Make a new class to handle the socket state
class SocketState:

	#This is the create method fo the class.  It expects a string like "host:port"
	def __init__(self,host):
		#RE to divide hostname and port
		m=re.match("(.*?):(\d+)",host)
		try:
			#If we make it through here, we're defining host and port in the object
			self.host=m.group(1)
			self.port=int(m.group(2))
		except:
			#Something went wrong (Likely a bad string passed in.  Raise an error
			raise SocketCheckInvalidPort
		#state holds if it's up or down.  0 = down, 1 = up and -1 = undefined
		self.state=-1

		#This array keeps track of all the state changes.
		self.changes=[]


	#This method does the check itself.  It creates a socket and if it does so, it return 1.  Otherwise 0
	def tcpcheckconnect(self):
		try:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(2)
			s.connect((self.host,self.port))
			s.close
			return 1
		except socket.error:
			return 0


	#This method just makes a string to print the last status and how long it lasted.
	def getprintchange(self,state,outage):
		status=('down','up')
		s="It was %s for %d seconds"%(status[state],outage)
		return s

	#Return the last string in the array that has the display info for the last change
	def getprintlaststate(self):
		if len(self.changes) >0:
			return self.changes[len(self.changes)-1][2]
		else:
			return ""
	
	#What to do when we print the object.  We print the current state and the last change
	def __str__(self):
		status=('down','up')
		ret="Current state is %s at %s\n"%(status[self.state],datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		ret=ret+self.getprintlaststate()
		return ret
		
	#Return the state.
	def getstate(self):
		return self.state
		
	#This is the main function called.  This does a check and sets the status using the other class methods
	def tcpcheck(self):
		cstate=self.tcpcheckconnect()
		status=('down','up')
		if cstate != self.state:
			now=datetime.datetime.now()
			if self.state != -1:
				self.changes.append([self.state,(now-self.timechange).seconds,""])
				self.changes[len(self.changes)-1][2]=self.getprintchange(self.changes[len(self.changes)-1][0],self.changes[len(self.changes)-1][1])
				self.state=cstate
				self.timechange=now
			else:
				self.state=cstate
				self.timechange=now

				
		



if __name__ == "__main__":
	ap=argparse.ArgumentParser(description='Health validator',usage="Usage: %s [-w] [-p port] host"%(sys.argv[0]),)
	ap.add_argument('-w','--watch',help="Watch Mode", action="store_true")
	ap.add_argument('-p','--port',type=int,help="TCP Port",required=True)
	ap.add_argument('host')
	args=ap.parse_args()

	hostname="%s:%d"%(args.host,args.port)
	s=SocketState(hostname)
	if args.watch:
		while True:
			pstate=s.getstate()
			s.tcpcheck()
			if pstate != s.getstate():
				print s
				print ""
			time.sleep(5)
	else:
		while 1 != s.getstate():
			s.tcpcheck()
			if s.getstate() == 0:
				time.sleep(5)
	print s


