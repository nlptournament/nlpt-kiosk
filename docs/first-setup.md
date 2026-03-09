# First setup (a Walktrough over the basic functionality)

After you installed and started your instance of KioskController, like described in the [install guide](./install-controller.md) you should now start by logging in to the Admin-Interface.

In your browser navigate to `http://<ip-of-controller\>/admin`, you will get a login promt, enter **admin** as the username and the default password **password**

The first thing you should do is changeing your password, you can do this via the menu *User->Change Password*

In case you want to change your username, go to *User->Manage User*, hit the pencil icon, change **admin** to whatever username you like, and click the save icon.  
BTW: In the *User Manager* you can create new users, change their passwords, grant them admin privileges or set their default interface to be the [Streamer-Interface](./streamer-interface.md)

## The System Settings

Navigating to *User->Settings* you can change a lot of different system settings, be aware that some are able to cause problems if misconfigured,
but I hope the descriptions give you a good idea of what to expect by a specific setting.

For the purpose of this demonstration we are going to enable some mockup data, to get some real looking Screens onto our first Kiosk.  
Scroll down to the bottom of *Settings Manager* and tick **mock_anno** then hit **Save**

> [!NOTE]
> You should never enable mockup-data in production, these options are just useful for development (or this demonstration)
>
> Remember to turn of **mock_anno** after you are done with this tutorial!

## Connect a Kiosk

If you like you can now setup a [Raspberry Pi based](./install-kiosk-rpi.md) or [generic Hardware](./install-kiosk-generic.md) Kiosk and connect it to your Controller.  
But, for the purpose of this tutorial, you can also use a second browser-tab or -window. Yes, a Kiosk is nothing more than a browser displaying a website (in fullscreen).

> [!NOTE]
> If you don't like to setup a hardware Kiosk for now, just oben a new browser-window and navigate to: `http://<ip-of-controller\>/?name=kioskA`
>
> The last part of the URL (**kioskA** in this case) defines the uniqe identifier for a Kiosk, you should avoid to use the same identifier on two Kiosks, to be able to control them separately

If the connection to the controller is successful, you should see a message in your Kiosk telling *awaiting data from server*.

Back at the Admin-Interface you see a card, that the Kiosk is requesting access. Accept this request and the card changes it's content to control the Kiosk.  
You now have a first (common) Kiosk added to your controller.

> [!NOTE]
> Common Kiosks (indicated by the filled circle in the upper left corner) are available to (and controllable by) all logged in users. This can be changed in the edit-dialog of the Kiosk.

> [!TIP]
> If you want to block access requests for new Kiosk, go to *User->Settings* and untick **new_kiosks**
>
> This can be useful, after you are done setting up all Kiosks and want to avoid trolls to spam your dashboard with access requests ;)

For the purpose of this demo we now create a second Kiosk. This time we don't let the Kiosk request the access, we just define (create) it.  
Navigate to *User->Create Kiosk*, in the dialog enter the name **kioskB**, keep the other settings untouched and click **Save**. A second Kiosk appeared on your dashboard (this time it's a private one).  
With this method it's possible to predefine all Kiosk during setup, without having the hardware on hand. Later just ensure the Kiosk names are used as identifier on your real Kiosks.

> [!IMPORTANT]
> For the rest of this demo I assume you have two Kiosks, named **kioskA** and **kioskB**, defined
