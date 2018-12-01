import logging
from datetime import timedelta

from cozypy.client import CozytouchClient
from cozypy.constant import DeviceType, DeviceState
from cozypy.exception import CozytouchException

from homeassistant.components.climate import ClimateDevice, SUPPORT_TARGET_TEMPERATURE_HIGH, \
    SUPPORT_TARGET_TEMPERATURE_LOW, SUPPORT_OPERATION_MODE, SUPPORT_ON_OFF
from homeassistant.components.water_heater import SUPPORT_TARGET_TEMPERATURE, SUPPORT_AWAY_MODE
from homeassistant.const import TEMP_CELSIUS
from homeassistant.util import Throttle

logger = logging.getLogger("cozytouch.climate")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    if "userId" not in config or "userPassword" not in config:
        raise CozytouchException("Bad configuration")
    client = CozytouchClient(config.get("userId"), config.get("userPassword"))
    setup = client.get_setup()
    devices = []
    for heater in setup.heaters:
        devices.append(CozytouchThermostat(heater))

    logger.info("Found %d thermostat" % len(devices))

    add_devices(devices)



SUPPORT_FLAGS_HEATER = (SUPPORT_ON_OFF|SUPPORT_TARGET_TEMPERATURE_HIGH|SUPPORT_TARGET_TEMPERATURE_LOW|SUPPORT_TARGET_TEMPERATURE|SUPPORT_OPERATION_MODE|SUPPORT_AWAY_MODE)

DEFAULT_TIME_OFFSET = 7200

class CozytouchThermostat(ClimateDevice):
    """Representation a Netatmo thermostat."""

    def __init__(self, heater):
        """Initialize the sensor."""
        self.heater = heater
        self._state = None
        self._target_temperature = None
        self._away = None
        self._current_operation = "auto"

    @property
    def operation_list(self):
        return self.heater.operation_list


    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATER

    @property
    def name(self):
        """Return the name of the sensor."""
        return "%s %s" % (self.heater.place.name, self.heater.name)

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.heater.temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.heater.comfort_temperature

    @property
    def current_operation(self):
        """Return the current state of the thermostat."""
        return self.heater.operation_mode
    

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self._away

    def set_operation_mode(self, operation_mode):
        """Change operation mode."""
        pass

    def turn_away_mode_on(self):
        """Turn away on."""
        pass

    def turn_away_mode_off(self):
        """Turn away off."""
        pass

    def set_temperature(self, **kwargs):
        """Set new target temperature"""
        pass

    @Throttle(timedelta(seconds=60))
    def update(self):
        logger.info("Update thermostat %s" % self.name)
        for sensor in self.heater.sensors:
            sensor.update()
