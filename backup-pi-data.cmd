@echo off
echo Running Backup
rem Extract the hour and minute from the time
set TM=%TIME:~0,2%%TIME:~3,2%
rem Zero-pad the hour if it is before 10am
set TM=%TM: =0%
set BOT-BACKUP-PATH=%date%-%TM%
echo Path: %BOT-BACKUP-PATH%
mkdir "pi-backup/%BOT-BACKUP-PATH%"
scp -r pi@raspberrypi:~/impfstat-bot/impfstat-bot pi-backup/%BOT-BACKUP-PATH%
echo finished Backup