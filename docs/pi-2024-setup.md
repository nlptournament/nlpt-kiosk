# Kiosk einrichten

Wie man einen RaspberryPi konfiguriert um ihn am Beamer zu nutzen.

## Grundkonfiguration

SD-Karte mit einem Raspberrypi-OS flashen (inkl Desktop, darf ruhig irgendwas leichtgewichtiges sein). PI booten und Netzwerk konfigurieren.

`sudo raspi-config`

Auto Login aktivieren: `System Options -> Boot / Auto Login -> Desktop Autologin`  
In `Localisation Options`die Zeitzone und Tastatur setzen  
Über `Interface Options` dann `VNC` den VNC-Server aktivieren

> [!NOTE]
> Es funktioniert nur RealVNC auf der Client-Seite, andere VNC-Viewer beschweren sich über die Rechte


## Low-Power Warning entfernen

Rechtsklick auf die Taskbar `Add/Remove Panel Elements` In der Liste nach `Batterie` suchen, markieren und entfernen


## Autostart von Chromium

`sudo vim /etc/xdg/autostart/kiosk.desktop`

```
[Desktop Entry]
Name=Kiosk
Exec=chromium-browser https://nlpt.online/beamer-dashboard?token=beamer http://tas.nlpt.network/de/start-countdown http://monitoring.nlpt.network/d/ddxibf5aiitj4f/playercount?orgId=2&refresh=5s&kiosk --kiosk --noerrdialogs --disable-infobars --no-first-run --enable-features=OverlayScrollbar --start-maximized
Terminal=false
Type=Application
```


# Automatisches weiterschalten der Tabs

`vim /home/pi/switchtab.sh`

```
#!/bin/bash

sleep 30

export DISPLAY=:0.0
export XAUTHORITY="/home/pi/.Xauthority"

xdotool mousemove 1920 1080

while true; do
  xdotool key "ctrl+Tab"
  xdotool mousemove 1919 1080
  xdotool mousemove 1920 1080
  sleep 30
done
```

```
chmod 755 /home/pi/switchtab.sh
```

`sudo vim /etc/systemd/system/switchtab.service`

```
[Unit]
Description=SwitchTab

[Service]
Type=exec

Restart=always
RestartSec=5

ExecStart=/home/pi/switchtab.sh
WorkingDirectory=/home/pi
KillSignal=SIGINT

StandardInput=null
SyslogIdentifier=SwitchTab

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl enable switchtab
```
