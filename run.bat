@echo off
setlocal enabledelayedexpansion

:: Project Name
set "projectName=install_ubbospike"
set "moduleFile=UbboSpike.py"

:: Temporary files
set "llsp3file=%projectName%.llsp3"
set "manifestFile=manifest.json"
set "projectbodyFile=projectbody.json"
set "iconFile=icon.svg"
set "temp_zip=temp__.zip"

:: Generate icon file
echo Generating "%iconFile%"
set "icon=<svg width="60" height="60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="#D8D8D8" fill-rule="nonzero"><path d="M34.613 7.325H15.79a3.775 3.775 0 00-3.776 3.776v37.575a3.775 3.775 0 003.776 3.776h28.274a3.775 3.775 0 003.776-3.776V20.714a.8.8 0 00-.231-.561L35.183 7.563a.8.8 0 00-.57-.238zm-.334 1.6l11.96 12.118v27.633a2.175 2.175 0 01-2.176 2.176H15.789a2.175 2.175 0 01-2.176-2.176V11.1c0-1.202.973-2.176 2.176-2.176h18.49z"/><path d="M35.413 8.214v11.7h11.7v1.6h-13.3v-13.3z"/></g><path fill="#0290F5" d="M23.291 27h13.5v2.744h-13.5z"/><path fill="#D8D8D8" d="M38.428 27h4.32v2.744h-4.32zM17 27h2.7v2.7H17zM17 31.86h2.7v2.744H17zM28.151 31.861h11.34v2.7h-11.34zM17 36.72h2.7v2.7H17zM34.665 36.723h8.1v2.7h-8.1z"/><path fill="#0290F5" d="M28.168 36.723h4.86v2.7h-4.86z"/></g></svg>"
(
    echo !icon!
) > "%iconFile%"
if errorlevel 1 (
    echo Error: Failed to generate "%iconFile%".
    goto cleanup
)

:: Generate manifest file
echo Generating "%manifestFile%"
(
echo {
echo    "type": "python",
echo    "appType": "llsp3",
echo    "autoDelete": false,
echo    "id": "NSX-0kfbiti_",
echo    "name": "%projectName%",
echo    "slotIndex": 0,
echo    "workspaceX": -155,
echo    "workspaceY": 0,
echo    "zoomLevel": 0.5,
echo    "hardware": {
echo        "python": {
echo            "id": "61620913605406",
echo            "description": "",
echo            "type": "flipper",
echo            "connectionState": 2,
echo            "hubState": {
echo                "programRunning": true
echo            },
echo            "lastConnectedHubId": "61620913605406"
echo        }
echo    },
echo    "state": {
echo        "canvasDrawerOpen": true,
echo        "knowledgeBaseSection": "lls-help-python-spm",
echo        "playMode": "download",
echo        "hasMonitors": false
echo    }
echo }
) > "%manifestFile%"
if errorlevel 1 (
    echo Error: Failed to generate "%manifestFile%".
    goto cleanup
)

:: Generate projectbody
echo Generating "%projectbodyFile%"
generate_projectbody_json.exe "%moduleFile%" > "%projectbodyFile%"
if errorlevel 1 (
    echo Error: Failed to generate "%projectbodyFile%".
    goto cleanup
)

:: Create a temporary ZIP file
echo Generating "%llsp3file%"
PowerShell -Command "Compress-Archive -Path '%iconFile%', '%manifestFile%', '%projectbodyFile%' -DestinationPath '%temp_zip%'"
if not exist "%temp_zip%" (
    echo Error: Failed to create ZIP file.
    goto cleanup
)

:: delete existing manifest
if exist "%llsp3file%" (
	del /f /q "%llsp3file%"
)

:: Rename the ZIP file to .llsp3
rename "%temp_zip%" "%llsp3file%"
if errorlevel 1 (
    echo Error: Failed to rename ZIP to .llsp3.
    goto cleanup
)
echo Done!


:: Define cleanup function
:cleanup
echo Cleaning up...
if exist "%iconFile%" del "%iconFile%"
if exist "%manifestFile%" del "%manifestFile%"
if exist "%projectbodyFile%" del "%projectbodyFile%"
if exist "%temp_zip%" del "%temp_zip%"
pause