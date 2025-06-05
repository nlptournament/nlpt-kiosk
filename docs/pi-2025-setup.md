# Kiosk einrichten

Wie man einen RaspberryPi konfiguriert um ihn als Display für NLPT-Kiosk-Controller zu nutzen

## Grundkonfiguration

SD-Karte mit einem Raspberrypi-OS flashen (inkl Desktop, darf ruhig irgendwas leichtgewichtiges sein). PI booten und Netzwerk konfigurieren.

WICHTIG!!! : Dran denken im Browser auto-play für videos zu erlauben

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
