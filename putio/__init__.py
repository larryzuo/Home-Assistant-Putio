import asyncio
import logging
import json
import requests
import voluptuous as vol
import os

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_TOKEN
from homeassistant.components.downloader import DOMAIN as DOWNLOADER, CONF_DOWNLOAD_DIR, SERVICE_DOWNLOAD_FILE, DOWNLOAD_COMPLETED_EVENT
from .const import DOMAIN
from zipfile import ZipFile

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'https://api.put.io/v2'
TRANSFER_COMPLETED_ID = '{}_transfer_completed'.format(DOMAIN)
CONF_RETRY_ATTEMPTS = 'retry_attempts'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_RETRY_ATTEMPTS, default=5): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    hass.data[DOMAIN] = config[DOMAIN]
    hass.components.webhook.async_register(
    	DOMAIN, 'Putio', TRANSFER_COMPLETED_ID, handle_webhook)

    def handle_event(event):
        _LOGGER.debug('putio finished {}'.format(event.data.get('filename')))
        download_dir = config[DOWNLOADER][CONF_DOWNLOAD_DIR]
        zip_file_path = '{}/{}'.format(download_dir, event.data.get('filename'))
        with ZipFile(zip_file_path, 'r') as zip_file:
            for member in zip_file.infolist():
                filename = os.path.basename(member.filename)
                if filename and filename.endswith(('.mp4', '.mkv', '.avi')):
                    _LOGGER.debug('extracting {}'.format(filename))
                    member.filename = filename
                    zip_file.extract(member, '{}/'.format(download_dir))
                    hass.components.persistent_notification.create('{} has been downloaded'.format(filename),
                        title='Put.io')
            os.remove(zip_file_path)

    hass.bus.async_listen('{}_{}'.format(DOWNLOADER, DOWNLOAD_COMPLETED_EVENT), handle_event)

    return True

async def handle_webhook(hass, webhook_id, request):
    data = dict(await request.post())

    if not data['file_id']:
        _LOGGER.warning(
            'Put.io webhook received an unrecognized payload - content: {}'.format(data)
        )
        return 

    hass.async_create_task(handle_file(hass, webhook_id, data))
    return

async def handle_file(hass, webhook_id, data):
    zip_id = await create_zip_file(hass, data['file_id'])
    download_link = await get_download_link(hass, zip_id)
    download_file(hass, download_link, data['name'])
    return

async def create_zip_file(hass, file_id):
    _LOGGER.debug('zipping: %s', file_id)
    url = '{}/zips/create'.format(BASE_URL)
    data = { 'file_ids': file_id }
    response = await request(hass, 'post', url, { 'status': 'ok'}, data)
    return response['zip_id']

async def get_download_link(hass, zip_id):
    _LOGGER.debug('getting zip: %s', zip_id)
    url = '{}/zips/{}'.format(BASE_URL, zip_id)
    response = await request(hass, 'get', url, { 'status': 'ok', 'zip_status': 'done' })
    return response['url']

def download_file(hass, url, filename):
    data = { 'url': url, 'filename': '{}.zip'.format(filename), 'overwrite': 'true' }
    asyncio.run_coroutine_threadsafe(
        hass.services.async_call(DOWNLOADER, SERVICE_DOWNLOAD_FILE, data, blocking=True), hass.loop)

async def request(hass, method, url, conditions, data=None):
    headers = { 
        'accept': 'application/json', 
        'Authorization': 'Bearer {}'.format(hass.data[DOMAIN][CONF_TOKEN]), 
        'Content-Type': 'application/x-www-form-urlencoded' 
    }
    for i in range(hass.data[DOMAIN][CONF_RETRY_ATTEMPTS]):
        _LOGGER.debug('Attempt: {}'.format(i))
        if i > 0:
            await asyncio.sleep(30)

        if method == 'get':
            response = requests.get(url, headers=headers)
        elif method == 'post':
            response = requests.post(url, data=data, headers=headers)
        else:
            return None

        _LOGGER.debug(response.status_code)
        if response.status_code == 200:
            json = response.json()
            _LOGGER.debug('Attempt: {} - {}'.format(i, json))

            conditions_passed = True
            for key, value in conditions.items():
                if json[key].lower() != value.lower():
                    conditions_passed = False
                    break
            
            if conditions_passed:
                _LOGGER.debug('Attempt: {} - passed'.format(i))
                return json

        _LOGGER.warning(
            'Put.io file could not be downloaded: {}'.format(json)
        )
        return