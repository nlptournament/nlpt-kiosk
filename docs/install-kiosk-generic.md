# Setup a Kiosk on generic Hardware

In essence a Kiosk is just a browser displayed in fullscreen mode, therefor you can use any hardware you like, but there are some consideration you should take into account.

## Hardware

Hardware wise there is not much to consider. A decently new PC or Laptop is going to be fine. The amount of RAM souldn't be to small as browsers tend to use a lot of it, I would say 4 GB on Linux and 8GB on windows should e fine. Also, if you are going to use video Screens, Hardware support for H.264 and H.265 codec is kind of a must.

## Software

On the software side, you should care about the following settings:

  * disable screensaver
  * disable standby
  * enable options to hide the mouse, when browser is in fullscreen
  * disable toast/notifications
  * disable translation questions
  * disable menubar, or let them disapear in the background
  * configure the machine to use the NTP server of Kiosk-Controller (recommended for all Kiosks to have the exact same time)
  * I recomend chromium to be used as the browser, see the next section

## Chromium Infos

For Kiosks it's recomended to disable some "security" features in Chromium for a smooth experience. (video and stream Screens can get stuck, if those features aren't disabled)

disable CORS: `--user-data-dir="/tmp/chrome-dev-data" --disable-web-security`

allow auto-play for videos: `--autoplay-policy=no-user-gesture-required`

recommended Chromium startcommand for Kiosks:

```
chromium-browser http://your.server.goes.here/?name=bpi1 --kiosk --noerrdialogs --disable-infobars --no-first-run --enable-features=OverlayScrollbar --start-maximized --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-kiosk-data" --disable-web-security
```

> [!IMPORTANT]
> Replace **your.server.goes.here** with the IP or DNS name of your KioskController
>
> Also replace **bpi1** on each Kiosk by a unique value, to be able to controll multiple Kiosks independently
