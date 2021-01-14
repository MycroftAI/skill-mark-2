# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import astral
import time
import arrow
from pytz import timezone
from datetime import datetime

from mycroft.configuration.config import LocalConf, USER_CONFIG, Configuration
from mycroft.messagebus.message import Message
from mycroft.util import get_ipc_directory
from mycroft.util.log import LOG
from mycroft.util.parse import normalize
from mycroft import MycroftSkill, intent_handler

import os
import subprocess

import pyaudio
from threading import Thread, Lock


def compare_origin(m1, m2):
    origin1 = m1.data["__from"] if isinstance(m1, Message) else m1
    origin2 = m2.data["__from"] if isinstance(m2, Message) else m2
    return origin1 == origin2


class RestingScreen:
    """Implementation of functionallity around resting screens.

    This class handles registration and override of resting screens,
    encapsulating the system.
    """

    def __init__(self, bus, gui, log, settings):
        self.bus = bus
        self.gui = gui
        self.log = log
        self.settings = settings

        self.screens = {}
        self.override_idle = None
        self.next = 0  # Next time the idle screen should trigger
        self.lock = Lock()
        self.override_set_time = time.monotonic()

        # Preselect Time and Date as resting screen
        self.gui["selected"] = self.settings.get("selected", "Time and Date")
        self.gui.set_on_gui_changed(self.save)

    def on_register(self, message):
        """Handler for catching incoming idle screens."""
        if "name" in message.data and "id" in message.data:
            self.screens[message.data["name"]] = message.data["id"]
            self.log.info("Registered {}".format(message.data["name"]))
        else:
            self.log.error("Malformed idle screen registration received")

    def save(self):
        """Handler to be called if the settings are changed by the GUI.

        Stores the selected idle screen.
        """
        self.log.debug("Saving resting screen")
        self.settings["selected"] = self.gui["selected"]
        self.gui["selectedScreen"] = self.gui["selected"]

    def collect(self):
        """Trigger collection and then show the resting screen."""
        self.bus.emit(Message("mycroft.mark2.collect_idle"))
        time.sleep(1)
        self.show()

    def set(self, message):
        """Set selected idle screen from message."""
        self.gui["selected"] = message.data["selected"]
        self.save()

    def show(self):
        """Show the idle screen or return to the skill that's overriding idle."""
        self.log.debug("Showing idle screen")
        screen = None
        if self.override_idle:
            self.log.debug("Returning to override idle screen")
            # Restore the page overriding idle instead of the normal idle
            self.bus.emit(self.override_idle[0])
        elif len(self.screens) > 0 and "selected" in self.gui:
            # TODO remove hard coded value
            self.log.info("Showing Idle screen for " "{}".format(self.gui["selected"]))
            screen = self.screens.get(self.gui["selected"])

        self.log.info(screen)
        if screen:
            self.bus.emit(Message("{}.idle".format(screen)))

    def restore(self, _=None):
        """Remove any override and show the selected resting screen."""
        if self.override_idle and time.monotonic() - self.override_idle[1] > 2:
            self.override_idle = None
            self.show()

    def stop(self):
        if time.monotonic() > self.override_set_time + 7:
            self.restore()

    def override(self, message=None):
        """Override the resting screen.

        Arguments:
            message: Optional message to use for to restore
                     the expected override screen after
                     another screen has been displayed.
        """
        self.override_set_time = time.monotonic()
        if message:
            self.override_idle = (message, time.monotonic())

    def cancel_override(self):
        """Remove the override screen."""
        self.override_idle = None


