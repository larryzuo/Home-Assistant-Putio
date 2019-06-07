# Home-Assistant-Putio
The [Home Assistant](https://home-assistant.io) Putio component is a component that downloads all your transfers from [put.io](http://put.io) automatically.

## Prerequisites

This component requires the [Downloader component](https://www.home-assistant.io/components/downloader/). Make sure it is set up correctly and your instance is able to receive [webhooks](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger) else your files won't be downloaded.

## Instructions

1. Download and move the `putio` folder into your `custom_components` directory.

2. Create an OAuth token for the component [here](https://app.put.io/authenticate?client_id=4045). After authorizing the app, the token will be presented in the adress bar.

3. Add the following entry to your `configuration.yaml`:

```yaml
putio: 
  token: OAUTH_TOKEN
```

4. Set `https://YOUR_HOME_ASSISTANT_DOMAIN/api/webhook/putio_transfer_completed` in your [Putio account preferences(Advanced Settings)](https://app.put.io/settings/preferences) as callback url.

After restarting your Home Assistant instance, all future finished Putio transfers will be downloaded automatically to the directory specified by the [Downloader component](https://www.home-assistant.io/components/downloader/) configuration.