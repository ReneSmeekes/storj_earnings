@ECHO OFF
TITLE StorJ earnings
COLOR F1

SET dataPath=\path\to\storj\data

MKDIR "%TEMP%\storj_earnings"
Powershell.exe -command "(New-Object System.Net.WebClient).DownloadFile('https://raw.githubusercontent.com/ReneSmeekes/storj_earnings/master/earnings.py','%TEMP%\storj_earnings\earnings.py')"
MKDIR "%TEMP%\storj_earnings\storage"
COPY "%dataPath%\bandwidth.db" "%TEMP%\storj_earnings\storage\bandwidth.db" >NUL
COPY "%dataPath%\storage_usage.db" "%TEMP%\storj_earnings\storage\storage_usage.db" >NUL
COPY "%dataPath%\piece_spaced_used.db" "%TEMP%\storj_earnings\storage\piece_spaced_used.db" >NUL
COPY "%dataPath%\reputation.db" "%TEMP%\storj_earnings\storage\reputation.db" >NUL
COPY "%dataPath%\satellites.db" "%TEMP%\storj_earnings\storage\satellites.db" >NUL
COPY "%dataPath%\heldamount.db" "%TEMP%\storj_earnings\storage\heldamount.db" >NUL

PYTHON "%TEMP%\storj_earnings\earnings.py" "%TEMP%\storj_earnings\storage"

RMDIR /S /Q "%TEMP%\storj_earnings"

pause