class Mark2(MycroftSkill):
    """
    The Mark2 skill handles much of the gui activities related to Mycroft's
    core functionality. This includes showing "speaking" faces as well as
    more complicated things such as switching to the selected resting face
    and handling system signals.

    # TODO move most things to enclosure / HAL. Only voice interaction should
      reside in the Skill.
    """

    def __init__(self):
        super().__init__("Mark2")

        self.settings["auto_brightness"] = False
        self.settings["use_listening_beep"] = True

        self.has_show_page = False  # resets with each handler
        self.override_animations = False
        self.resting_screen = None

    def initialize(self):
        """Perform initalization.

        Registers messagebus handlers and sets default gui values.
        """
        self.resting_screen = RestingScreen(self.bus, self.gui, self.log, self.settings)

        enclosure_info = self.config_core.get("enclosure", {})

        self.brightness_dict = self.translate_namedvalues("brightness.levels")
        self.gui["volume"] = 0

        # Prepare GUI Viseme structure
        self.gui["viseme"] = {"start": 0, "visemes": []}

        try:
            # Handle network connection events
            self.add_event("mycroft.internet.connected", self.handle_internet_connected)
            self.add_event("system.wifi.setup.hotspot_activated", self.handle_wifi_setup_started)
            self.add_event("system.wifi.setup.network_selection", self.handle_wifi_setup_network_selection)
            self.add_event("system.wifi.setup.connected", self.handle_wifi_setup_connected)

            # Handle the 'busy' visual
            self.bus.on("mycroft.skill.handler.start", self.on_handler_started)

            self.bus.on("recognizer_loop:sleep", self.on_handler_sleep)
            self.bus.on("mycroft.awoken", self.on_handler_awoken)
            self.bus.on("enclosure.mouth.reset", self.on_handler_mouth_reset)
            self.bus.on("recognizer_loop:audio_output_end", self.on_handler_mouth_reset)
            self.bus.on("enclosure.mouth.viseme_list", self.on_handler_speaking)
            self.bus.on("gui.page.show", self.on_gui_page_show)
            self.bus.on("gui.page_interaction", self.on_gui_page_interaction)

            self.bus.on("mycroft.skills.initialized", self.reset_face)
            self.bus.on("mycroft.mark2.register_idle", self.resting_screen.on_register)

            self.add_event("mycroft.mark2.reset_idle", self.resting_screen.restore)
            # TODO move resting screen to Enclosure
            # TODO consolidate bus message format
            # - this message is set to be consistent with a handler below.
            self.add_event("mycroft.device.show.idle", self.resting_screen.show)

            # Handle device settings events
            self.add_event("mycroft.device.settings", self.handle_device_settings)

            # Use Legacy for QuickSetting delegate
            self.gui.register_handler(
                "mycroft.device.settings", self.handle_device_settings
            )
            self.gui.register_handler(
                "mycroft.device.settings.homescreen",
                self.handle_device_homescreen_settings,
            )
            self.gui.register_handler(
                "mycroft.device.settings.ssh", self.handle_device_ssh_settings
            )
            self.gui.register_handler(
                "mycroft.device.settings.reset",
                self.handle_device_factory_reset_settings,
            )
            self.gui.register_handler(
                "mycroft.device.settings.update", self.handle_device_update_settings
            )
            self.gui.register_handler(
                "mycroft.device.settings.restart", self.handle_device_restart_action
            )
            self.gui.register_handler(
                "mycroft.device.settings.poweroff", self.handle_device_poweroff_action
            )
            self.gui.register_handler(
                "mycroft.device.settings.wireless", self.handle_show_wifi_screen_intent
            )
            self.gui.register_handler(
                "mycroft.device.show.idle", self.resting_screen.show
            )

            # Handle idle selection
            self.gui.register_handler(
                "mycroft.device.set.idle", self.resting_screen.set
            )

            # System events
            self.add_event("system.reboot", self.handle_system_reboot)
            self.add_event("system.shutdown", self.handle_system_shutdown)

            # Show loading screen while starting up skills.
            # self.gui['state'] = 'loading'
            # self.gui.show_page('all.qml')

            # Collect Idle screens and display if skill is restarted
            self.resting_screen.collect()
        except Exception:
            LOG.exception("In Mark 2 Skill")

        # Update use of wake-up beep
        self._sync_wake_beep_setting()

        self.settings_change_callback = self.on_websettings_changed

    ###################################################################
    # System events
    def handle_system_reboot(self, message):
        self.speak_dialog("rebooting", wait=True)
        subprocess.call(["/usr/bin/systemctl", "reboot"])

    def handle_system_shutdown(self, message):
        subprocess.call(["/usr/bin/systemctl", "poweroff"])

    ###################################################################
    # Idle screen mechanism

    def reset_face(self, message):
        """Triggered after skills are initialized.

        Sets switches from resting "face" to a registered resting screen.
        """
        time.sleep(1)
        self.resting_screen.collect()


    def stop(self, message=None):
        """ Clear override_idle and stop visemes. """
        self.log.info("Stop received")
        self.resting_screen.stop()
        self.gui["viseme"] = {"start": 0, "visemes": []}
        return False

    def shutdown(self):
        # Gotta clean up manually since not using add_event()
        self.bus.remove("mycroft.skill.handler.start", self.on_handler_started)
        self.bus.remove("recognizer_loop:sleep", self.on_handler_sleep)
        self.bus.remove("mycroft.awoken", self.on_handler_awoken)
        self.bus.remove("enclosure.mouth.reset", self.on_handler_mouth_reset)
        self.bus.remove("recognizer_loop:audio_output_end", self.on_handler_mouth_reset)
        self.bus.remove("enclosure.mouth.viseme_list", self.on_handler_speaking)
        self.bus.remove("gui.page.show", self.on_gui_page_show)
        self.bus.remove("gui.page_interaction", self.on_gui_page_interaction)
        self.bus.remove("mycroft.mark2.register_idle", self.on_register)

    #####################################################################
    # Manage "busy" visual

    def on_handler_started(self, message):
        handler = message.data.get("handler", "")
        # Ignoring handlers from this skill and from the background clock
        if "Mark2" in handler:
            return
        if "TimeSkill.update_display" in handler:
            return

    def on_gui_page_interaction(self, message):
        """ Reset idle timer to 30 seconds when page is flipped. """
        self.log.info("Resetting idle counter to 30 seconds")
        self.start_idle_event(30)

    def on_gui_page_show(self, message):
        if "mark-2" not in message.data.get("__from", ""):
            # Some skill other than the handler is showing a page
            self.has_show_page = True

            # If a skill overrides the animations do not show any
            override_animations = message.data.get("__animations", False)
            if override_animations:
                # Disable animations
                self.log.info("Disabling all animations for page")
                self.override_animations = True
            else:
                self.log.info("Displaying all animations for page")
                self.override_animations = False

            # If a skill overrides the idle do not switch page
            override_idle = message.data.get("__idle")
            if override_idle is True:
                # Disable idle screen
                self.log.info("Cancelling Idle screen")
                self.cancel_idle_event()
                self.resting_screen.override(message)
            elif isinstance(override_idle, int) and override_idle is not False:
                self.log.info(
                    "Overriding idle timer to" " {} seconds".format(override_idle)
                )
                self.resting_screen.override(None)
                self.start_idle_event(override_idle)
            elif message.data["page"] and not message.data["page"][0].endswith(
                "idle.qml"
            ):
                # Check if the show_page deactivates a previous idle override
                # This is only possible if the page is from the same skill
                self.log.info("Cancelling idle override")
                if override_idle is False and compare_origin(
                    message, self.override_idle[0]
                ):
                    # Remove the idle override page if override is set to false
                    self.resting_screen.cancel_override()
                # Set default idle screen timer
                self.start_idle_event(30)

    def on_handler_mouth_reset(self, message):
        """ Restore viseme to a smile. """
        pass

    def on_handler_sleep(self, message):
        """ Show resting face when going to sleep. """
        self.gui["state"] = "resting"
        self.gui.show_page("all.qml")

    def on_handler_awoken(self, message):
        """ Show awake face when sleep ends. """
        self.gui["state"] = "awake"
        self.gui.show_page("all.qml")

    def on_handler_complete(self, message):
        """ When a skill finishes executing clear the showing page state. """
        handler = message.data.get("handler", "")
        # Ignoring handlers from this skill and from the background clock
        if "Mark2" in handler:
            return
        if "TimeSkill.update_display" in handler:
            return

        self.has_show_page = False

        try:
            if self.hourglass_info[handler] == -1:
                self.enclosure.reset()
            del self.hourglass_info[handler]
        except Exception:
            # There is a slim chance the self.hourglass_info might not
            # be populated if this skill reloads at just the right time
            # so that it misses the mycroft.skill.handler.start but
            # catches the mycroft.skill.handler.complete
            pass

    #####################################################################
    # Manage "speaking" visual

    def on_handler_speaking(self, message):
        """Show the speaking page if no skill has registered a page
        to be shown in it's place.
        """
        self.gui["viseme"] = message.data
        if not self.has_show_page:
            self.gui["state"] = "speaking"
            self.gui.show_page("all.qml")
            # Show idle screen after the visemes are done (+ 2 sec).
            time = message.data["visemes"][-1][1] + 5
            self.start_idle_event(time)

    #####################################################################
    # Manage resting screen visual state
    def cancel_idle_event(self):
        """Cancel the event monitoring current system idle time."""
        self.resting_screen.next = 0
        self.cancel_scheduled_event("IdleCheck")

    def start_idle_event(self, offset=60, weak=False):
        """Start an event for showing the idle screen.

        Arguments:
            offset: How long until the idle screen should be shown
            weak: set to true if the time should be able to be overridden
        """
        with self.resting_screen.lock:
            if time.monotonic() + offset < self.resting_screen.next:
                self.log.info("No update, before next time")
                return

            self.log.info("Starting idle event")
            try:
                if not weak:
                    self.resting_screen.next = time.monotonic() + offset
                # Clear any existing checker
                self.cancel_scheduled_event("IdleCheck")
                time.sleep(0.5)
                self.schedule_event(
                    self.resting_screen.show, int(offset), name="IdleCheck"
                )
                self.log.info("Showing idle screen in " "{} seconds".format(offset))
            except Exception as e:
                self.log.exception(repr(e))

    #####################################################################
    # Manage network connection including wifi setup

    def handle_internet_connected(self, message):
        """ System came online later after booting. """
        self.enclosure.mouth_reset()

    def handle_wifi_setup_started(self, message):
        """Provide instructions for setting up wifi."""
        text = self.translate('device.wifi.setup.started')
        self.speak_dialog(text)
        self.gui.show_text(text)

    def handle_wifi_setup_network_selection(self, message):
        """Prompt user to select network and login."""
        text = self.translate('device.wifi.setup.network.selection')
        self.speak_dialog(text)
        self.gui.show_text(text)

    def handle_wifi_setup_connected(self, message):
        """Wifi setup complete, network is connected."""
        text = self.translate('device.wifi.setup.complete')
        self.speak_dialog(text)
        self.gui.show_text(text)

    #####################################################################
    # Web settings

    def on_websettings_changed(self):
        """ Update use of wake-up beep. """
        self._sync_wake_beep_setting()

    def _sync_wake_beep_setting(self):
        """ Update "use beep" global config from skill settings. """
        config = Configuration.get()
        use_beep = self.settings.get("use_listening_beep", False)
        if not config["confirm_listening"] == use_beep:
            # Update local (user) configuration setting
            new_config = {"confirm_listening": use_beep}
            user_config = LocalConf(USER_CONFIG)
            user_config.merge(new_config)
            user_config.store()
            self.bus.emit(Message("configuration.updated"))

    #####################################################################
    # Brightness intent interaction

    def percent_to_level(self, percent):
        """Converts the brigtness value from percentage to a
        value the Arduino can read

        Arguments:
            percent (int): interger value from 0 to 100

        return:
            (int): value form 0 to 30
        """
        return int(float(percent) / float(100) * 30)

    def parse_brightness(self, brightness):
        """Parse text for brightness percentage.

        Arguments:
            brightness (str): string containing brightness level

        Returns:
            (int): brightness as percentage (0-100)
        """

        try:
            # Handle "full", etc.
            name = normalize(brightness)
            if name in self.brightness_dict:
                return self.brightness_dict[name]

            if "%" in brightness:
                brightness = brightness.replace("%", "").strip()
                return int(brightness)
            if "percent" in brightness:
                brightness = brightness.replace("percent", "").strip()
                return int(brightness)

            i = int(brightness)
            if i < 0 or i > 100:
                return None

            if i < 30:
                # Assmume plain 0-30 is "level"
                return int((i * 100.0) / 30.0)

            # Assume plain 31-100 is "percentage"
            return i
        except Exception:
            return None  # failed in an int() conversion

    def set_screen_brightness(self, level, speak=True):
        """Actually change screen brightness.

        Arguments:
            level (int): 0-30, brightness level
            speak (bool): when True, speak a confirmation
        """
        # TODO CHANGE THE BRIGHTNESS
        if speak:
            percent = int(float(level) * float(100) / float(30))
            self.speak_dialog("brightness.set", data={"val": str(percent) + "%"})

    def _set_brightness(self, brightness):
        # brightness can be a number or word like "full", "half"
        percent = self.parse_brightness(brightness)
        if percent is None:
            self.speak_dialog("brightness.not.found.final")
        elif int(percent) == -1:
            self.handle_auto_brightness(None)
        else:
            self.auto_brightness = False
            self.set_screen_brightness(self.percent_to_level(percent))

    @intent_handler("brightness.intent")
    def handle_brightness(self, message):
        """Intent handler to set custom screen brightness.

        Arguments:
            message (dict): messagebus message from intent parser
        """
        brightness = message.data.get("brightness", None) or self.get_response(
            "brightness.not.found"
        )
        if brightness:
            self._set_brightness(brightness)

    def _get_auto_time(self):
        """Get dawn, sunrise, noon, sunset, and dusk time.

        Returns:
            times (dict): dict with associated (datetime, level)
        """
        tz = self.location["timezone"]["code"]
        lat = self.location["coordinate"]["latitude"]
        lon = self.location["coordinate"]["longitude"]
        ast_loc = astral.Location()
        ast_loc.timezone = tz
        ast_loc.lattitude = lat
        ast_loc.longitude = lon

        user_set_tz = timezone(tz).localize(datetime.now()).strftime("%Z")
        device_tz = time.tzname

        if user_set_tz in device_tz:
            sunrise = ast_loc.sun()["sunrise"]
            noon = ast_loc.sun()["noon"]
            sunset = ast_loc.sun()["sunset"]
        else:
            secs = int(self.location["timezone"]["offset"]) / -1000
            sunrise = (
                arrow.get(ast_loc.sun()["sunrise"])
                .shift(seconds=secs)
                .replace(tzinfo="UTC")
                .datetime
            )
            noon = (
                arrow.get(ast_loc.sun()["noon"])
                .shift(seconds=secs)
                .replace(tzinfo="UTC")
                .datetime
            )
            sunset = (
                arrow.get(ast_loc.sun()["sunset"])
                .shift(seconds=secs)
                .replace(tzinfo="UTC")
                .datetime
            )

        return {
            "Sunrise": (sunrise, 20),  # high
            "Noon": (noon, 30),  # full
            "Sunset": (sunset, 5),  # dim
        }

    def schedule_brightness(self, time_of_day, pair):
        """Schedule auto brightness with the event scheduler.

        Arguments:
            time_of_day (str): Sunrise, Noon, Sunset
            pair (tuple): (datetime, brightness)
        """
        d_time = pair[0]
        brightness = pair[1]
        now = arrow.now()
        arw_d_time = arrow.get(d_time)
        data = (time_of_day, brightness)
        if now.timestamp > arw_d_time.timestamp:
            d_time = arrow.get(d_time).shift(hours=+24)
            self.schedule_event(
                self._handle_screen_brightness_event,
                d_time,
                data=data,
                name=time_of_day,
            )
        else:
            self.schedule_event(
                self._handle_screen_brightness_event,
                d_time,
                data=data,
                name=time_of_day,
            )

    @intent_handler("brightness.auto.intent")
    def handle_auto_brightness(self, message):
        """brightness varies depending on time of day

        Arguments:
            message (Message): messagebus message from intent parser
        """
        self.auto_brightness = True
        auto_time = self._get_auto_time()
        nearest_time_to_now = (float("inf"), None, None)
        for time_of_day, pair in auto_time.items():
            self.schedule_brightness(time_of_day, pair)
            now = arrow.now().timestamp
            t = arrow.get(pair[0]).timestamp
            if abs(now - t) < nearest_time_to_now[0]:
                nearest_time_to_now = (abs(now - t), pair[1], time_of_day)
        self.set_screen_brightness(nearest_time_to_now[1], speak=False)

    def _handle_screen_brightness_event(self, message):
        """Wrapper for setting screen brightness from eventscheduler

        Arguments:
            message (Message): messagebus message
        """
        if self.auto_brightness:
            time_of_day = message.data[0]
            level = message.data[1]
            self.cancel_scheduled_event(time_of_day)
            self.set_screen_brightness(level, speak=False)
            pair = self._get_auto_time()[time_of_day]
            self.schedule_brightness(time_of_day, pair)

    #####################################################################
    # Device Settings

    @intent_handler("device.settings.intent")
    def handle_device_settings(self, message):
        """ Display device settings page. """
        self.gui["state"] = "settings/settingspage"
        self.gui.show_page("all.qml")

    @intent_handler("device.wifi.settings.intent")
    def handle_show_wifi_screen_intent(self, message):
        """ display network selection page. """
        self.gui.clear()
        self.gui["state"] = "settings/networking/SelectNetwork"
        self.gui.show_page("all.qml")

    @intent_handler("device.homescreen.settings.intent")
    def handle_device_homescreen_settings(self, message):
        """
        display homescreen settings page
        """
        screens = [{"screenName": s, "screenID": self.screens[s]} for s in self.screens]
        self.gui["idleScreenList"] = {"screenBlob": screens}
        self.gui["selectedScreen"] = self.gui["selected"]
        self.gui["state"] = "settings/homescreen_settings"
        self.gui.show_page("all.qml")

    @intent_handler("device.ssh.settings.intent")
    def handle_device_ssh_settings(self, message):
        """ Display ssh settings page. """
        self.gui["state"] = "settings/ssh_settings"
        self.gui.show_page("all.qml")

    @intent_handler("device.reset.settings.intent")
    def handle_device_factory_reset_settings(self, message):
        """ Display device factory reset settings page. """
        self.gui["state"] = "settings/factoryreset_settings"
        self.gui.show_page("all.qml")

    def handle_device_update_settings(self, message):
        """ Display device update settings page. """
        self.gui["state"] = "settings/updatedevice_settings"
        self.gui.show_page("all.qml")

    def handle_device_restart_action(self, message):
        """ Device restart action. """
        self.log.info("PlaceholderRestartAction")

    def handle_device_poweroff_action(self, message):
        """ Device poweroff action. """
        self.log.info("PlaceholderShutdownAction")


def create_skill():
    return Mark2()
