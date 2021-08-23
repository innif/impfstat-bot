CALL .\backup-pi-data.cmd
ssh pi@RP3 cd ~/impfstat-bot;git pull;sudo reboot now
pause