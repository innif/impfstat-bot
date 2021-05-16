del -r pi-data
scp -r pi@raspberrypi:~/impfstat-bot/impfstat-bot pi-data
ssh pi@raspberrypi cd ~/impfstat-bot;git pull
scp -r pi-data\impfstat-bot\resources pi@raspberrypi:~/impfstat-bot/impfstat-bot
scp -r pi-data\impfstat-bot\data pi@raspberrypi:~/impfstat-bot/impfstat-bot
ssh pi@raspberrypi sudo reboot now
pause