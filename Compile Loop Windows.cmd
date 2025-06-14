@ECHO OFF

TITLE Impala Auto Compiler

SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

ECHO.
ECHO *** Any impala file in this directory will now be recompiled automatically. *** 
ECHO.
ECHO Don't forget to give yourself write permission in the output folder.
ECHO.

:forever
FOR %%I IN (*.impala) DO (
	SET _source="%%I"
	SET _target="%%~dpnI.gazl"
	SET _dirty=1
	FOR /F "usebackq delims=" %%T IN (`DIR /B /OD %%_source%% %%_target%% ^| more +1`) DO (
		IF /I %%~xT EQU .gazl SET _dirty=0
	)
	IF !_dirty! EQU 1 (
		ECHO Compiling !_source!...
		PikaCmd impala.pika compile !_source! !_target!
	)
)
ping 123.45.67.89 -n 1 -w 100 > nul
GOTO forever
