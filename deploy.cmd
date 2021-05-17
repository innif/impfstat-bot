CALL .\backup-pi-data.cmd
ssh pi@raspberrypi cd ~/impfstat-bot;git pull;sudo reboot now
pause