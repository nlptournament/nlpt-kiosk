# Setup PlayerCount fetching from Discord

## Create a Discord Bot

If not already done... Create a Discord-Bot. This Bot is going to life on your Discord-Server and tracks player activities to be read by NLPT-Kiosk.

First open the Discord-Developer-Portal: [https://discord.com/developers/applications](https://discord.com/developers/applications)

Create a "New Application" and give it a name. Configure it as follows:

### Settings->Bot

![settings-bot](img/discord-settings-bot.png)

  * Click `Reset Token` and securely save it away (we need it later on in NLPT-Kiosk Admin-Interface)
  * Enable `Presence Intent`
  * Enable `Server Members Intent`
  * Enable `Message Content Intent`
  * `Save`

### Settings->OAuth2

![settings-oauth-generator](img/discord-settings-oauth-generator.png)
![settings-oauth-permissions](img/discord-settings-oauth-permissions.png)

  * in `OAuth2 URL Generator` section enable `bot`
  * in `Bot Permissions` section enable **nothing**
  * set `Integration Type` to `Guild Install`
  * copy the `Generated URL`
  * paste the copied URL in a new Tab or Window and follow the steps, ensure to select the server (guild) you like to get PlayerCounts from

## Setup within Admin-Interface

  * Open the Admin-Interface **http://<server_addr\>/admin**
  * Login as a admin user
  * Navigate to *User->Settings*
  * Find `discord_bot_token` and enter the saved token from above
  * Hit Save

After this setup the system is connected to Discord and is already fetching playerdata from your server (guild). To show those, create a new Screen:

  * Navigate to Manage *Screens->New*
  * Select `Player Counts - Discord` or `Player Counts - Multi` as template
  * If you like to apply player-filters for this Screen, you can do this with `guild` and `role`
  * The rest of the config is as usual
  * Afterwards you can add this Screen to a Timeline as it is done with other Screens

> [!NOTE]  
> If you like to use player-filters, select a guild first, depending on the selected guild, the frontend requests the available roles from the backend

> [!IMPORTANT]  
> With the `prometheus-endpoint` (can be enabled in *User->Settings*) only the content used by Screens is exported  
> This means: All guild- and role-filter combinations, that are used on Screens are reflected in the exported data. Therefore a game can have multiple entries (with different counts) if it is covered by multiple filters.
