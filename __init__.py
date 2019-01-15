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

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util import connected, find_input_device, get_ipc_directory
from mycroft.util.log import LOG
from mycroft.util.parse import normalize
from mycroft.audio import wait_while_speaking
from mycroft import intent_file_handler

import os

import pyaudio
import struct
import math
from threading import Thread

FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

def get_rms(block):
    """ RMS amplitude is defined as the square root of the
    mean over time of the square of the amplitude.
     so we need to convert this string of bytes into
     a string of 16-bit samples...
    """
    # we will get one short out for each
    # two chars in the string.
    count = len(block) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n

    return math.sqrt(sum_squares / count)


def open_mic_stream(pa, device_index, device_name):
    """ Open microphone stream from first best microphone device. """
    if not device_index and device_name:
        device_index = find_input_device(device_name)

    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                     input=True, input_device_index=device_index,
                     frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

    return stream


def read_file_from(filename, bytefrom):
    """ Read listener level from offset. """
    with open(filename, 'r') as fh:
        meter_cur = None
        fh.seek(bytefrom)
        while True:
            line = fh.readline()
            if line == "":
                break

            # Just adjust meter settings
            # Ex:Energy:  cur=4 thresh=1.5
            parts = line.split("=")
            meter_thresh = float(parts[-1])
            meter_cur = float(parts[-2].split(" ")[0])
        return meter_cur


