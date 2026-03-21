# Installing a Raspberry Pi to be used as Kiosk

> [!CAUTION]
> This guide covers specific setup for Debian-Trixie based Raspberry Pi OS. It does not work for Debian-Bookworm -- see the [Bookworm guide](install-kiosk-rpi-bookworm.md) if you still use an older OS

> [!TIP]
> The usage of a Raspberry Pi 4 or 5 with at least 2GB of RAM is strongly recommended. Other platforms are not covered by this guide

## Baseconfiguration

Flash an SD-Card with Raspberry Pi OS including the Desktop in the 64bit variant.

Start the Pi, login via SSH and configure the following basics:

  * enable and start ssh(-daemon)
  * Hostname (in the following example this is **bpi1**)
  * IP-address (in the following example this is **10.13.66.31/24**)
  * Default-Gateway (in the following example this is **10.13.66.1**)
  * DNS-Server (in the following example this is **10.13.66.5**)

Then do a reboot and continue with the next section

### Example bash commands for this Section

```bash
sudo su

systemctl enable ssh
systemctl start ssh
echo "bpi1" > /etc/hostname
sed -i -e 's/raspberrypi/bpi1/g' /etc/hosts
nmcli con mod "netplan-eth0" ipv4.addresses 10.13.66.31/24 ipv4.method manual
nmcli con mod "netplan-eth0" ipv4.gateway 10.13.66.1
nmcli con mod "netplan-eth0" ipv4.dns "10.13.66.5"
reboot
```

## raspi-config

Execute `sudo raspi-config` and change the following settings:

  * enable Wayland: `Advanced Options -> Wayland -> Labwc`
  * enable boot to desktop: `System Options -> Boot -> Desktop Desktop GUI`
  * enable auto-login: `System Options -> Auto Login -> No -> OK -> Yes -> OK`
  * set timezone (and keyboard layout): `Localisation Options`

### Alternate way

Instead of using the interactive raspi-config interface, the same changes can be done directly from the commandline:

```bash
sudo raspi-config nonint do_wayland W2

sudo raspi-config nonint do_boot_behaviour B4

sudo raspi-config nonint do_change_timezone Europe/Berlin
```

## Configure Autostart

### Install dependency

install `wtype` for the HideCursor shortcut to take effect:

`sudo apt update && sudo apt install wtype`

### Disable keyring

Chromium likes to have it's passwords saved securely, for a Kiosk this is not needed and quiet anoying. Therefor disable keyring globally like this:

`sudo chmod a-x /usr/bin/gnome-keyring*`

### Configure shortcut to hide cursor

`nano .config/labwc/rc.xml`

place or append the following config:

```
<?xml version="1.0"?>
<labwc_config>
        <keyboard>
                <keybind key="A-W-h">
                <action name="HideCursor" />
                <action name="WarpCursor" x="-1" y="-1" />
                </keybind>
        </keyboard>
</labwc_config>
```

### Configure Chromium to autostart

`nano .config/labwc/autostart`

place or append the following config:

> [!IMPORTANT]
> Replace **your.server.goes.here** with the IP or DNS name of your KioskController
>
> Also replace **bpi1** on each Kiosk by a unique value, to be able to controll multiple Kiosks independently

```
chromium http://your.server.goes.here/?name=bpi1 --kiosk --noerrdialogs --disable-infobars --no-first-run --ozone-platform=wayland --enable-features=OverlayScrollbar --start-maximized --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-kiosk-data" --disable-web-security &
sleep 1 && wtype -M alt -M logo -k h -m alt -m logo
```

### Optional: disable the desktop

To make the startup a bit faster and reduce memory consumption, you can comment out everything in

`sudo nano /etc/xdg/labwc/autostart`

The content should now look like the following:

```
#/usr/bin/lwrespawn /usr/bin/pcmanfm-pi &
#/usr/bin/lwrespawn /usr/bin/wf-panel-pi &
#/usr/bin/kanshi &
#/usr/bin/lxsession-xdg-autostart
```


## Configure NTP Client

It's strongly recommended that all Kiosks use the same (local) NTP server, for the Kiosks beeing able to work in sync (for example executing Screen changes at the same time if the Admin is requesting this)  
The default stack of KioskController serves it's own NTP servers, this is now configured to be used.

Place the following content in `/etc/systemd/timesyncd.conf`

> [!IMPORTANT]
> Replace **your.server.goes.here** with the IP or DNS name of your KioskController

```
[Time]
NTP=your.servername.goes.here
FallbackNTP=0.arch.pool.ntp.org 1.arch.pool.ntp.org 2.arch.pool.ntp.org 3.arch.pool.ntp.org
#RootDistanceMaxSec=5
#PollIntervalMinSec=32
#PollIntervalMaxSec=2048
```

`systemctl restart systemd-timesyncd` reloads the config

## Optional: Configure a VNC-Server

> [!WARNING]
> This might give LAN-Party participants access to the Kiosks-Interface, enable VNC to your own risk

In case you like to be able to remotely login to the graphical desktop, you can start a VNC-Server on the Kiosk Pi. After this you can use TigerVNC or RealVNC to access the desktop directly on port 5900

### enable Server

*Variant A:*  
`sudo raspi-config` -> `Interface Options` -> `VNC`

*Variant B:*  
`sudo raspi-config nonint do_vnc 0` (yes, a value of 0 enables the VNC-Server)

### disable Auth

By default it's now not possible to login to the VNC-Server.  
Edit `/etc/wayvnc/config` and set the vlaue of `enable_auth` to `false`

Now restart the VNC-Server `sudo systemctl restart wayvnc`
