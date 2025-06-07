# Kiosk einrichten

Wie man einen RaspberryPi konfiguriert um ihn als Display für NLPT-Kiosk-Controller zu nutzen

## Grundkonfiguration

SD-Karte mit einem Raspberrypi-OS flashen (inkl Desktop, darf ruhig irgendwas leichtgewichtiges sein). PI booten und Netzwerk konfigurieren.

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
