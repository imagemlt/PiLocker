# PiLocker

## what is it  
This application is a face recognition application build on raspberry pi with webpy and face++ api.



## requires  
* Raspberry Pi with Raspbian  
* Specific camera module for RPi  
* Python with webpy and PiCamera extension  
* Face++ sdk  
> note: this application run on 800x600 screen.  
 

## start  
just type   
```shell
	./PiLocker.py  
```
then the web application will run and you can lauch it with your browser. 
To make the application be accessed after the raspberry pi booted, you should do the following to enable the application run with full-screen chrome browser.  
edit the file:  
```shell
	sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```  
Comment out this line:  
```shell
	@xscreensaver -no-splash
```
Add these lines:  
```shell
	@xset s off @xset -dpms @xset s noblank /usr/bin/chromium --noerrdialogs --kiosk --incognito "http://localhost:8080"
```  
edit the /etc/rc.local, add these lines before the line "exit 0":  
```shell
	cd YOUR_PROJECT_BASE_DIR && python ./PiLocker.py &
```
Then you can enjoy the lock.


