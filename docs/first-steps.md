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

## Create a Timeline

Now, let's display some information on our Kiosks.  
In essesnce we need a Screen (which is kind of an information bucket), then we have to arrage one (or multiple) Screens onto a TimelineTemplate and finally apply a TimelineTemplate to a Kiosk to get a Timeline that can be displayed.

The Screen needs to be defined first. Open *Manage Screens*, click the plus and fill out the following information:

  * Description: hi
  * Template: Plain Text
  * text: Hello World
  * text_color: red

Hit save and close the *Screen Manager*  
Next we need to create a TimelineTemplate, that contains the **hi** Screen.  
Open *Manage Timelines* and click the plus. The textbox on top sets the description for the TimelineTemplate, let's name it **first timeline**. Now click the plus and select **hi**. click the save icon and close *Timelines Manager*

Finally expand *other Timelines* on **kioskA**, hit the plus and select **first timeline**. This now created a Timeline from the TimelineTemplate and assinged it to **kioskA**. But the Kiosk still doesn't show *Hello World*.
That is because you have to pick a Timeline to be the active one for a Kiosk. To do so, click the screen icon besides the Timeline you like to activate, now hit the save icon on top of the Kiosk card. The Timeline jumps from *other Timelines* to the top of the Kiosk and the real Kiosk should now show *Hello World*

Now also apply the same TimelineTemplate to **kioskB** and activate the resulting Timeline. Both Kiosks should now display *Hello World*

## Make a Timeline that does someting

It's nice to have some text displayed on the Kiosk, but now we want to make it a bit more dynamic.

If you don't already, you should get yourself the iconic [Gandalf gif](https://images.steamusercontent.com/ugc/436073184353221196/D2F0B7F99370F71CC6E6593A658BB11B05177070/?imw=5000&imh=5000&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false) just save it anywhere on your computer.  
Next we upload it to the KioskController, for this purpose we create a Media element. Open *Manage Media*, click the plus and fill the information as follows:

  * Description: Gandalf
  * Type: animated image
  * Storage: internal S3 storage
  * Upload: select the saved gif from your computer

Click save and close the *Media Manager*  
Now we need a Screen, that uses this Media: *Manage Screens* -> plus -> and fill out:

  * Description: Gandalf
  * Template: Background Image
  * Duration: 5s
  * image: Gandalf
  * -> Save

This time, don't close *Screen Manager*, we need two more Screens, the first one is:

  * Description: anno
  * Template: Announcements
  * Duration: 5s

And the second one:

  * Description: let's go
  * Template: Plain Text
  * Duration: 5s
  * text: let's have some fun

Nice, we do now have three new Screens, let's add them to a new TimelineTemplate. You could name it **funTL** and the order of the Screens should be (from left to right) `let's go`, `Gandalf` and `anno`

> [!TIP]
> If you added the Screens in the wrong order to the TimelineTemplate, you can adjust this by using the arrows below the Screens while editing the TimelineTemplate. (Also there is an X to remove the Screen from the TimelineTemplate)

Add the new TimelineTemplate as Timelines to both Kiosks, but do not apply them as displayed. Instead just select both Timelines as next Timeline (screen icon) on both Kiosk and click *Synced Apply->Selected Timelines* in the menu.
You should see, it takes a moment, that both Kiosks start the new Timeline at the same time. As the name reveals, *Synced Apply* is meant to be used, if you have multiple Kiosks that should work in sync.

Rgarding this sync feature, one little trick at the end:  
If you have some kind of rotation, and multiple Kiosks in the same room, you can set each Kiosk (or to be more correct, each Timeline) to start each Timeline at a different Screen, but all using the same TimelineTemplate. First apply **first Timeline** as displayed on both Kiosks (active Timelines can't be edited) now expand *other Timelines* on **kioskA** and click the pencil icon (edit) for Timeline **funTL**, now move the slider below the Screens between `let's go` and `Gandalf`, and click the save icon on the Timeline (only do this for **kioskA**) do a *Synced Apply* for **funTL** on both Kiosks. You should now see, that **kioskA** starts it rotation with `Gandalf` and **kioskB** starts at `let's go`

## Tutorial completed

And now it's up to you, explore the Admin-Interface and create your own awsome Kiosk Timelines.

If you like to learn more about the different ScreenTemplates and how to use them, go: [here](screens/discord-playercount.md)

> [!NOTE]
> remember to disable **mock_anno** in the Settings, as you are now done with this tutorial
