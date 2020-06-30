import aiohttp
import datetime
import homeassistant.helpers.config_validation as cv
import logging
import time
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.helpers.entity import Entity


__version__ = '0.1.0'

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_LATITUDE): vol.Coerce(float),
    vol.Optional(CONF_LONGITUDE): vol.Coerce(float),
    vol.Optional(CONF_SCAN_INTERVAL, default=300): cv.time_period,
})

BASE_URL = 'https://yandex.ru/pogoda/front/maps/nowcast-single?lat={lat}&lon={lon}&lang=ru&alert=1'

SUPPORTED_ALERT_TYPES = {'rain', 'noprec'}

ATTR_LAST_UPDATE = 'last_update'
ATTR_RAIN_STATE = 'rain_state'
ATTR_RAIN_STATE_LIST = 'rain_state_list'

RAIN_STATES = ['starts', 'ends', 'noprec', 'still']


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config[CONF_NAME]
    lat = config.get(CONF_LATITUDE, hass.config.latitude)
    lon = config.get(CONF_LONGITUDE, hass.config.longitude)
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    async_add_entities([YandexRainSensor(hass, name, lat, lon, scan_interval)], True)


class YandexRainSensor(Entity):
    def __init__(self, hass, name, lat, lon, scan_interval):
        self.hass = hass
        self._state = None
        self._name = name
        self._lat = lat
        self._lon = lon
        self._scan_interval = scan_interval
        self.attr = {
            ATTR_RAIN_STATE_LIST: RAIN_STATES
        }
        self._update_ts = 0
        _LOGGER.debug(f'Initialized sensor {self._name}')

    async def async_update(self):
        _LOGGER.debug(f'Updating sensor {self._name}...')
        if (time.monotonic() - self._update_ts) >= self._scan_interval.total_seconds():
            try:
                url = BASE_URL.format(lat=self._lat, lon=self._lon)
                async with aiohttp.ClientSession() as client:
                    async with client.get(url) as resp:
                        response = await resp.json()
                        alert = response['alert']
                        _LOGGER.debug(f'Got alert response: {alert}')

                        if alert['type'] not in SUPPORTED_ALERT_TYPES:
                            _LOGGER.warning(f"Got unsupported alert type: {alert['type']}")
                            return

                        self._state = alert.get('title', None)

                        self.attr[ATTR_RAIN_STATE] = alert.get('state', None)
                        updated_ts = alert.get('time')
                        if updated_ts is not None:
                            self.attr[ATTR_LAST_UPDATE] = datetime.datetime.fromtimestamp(updated_ts)
            except Exception as ex:
                _LOGGER.error(f'Could not update {self._name}: {ex}')
        else:
            _LOGGER.debug('Skipping update')

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return 'mdi:weather-pouring'

    @property
    def device_state_attributes(self):
        return self.attr
