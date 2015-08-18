@echo off
setlocal

rem -- Check args -----------------------------------------------------------------
if "%1" == "" goto doArgErrors
if "%2" == "" goto doArgErrors
if "%3" == "" goto doArgErrors
if "%4" == "" goto doArgErrors

rem -- Set Environment Vars -----------------------------------------------------------------
set DS_WEB_URL=https://udserver.mylaptop.com:8443
set JAVACMD=C:\PROGRA~2\Java\jre6\bin\java
set JARFILE=C:\IBM\udclient\udclient\udeploy-client.jar

rem -- Execute -----------------------------------------------------------------

set AUTHTOKEN=%1
set COMP_NAME=%2
set COMP_VER=%3
set COMP_BASEDIR=%4

rem --- run commands--- 

%JAVACMD% -jar "%JARFILE%" -authtoken %AUTHTOKEN% createVersion -component "%COMP_NAME%" -name "%COMP_VER%"
%JAVACMD% -jar "%JARFILE%" -authtoken %AUTHTOKEN% addVersionFiles -component "%COMP_NAME%" -version "%COMP_VER%" -base "%COMP_BASEDIR%"

goto end

rem -- End Execute -----------------------------------------------------------------


:doArgErrors
echo Usage Error: udimportver AUTHTOKEN COMPONENT_NAME COMPONENT_VERSION ARTIFACT_PATH
goto end

:end