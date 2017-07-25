#!/usr/bin/env python
#coding=utf-8

import picamera
from time import sleep
import urllib2
import urllib
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import uniout
import web
import RPi.GPIO as GPIO
import sqlite3
import os

register_openers()
api_key="Your face++ api_key here"
api_secret="Your face++ api_secret here"
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)



urls=(
        "/","index",
        "/config","config",
	"/manage","manage",
	"/setpass","setpass",
	"/opendoor","opendoor",
	"/login","login",
	"/insert","insert",
	"/compare","compare",
	"/index","index"
     )
app=web.application(urls,globals())
session=web.session.Session(app,web.session.DiskStore('sessions'),initializer={'auth':0})

def checkAuth():
    if session.auth == 0:
        raise web.seeother("/config")

def getphoto(path):
        camera=picamera.PiCamera()
        camera.start_preview()
	camera.vflip=False
	sleep(10)
	camera.capture(path)
	camera.stop_preview()
	camera.close()

def getCout(command):
	f=os.popen(command)
	result=f.read()
	f.close()
	return result


def openDoor():
	for i in range(0,20):
		GPIO.setup(7,GPIO.OUT)
		sleep(0.5)

		
class index:
    def GET(self):
                session.auth=0
		try:
			urllib2.urlopen("http://www.baidu.com")
                except:
                        session.auth=1
			raise web.seeother("/config")
		render=web.template.render("templates")
		if web.input().get("set") is not None:
			return render.index(True)
		else:
			return render.index(False)


class config:
	def GET(self):
	        checkAuth()
	        render=web.template.render("templates")
		if web.input().get(set) is not None:
			return render.config(True)
		else:
			return render.config(False)
	def POST(self):
	        checkAuth()
		f=open("/etc/wpa_supplicant/wpa_supplicant.conf","a")
		f.write("network={\nssid=\"%s\"\npsk=\"%s\"\n}"%(web.input().get("ssid"),web.input().get("psk")))
		f.close()
		os.system("sudo service networkmanager restart")
		sleep(10)
		try:
			urllib2.urlopen("http://www.baidu.com")
		except:
			raise web.seeother("/config?set=1")
		else:
			raise web.seeother("/setpass")
			

class login:
	def GET(self):
		render=web.template.render("templates")
		if web.input().get(set) is not None:
			return render.login(False)
		else:
			return render.login(True)
	def POST(self):
		conn=sqlite3.connect("web.db")
		cu=conn.cursor()
		cu.execute("select pass from passes")
		t=cu.fetchall()
                for m in t:
		    if m[0]==web.input().get("pass"):
		        session.auth=0
			raise web.seeother("/manage")
		raise web.seeother("/login?set=1")
			
class manage:
	def GET(self):
	        checkAuth()
		render=web.template.render("templates")
		conn=sqlite3.connect("web.db")
		cu=conn.cursor()
		cu.execute("select address from users")
		t=cu.fetchall()
		print t
		return render.manage(t)

class insert:
	def GET(self):
	        checkAuth()
		try:
			getphoto("temp.jpg")
			conn=sqlite3.connect("web.db")
			cu=conn.cursor()
			cu.execute("select id from users order by id  desc limit 0,1")
			t=cu.fetchall()
                        print "1"
                        if t==[]:
                            address="static/1.jpg"
                        else:
			    address="static/"+str(t[0][0]+1)+".jpg"
			os.system("mv temp.jpg "+address)
			datagen,headers=multipart_encode({"api_key":api_key,"api_secret":api_secret,"image_file":open(address,"rb")})
			request=urllib2.Request("https://api-cn.faceplusplus.com/facepp/v3/detect",datagen,headers)
			res=json.loads(urllib2.urlopen(request).read())
			try:
			        print "2"
				face_token1=res["faces"][0]["face_token"]
				conn=sqlite3.connect("web.db")
				cu=conn.cursor()
				cu.execute("insert into users(address,token) values(?,?)",(address,face_token1,))
				conn.commit()
				print "3"
				return json.dumps({"ans":"success"})
			except Exception,e:
				print res
				print e
				return json.dumps({"ans":"fail"})
		except Exception,e:
			print e
			return json.dumps({"ans":"fail"})

class opendoor:
	def GET(self):
	        checkAuth()
	        web.header("Content-Type","application/json")
		openDoor()
		return json.dumps({"finished":"true"})

class setpass:
	def GET(self):
	        checkAuth()
		render=web.template.render("templates")
		return render.setpass()
	def POST(self):
	        checkAuth()
		conn=sqlite3.connect("web.db")
		cu=conn.cursor()
		cu.execute("INSERT INTO passes(pass) values(?)",(web.input().get("pass"),))
		conn.commit()
		raise web.seeother("manage")

class compare:
	def GET(self):
	        web.header("Content-Type","application/json")
		try:
			getphoto("temp.jpg")
			conn=sqlite3.connect("web.db")
			cu=conn.cursor()
			cu.execute("select token from users")
			t=cu.fetchall()
			flag=False
			for m in t:
				datagen,headers=multipart_encode({"api_key":api_key,"api_secret":api_secret,"face_token1":m[0],"image_file2":open("temp.jpg","rb")})
				request=urllib2.Request("https://api-cn.faceplusplus.com/facepp/v3/compare",datagen,headers)
				ans=urllib2.urlopen(request).read()
				result=json.loads(ans)
				try:
					if result["confidence"]>=80:
						flag=True
						break
					else:
						continue
				except:
					continue
			if flag:
			        openDoor()
				return json.dumps({"ans":"success"})
                        else:
				return json.dumps({"ans":"fail"})
		except Exception,e:
			print e
			return json.dumps({"ans":"fail"})
			
if __name__=="__main__":
    app.run()
