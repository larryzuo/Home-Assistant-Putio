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

### Configuration

| Parameter | Default | Description |
|:---:|:---:|---|
| token | none| Your Put.io OAuth token |                                                                                                                                      
| accepted_file_types | [] | Only accepted file types will be extracted. By default all file types are accepted. |
| retry_attempts | 5 | Number of retry attempts if the download fails. Between each attempt, there is a 30s delay. |

The following config example will only extract .mp4 and .mkv files and discard all other file types:

```yaml
putio: 
  token: OAUTH_TOKEN
  accepted_file_types: ['.mp4', '.mkv']
```