class Mark2(MycroftSkill):

    IDLE_CHECK_FREQUENCY = 6  # in seconds

    def __init__(self):
        super().__init__("Mark2")

        self.idle_count = 99
        self.hourglass_info = {}
        self.interaction_id = 0

        self.settings['auto_brightness'] = False
        self.settings['auto_dim_eyes'] = True
        self.settings['use_listening_beep'] = True
        self.settings['eye color'] = "default"
        self.settings['current_eye_color'] = self.settings['eye color']

        self.has_show_page = False  # resets with each handler

        self.setup_mic_listening()
        self.listener_file = os.path.join(get_ipc_directory(), "mic_level")
        self.st_results = os.stat(self.listener_file)
        self.max_amplitude = 0

    def setup_mic_listening(self):
        """ Initializes PyAudio, starts an input stream and launches the
            listening thread.
        """
        self.pa = pyaudio.PyAudio()
        listener_conf = self.config_core['listener']
        self.stream = open_mic_stream(self.pa,
                                      listener_conf.get('device_index'),
                                      listener_conf.get('device_name'))
        self.amplitude = 0

    def initialize(self):
        # Initialize...
        self.brightness_dict = self.translate_namedvalues('brightness.levels')
        self.color_dict = self.translate_namedvalues('colors')
        self.settings['web eye color'] = self.settings['eye color']
        self.gui['volume'] = 0

        # Start listening thread
        self.running = True
        self.thread = Thread(target=self.listen_thread)
        self.thread.daemon = True
        self.thread.start()

        try:
            # Handle changing the eye color once Mark 1 is ready to go
            # (Part of the statup sequence)
            self.add_event('mycroft.internet.connected',
                           self.handle_internet_connected)

            self.add_event('mycroft.eyes.default',
                           self.handle_default_eyes)

            # Handle the 'waking' visual
            self.add_event('recognizer_loop:record_begin',
                           self.handle_listener_started)
            self.add_event('recognizer_loop:record_end',
                           self.handle_listener_ended)
            self.add_event('mycroft.speech.recognition.unknown',
                           self.handle_failed_stt)

            self.start_idle_check()

            # Handle the 'busy' visual
            self.bus.on('mycroft.skill.handler.start',
                        self.on_handler_started)
            self.bus.on('mycroft.skill.handler.complete',
                        self.on_handler_complete)

            self.bus.on('recognizer_loop:sleep',
                        self.on_handler_sleep)
            self.bus.on('mycroft.awoken',
                        self.on_handler_awoken)
            self.bus.on('recognizer_loop:audio_output_start',
                        self.on_handler_interactingwithuser)
            self.bus.on('enclosure.mouth.think',
                        self.on_handler_interactingwithuser)
            self.bus.on('enclosure.mouth.reset',
                        self.on_handler_mouth_reset)
            self.bus.on('recognizer_loop:audio_output_end',
                        self.on_handler_mouth_reset)
            self.bus.on('enclosure.mouth.events.deactivate',
                        self.on_handler_interactingwithuser)
            self.bus.on('enclosure.mouth.text',
                        self.on_handler_interactingwithuser)
            self.bus.on('enclosure.mouth.viseme',
                        self.on_handler_speaking)
            self.bus.on('gui.page.show',
                        self.on_gui_page_show)

            self.bus.on('mycroft.skills.initialized', self.reset_face)
            
            # Handle device settings events
            self.add_event('mycroft.device.settings', 
                           self.handle_device_settings) #Use Legacy for QuickSetting delegate
            self.gui.register_handler('mycroft.device.settings', 
                                      self.handle_device_settings)
            self.gui.register_handler('mycroft.device.settings.brightness', 
                                      self.handle_device_brightness_settings)
            self.gui.register_handler('mycroft.device.settings.homescreen', 
                                      self.handle_device_homescreen_settings)
            self.gui.register_handler('mycroft.device.settings.ssh', 
                                      self.handle_device_ssh_settings)
            self.gui.register_handler('mycroft.device.settings.reset', 
                                      self.handle_device_factory_reset_settings)
            self.gui.register_handler('mycroft.device.settings.update', 
                                      self.handle_device_update_settings)
            self.gui.register_handler('mycroft.device.settings.restart', 
                                      self.handle_device_restart_action)
            self.gui.register_handler('mycroft.device.settings.poweroff', 
                            self.handle_device_poweroff_action)

        except Exception:
            LOG.exception('In Mark 1 Skill')

        # Update use of wake-up beep
        self._sync_wake_beep_setting()

        self.settings.set_changed_callback(self.on_websettings_changed)

    def reset_face(self, message):
        if connected():
            # Connected at startup: setting eye color
            self.enclosure.mouth_reset()

    def listen_thread(self):
        """ listen on mic input until self.running is False. """
        while(self.running):
            self.listen()

    def get_audio_level(self):
        """ Get level directly from audio device. """
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError as e:
            # damn
            self.errorcount += 1
            self.log.error("(%d) Error recording: %s"%(self.errorcount,e))
            self.noisycount = 1
            return None

        return int(get_rms(block) * 20)

    def get_listener_level(self):
        """ Get level from IPC file created by listener. """
        time.sleep(0.05)
        try:
            st_results = os.stat(self.listener_file)

            if (not st_results.st_ctime == self.st_results.st_ctime or
                    not st_results.st_mtime == self.st_results.st_mtime):
                ret = read_file_from(self.listener_file, 0)
                self.st_results = st_results
                if ret is not None:
                    if ret > self.max_amplitude:
                        self.max_amplitude = ret
                    ret = int(ret / self.max_amplitude * 10)
                return ret
        except Exception as e:
            self.log.error(repr(e))
        return None

        
    def listen(self):
        """ Read microphone level and store rms into self.gui['volume']. """
        #amplitude = self.get_audio_level()
        amplitude = self.get_listener_level()

        if (self.gui and ('volume' not in self.gui
                     or self.gui['volume'] != amplitude) and
                 amplitude is not None):
            self.gui['volume'] = amplitude

    def shutdown(self):
        # Gotta clean up manually since not using add_event()
        self.bus.remove('mycroft.skill.handler.start',
                        self.on_handler_started)
        self.bus.remove('mycroft.skill.handler.complete',
                        self.on_handler_complete)
        self.bus.remove('recognizer_loop:audio_output_start',
                        self.on_handler_interactingwithuser)
        self.bus.remove('recognizer_loop:sleep',
                        self.on_handler_sleep)
        self.bus.remove('mycroft.awoken',
                        self.on_handler_awoken)
        self.bus.remove('enclosure.mouth.think',
                        self.on_handler_interactingwithuser)
        self.bus.remove('enclosure.mouth.reset',
                        self.on_handler_mouth_reset)
        self.bus.remove('recognizer_loop:audio_output_end',
                        self.on_handler_mouth_reset)
        self.bus.remove('enclosure.mouth.events.deactivate',
                        self.on_handler_interactingwithuser)
        self.bus.remove('enclosure.mouth.text',
                        self.on_handler_interactingwithuser)
        self.bus.remove('enclosure.mouth.viseme',
                        self.on_handler_speaking)

        self.running = False
        self.thread.join()
        self.stream.close()

    #####################################################################
    # Manage "busy" visual

    def on_handler_started(self, message):
        handler = message.data.get("handler", "")
        # Ignoring handlers from this skill and from the background clock
        if "Mark2" in handler:
            return
        if "TimeSkill.update_display" in handler:
            return

        self.hourglass_info[handler] = self.interaction_id
        # time.sleep(0.25)
        if self.hourglass_info[handler] == self.interaction_id:
            # Nothing has happend within a quarter second to indicate to the
            # user that we are active, so start a thinking visual
            self.hourglass_info[handler] = -1
            # SSP: No longer need this logic since we show "thinking.qml"
            #      immediately after the record_end?
            # self.gui.show_page("thinking.qml")

    def on_gui_page_show(self, message):
        print('HANDLER', message.data)
        if "mark-2" not in message.data.get("__from", ""):
            # Some skill other than the handler is showing a page
            # TODO: Maybe just check for the "speaking.qml" page?
            self.has_show_page = True
            override_idle = message.data.get('__idle')
            if override_idle is not None:
                print("CANCELING IDLE")
                self.cancel_scheduled_event('IdleCheck')

    def on_handler_mouth_reset(self, message):
        """ Restore viseme to a smile. """
        self.gui['viseme'] = 'smile'

    def on_handler_interactingwithuser(self, message):
        # Every time we do something that the user would notice, increment
        # an interaction counter.
        self.interaction_id += 1

    def on_handler_sleep(self, message):
        """ Show resting face when going to sleep. """
        self.gui['state'] = 'resting'
        self.gui.show_page("all.qml")

    def on_handler_awoken(self, message):
        """ Show awake face when sleep ends. """
        self.gui['state'] = 'awake'
        self.gui.show_page("all.qml")

    def on_handler_complete(self, message):
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
        except:
            # There is a slim chance the self.hourglass_info might not
            # be populated if this skill reloads at just the right time
            # so that it misses the mycroft.skill.handler.start but
            # catches the mycroft.skill.handler.complete
            pass

    #####################################################################
    # Manage "speaking" visual

    def on_handler_speaking(self, message):
        print(message.data["code"], self.has_show_page)
        if not self.has_show_page and self.gui['state'] != 'speaking':
            self.gui['state'] = 'speaking'
            self.gui.show_page("all.qml")
        self.gui["viseme"] = message.data["code"]

    #####################################################################
    # Manage "idle" visual state

    def start_idle_check(self):
        # Clear any existing checker
        print("!!!!! START IDLE CHECK !!!!!")
        self.cancel_scheduled_event('IdleCheck')
        self.idle_count = 0

        if True:
            # Schedule a check every few seconds
            self.schedule_repeating_event(self.check_for_idle, None,
                                          Mark2.IDLE_CHECK_FREQUENCY,
                                          name='IdleCheck')

    def check_for_idle(self):
        print('CHECING IDLE')
        if True:
            # No activity, start to fall asleep
            self.idle_count += 1

            if self.idle_count == 5:
                # Go into a 'sleep' visual state
                print("TRIGGERED!")
                self.bus.emit(Message('mycroft-date-time.mycroftai.idle'))
            elif self.idle_count > 5:
                self.cancel_scheduled_event('IdleCheck')

    def handle_listener_started(self, message):
        if False:
            self.cancel_scheduled_event('IdleCheck')
        else:
            print("IDLE CHECK!")
            # Check if in 'idle' state and visually come to attention
            if self.idle_count > 2:
                # Perform 'waking' animation
                # TODO: Anything in QML?  E.g. self.gui.show_page("waking.qml")

                # Begin checking for the idle state again
                self.idle_count = 0
                self.start_idle_check()

        self.gui['state'] = 'listening'
        self.gui.show_page('all.qml')

    def handle_listener_ended(self, message):
        self.gui['state'] = 'thinking'
        self.gui.show_page('all.qml')

    def handle_failed_stt(self, message):
        # No discernable words were transcribed
        self.gui.show_page("idle.qml")

    #####################################################################
    # Manage network connction feedback

    def handle_internet_connected(self, message):
        # System came online later after booting
        self.enclosure.mouth_reset()

    #####################################################################
    # Reset eye appearance

    def handle_default_eyes(self, message):
        pass # self.set_eye_color(self.settings['current_eye_color'], speak=False)

    #####################################################################
    # Web settings

    def on_websettings_changed(self):
        # Update eye state if auto_dim_eyes changes...
        # if self.settings.get("auto_dim_eyes"):
        #     self.start_idle_check()
        # else:
        #     # No longer dimming, show open eyes if closed...
        #     self.cancel_scheduled_event('IdleCheck')
        #     if self.idle_count > 2:
        #         self.idle_count = 0
        #         self.enclosure.eyes_color(self._current_color)

        # Update use of wake-up beep
        self._sync_wake_beep_setting()

    def _sync_wake_beep_setting(self):
        from mycroft.configuration.config import (
            LocalConf, USER_CONFIG, Configuration
        )
        config = Configuration.get()
        use_beep = self.settings.get("use_listening_beep") is True
        if not config['confirm_listening'] == use_beep:
            # Update local (user) configuration setting
            new_config = {
                'confirm_listening': use_beep
            }
            user_config = LocalConf(USER_CONFIG)
            user_config.merge(new_config)
            user_config.store()
            self.bus.emit(Message('configuration.updated'))

    #####################################################################
    # Brightness intent interaction

    def percent_to_level(self, percent):
        """ converts the brigtness value from percentage to
             a value arduino can read

            Args:
                percent (int): interger value from 0 to 100

            return:
                (int): value form 0 to 30
        """
        return int(float(percent)/float(100)*30)

    def parse_brightness(self, brightness):
        """ parse text for brightness percentage

            Args:
                brightness (str): string containing brightness level

            return:
                (int): brightness as percentage (0-100)
        """

        try:
            # Handle "full", etc.
            name = normalize(brightness)
            if name in self.brightness_dict:
                return self.brightness_dict[name]

            if '%' in brightness:
                brightness = brightness.replace("%", "").strip()
                return int(brightness)
            if 'percent' in brightness:
                brightness = brightness.replace("percent", "").strip()
                return int(brightness)

            i = int(brightness)
            if i < 0 or i > 100:
                return None

            if i < 30:
                # Assmume plain 0-30 is "level"
                return int((i*100.0)/30.0)

            # Assume plain 31-100 is "percentage"
            return i
        except:
            return None  # failed in an int() conversion

    def set_eye_brightness(self, level, speak=True):
        """ Actually change hardware eye brightness

            Args:
                level (int): 0-30, brightness level
                speak (bool): when True, speak a confirmation
        """
        self.enclosure.eyes_brightness(level)
        if speak is True:
            percent = int(float(level)*float(100)/float(30))
            self.speak_dialog(
                'brightness.set', data={'val': str(percent)+'%'})

    def _set_brightness(self, brightness):
        # brightness can be a number or word like "full", "half"
        percent = self.parse_brightness(brightness)
        if percent is None:
            self.speak_dialog('brightness.not.found.final')
        elif int(percent) is -1:
            self.handle_auto_brightness(None)
        else:
            self.auto_brightness = False
            self.set_eye_brightness(self.percent_to_level(percent))

    @intent_file_handler('brightness.intent')
    def handle_brightness(self, message):
        """ Intent Callback to set custom eye brightness

            Args:
                message (dict): messagebus message from intent parser
        """
        brightness = (message.data.get('brightness', None) or
                      self.get_response('brightness.not.found'))
        if brightness:
            self._set_brightness(brightness)

    def _get_auto_time(self):
        """ get dawn, sunrise, noon, sunset, and dusk time

            returns:
                times (dict): dict with associated (datetime, level)
        """
        tz = self.location['timezone']['code']
        lat = self.location['coordinate']['latitude']
        lon = self.location['coordinate']['longitude']
        ast_loc = astral.Location()
        ast_loc.timezone = tz
        ast_loc.lattitude = lat
        ast_loc.longitude = lon

        user_set_tz = \
            timezone(tz).localize(datetime.now()).strftime('%Z')
        device_tz = time.tzname

        if user_set_tz in device_tz:
            sunrise = ast_loc.sun()['sunrise']
            noon = ast_loc.sun()['noon']
            sunset = ast_loc.sun()['sunset']
        else:
            secs = int(self.location['timezone']['offset']) / -1000
            sunrise = arrow.get(
                ast_loc.sun()['sunrise']).shift(
                    seconds=secs).replace(tzinfo='UTC').datetime
            noon = arrow.get(
                ast_loc.sun()['noon']).shift(
                    seconds=secs).replace(tzinfo='UTC').datetime
            sunset = arrow.get(
                ast_loc.sun()['sunset']).shift(
                    seconds=secs).replace(tzinfo='UTC').datetime

        return {
            'Sunrise': (sunrise, 20),  # high
            'Noon': (noon, 30),        # full
            'Sunset': (sunset, 5)      # dim
        }

    def schedule_brightness(self, time_of_day, pair):
        """ schedule auto brightness with the event scheduler

            Args:
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
            self.schedule_event(self._handle_eye_brightness_event, d_time,
                                data=data, name=time_of_day)
        else:
            self.schedule_event(self._handle_eye_brightness_event, d_time,
                                data=data, name=time_of_day)

    # TODO: this is currently set by voice.
    # allow setting from faceplate and web ui
    @intent_file_handler('brightness.auto.intent')
    def handle_auto_brightness(self, message):
        """ brightness varies depending on time of day

            Args:
                message (dict): messagebus message from intent parser
        """
        self.auto_brightness = True
        auto_time = self._get_auto_time()
        nearest_time_to_now = (float('inf'), None, None)
        for time_of_day, pair in auto_time.items():
            self.schedule_brightness(time_of_day, pair)
            now = arrow.now().timestamp
            t = arrow.get(pair[0]).timestamp
            if abs(now - t) < nearest_time_to_now[0]:
                nearest_time_to_now = (abs(now - t), pair[1], time_of_day)
        self.set_eye_brightness(nearest_time_to_now[1], speak=False)

        # SSP: I'm disabling this for now.  I don't think we
        # should announce this every day, it'll get tedious.
        #
        # tod = nearest_time_to_now[2]
        # if tod == 'Sunrise':
        #     self.speak_dialog('auto.sunrise')
        # elif tod == 'Sunset':
        #     self.speak_dialog('auto.sunset')
        # elif tod == 'Noon':
        #     self.speak_dialog('auto.noon')

    def _handle_eye_brightness_event(self, message):
        """ wrapper for setting eye brightness from
            eventscheduler

            Args:
                message (dict): messagebus message
        """
        if self.auto_brightness is True:
            time_of_day = message.data[0]
            level = message.data[1]
            self.cancel_scheduled_event(time_of_day)
            self.set_eye_brightness(level, speak=False)
            pair = self._get_auto_time()[time_of_day]
            self.schedule_brightness(time_of_day, pair)

    #####################################################################
    # Device Settings
    
    @intent_file_handler('device.settings.intent')
    def handle_device_settings(self, message):
        """ 
            display device settings page
        """
        self.gui['state'] = 'settings/settingspage'
        self.gui.show_page('all.qml')
    
    @intent_file_handler('device.brightness.settings.intent')
    def handle_device_brightness_settings(self, message):
        """
            display brightness settings page
        """
        self.gui['state'] = 'settings/brightness_settings'
        self.gui.show_page('all.qml')
        
    @intent_file_handler('device.homescreen.settings.intent')
    def handle_device_homescreen_settings(self, message):
        """
            display homescreen settings page
        """
        self.gui['state'] = 'settings/homescreen_settings'
        self.gui.show_page('all.qml')
        
    @intent_file_handler('device.ssh.settings.intent')
    def handle_device_ssh_settings(self, message):
        """
            display ssh settings page
        """
        self.gui['state'] = 'settings/ssh_settings'
        self.gui.show_page('all.qml')

    @intent_file_handler('device.reset.settings.intent')
    def handle_device_factory_reset_settings(self, message):
        """
            display device factory reset settings page
        """
        self.gui['state'] = 'settings/factoryreset_settings'
        self.gui.show_page('all.qml')
        
    def handle_device_update_settings(self, message):
        """
            display device update settings page
        """
        self.gui['state'] = 'settings/updatedevice_settings'
        self.gui.show_page('all.qml')
        
    def handle_device_restart_action(self, message):
        """
            device restart action
        """
        print("PlaceholderRestartAction")

    def handle_device_poweroff_action(self, message):
        """
            device poweroff action
        """
        print("PlaceholderShutdownAction")


def create_skill():
    return Mark2()
