# Kiosk einrichten

Wie man einen RaspberryPi konfiguriert um ihn als Display für NLPT-Kiosk-Controller zu nutzen

## Grundkonfiguration

SD-Karte mit einem Raspberrypi-OS flashen (inkl Desktop, am besten das 64bit Standart Image).  

Pi starten, per SSH einloggen und folgende Befehle absetzen, danach einen Neustart

```
sudo su

echo "bpi1" > /etc/hostname
sed -i -e 's/raspberrypi/bpi1/g' /etc/hosts
nmcli con mod "Wired connection 1" ipv4.addresses 10.13.66.31/24 ipv4.method manual
nmcli con mod "Wired connection 1" ipv4.gateway 10.13.66.1
nmcli con mod "Wired connection 1" ipv4.dns "10.13.66.5"
reboot
```

## Kiosk-Konfiguration (automatisiert)

Es gibt hier im Repository ein Ansible Playbook, dass die Einrichtung der Beamer-Pi's automatisch erledigt.  
Entweder man hat Ansible global auf dem Rechner installiert (zB via `pip install ansible`) oder man hat ein `venv` im Arbeitsverzeichnis des Repository, dann kann es auch per `pip install -r pisetup.txt` installiert werden, bzw wurde bereits installiert bei der Dev-Setup einrichtung via `pip install -r requirements.txt`.

**Zuvor** müssen die Schritte aus der Grundkonfiguration erledigt worden sein.

Dann einfach ins Verzeichnis `ansible` gehen und `ansible-playbook pisetup.yml` ausführen.  
Dies bitte solange machen bis alle Tasks ein `ok` gemeldet haben und keiner mehr mit `changed` abschließt. Die Pi's rebooten sich während der Prozedur durchaus mehrfach.

## Kiosk-Konfiguration (per Hand)

Wer zu viel Zeit hat und die Einrichtung per Hand machen möchte.

### RaspberryPi OS Konfig

```bash
sudo raspi-config
```

Wayland aktivieren: `Advanced Options -> Wayland -> Wayfire`  
Auto Login aktivieren: `System Options -> Boot / Auto Login -> Desktop Autologin`  
In `Localisation Options`die Zeitzone setzen  
Über `Interface Options` dann `VNC` den VNC-Server aktivieren

> [!NOTE]
> Per default kann man sich nicht auf dem VNC-Server einloggen, und das ist auch ok so, da er nur für den Notfall gedacht ist.  
> Zum aktivieren in der datei `/etc/wayvnc/config` den Wert für `enable_auth` auf `false`setzen und `sudo systemctl restart wayvnc`  
> Auf client Seite wurde TigerVNC, RealVNC sollte eigl auch gehen (VNC-Port: 5900)

#### Alternativ von Kommandozeile

```bash
sudo raspi-config nonint do_wayland W2

sudo raspi-config nonint do_boot_behaviour B4

sudo raspi-config nonint do_change_timezone Europe/Berlin

sudo raspi-config nonint do_vnc 0  # ja 0 aktiviert es
```

### Autostart von Chromium

`sudo nano .config/wayfire.ini`

folgende Sektionen ergänzen bzw erstellen

```
[core]
plugins = autostart hide-cursor

[autostart]
chromium = chromium-browser http://kiosk.mgmt.nlpt.network/?name=bpi1 --kiosk --noerrdialogs --disable-infobars --no-first-run --ozone-platform=wayland --enable-features=OverlayScrollbar --start-maximized --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-kiosk-data" --disable-web-security
screensaver = false
dpms = false
```

### NTP Server einrichten

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

## Chromium Extra Infos

Werden nicht zur Einrichtung gebraucht, aber nützlich während Entwicklung und zur Gedachtnisstütze

CORS deaktivieren: `--user-data-dir="/tmp/chrome-dev-data" --disable-web-security`

auto-play für videos zu erlauben : `--autoplay-policy=no-user-gesture-required`

Startbefehl zum testen:

```
chromium-browser http://localhost:4200/?name=testkiosk1 --no-first-run --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-dev-data" --disable-web-security
```
