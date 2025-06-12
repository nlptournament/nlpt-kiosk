# Kiosk einrichten

Wie man einen RaspberryPi konfiguriert um ihn als Display für NLPT-Kiosk-Controller zu nutzen

## Grundkonfiguration

SD-Karte mit einem Raspberrypi-OS flashen (inkl Desktop, darf ruhig irgendwas leichtgewichtiges sein).  
Pi booten und Netzwerk konfigurieren.

```bash
sudo apt update
sudo apt -y install lightdm chromium-browser

sudo raspi-config
```

Auto Login aktivieren: `System Options -> Boot / Auto Login -> Desktop Autologin`  
In `Localisation Options`die Zeitzone und Tastatur setzen  
Über `Interface Options` dann `VNC` den VNC-Server aktivieren

> [!NOTE]
> Es funktioniert nur RealVNC auf der Client-Seite, andere VNC-Viewer beschweren sich über die Rechte

### Alternativ von Kommandozeile

```bash
sudo raspi-config nonint do_change_locale de_DE.UTF-8 UTF-8
sudo raspi-config nonint do_change_timezone Europe/Berlin

sudo raspi-config nonint do_vnc 0  # ja 0 aktiviert es, laut doku

sudo raspi-config nonint do_boot_behaviour B4
```

## Autostart von Chromium

`sudo nano .config/wayfire.ini`

Um die folgenden Zeilen **ergänzen**

```
chromium = chromium-browser http://kiosk.nlpt.network/?name=bpi1 --kiosk --noerrdialogs --disable-infobars --no-first-run --ozone-platform=wayland --enable-features=OverlayScrollbar --start-maximized --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-kiosk-data" --disable-web-security
screensaver = false
dpms = false
```

## Chromium

CORS deaktivieren: `--user-data-dir="/tmp/chrome-dev-data" --disable-web-security`

auto-play für videos zu erlauben : `--autoplay-policy=no-user-gesture-required`

Vollständiger Startbefehl zum testen:

```
chromium-browser http://localhost:4200/?name=testkiosk1 --no-first-run --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-dev-data" --disable-web-security
```

Prod Befehl:

```
chromium-browser http://localhost:4200/?name=testkiosk1 --kiosk --noerrdialogs --disable-infobars --no-first-run --enable-features=OverlayScrollbar --start-maximized --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-dev-data" --disable-web-security
```

## NTP Server einrichten

Der default compose stack bringt einen timeserver mit, es ist sinnvoll alle Kiosks im lokalen Netz auf diesen Zeitserver zu konfigurieren, dass die Zeitabweichungen der Kiosks untereinander möglichst gering gehalten werden und so `synced apply` auch wirklich synchron ist.

`/etc/systemd/timesyncd.conf` editieren

```
[Time]
NTP=your.servername.goes.here
FallbackNTP=0.arch.pool.ntp.org 1.arch.pool.ntp.org 2.arch.pool.ntp.org 3.arch.pool.ntp.org
#RootDistanceMaxSec=5
#PollIntervalMinSec=32
#PollIntervalMaxSec=2048
```

Danach `systemctl restart systemd-timesyncd`oder den Pi neustarten.
