from __future__ import absolute_import, print_function, unicode_literals
from builtins import object
from functools import partial
from ableton.v2.base import task
from ableton.v2.control_surface.control import ButtonControl

BLINK_PERIOD = 0.1

class SessionRecordingMixin(object):
    record_button = ButtonControl(delay_time=0.5)

    def __init__(self, *a, **k):
        super(SessionRecordingMixin, self).__init__(*a, **k)
        blink_on = partial(self._set_record_button_color, 'Recording.CaptureTriggered')
        blink_off = partial(self._set_record_button_color, 'DefaultButton.Off')
        self._blink_task = self._tasks.add(task.sequence(task.run(blink_on), task.wait(BLINK_PERIOD), task.run(blink_off), task.wait(BLINK_PERIOD), task.run(blink_on), task.wait(BLINK_PERIOD), task.run(blink_off)))
        self._blink_task.kill()

    @record_button.released_immediately
    def record_button(self, _):
        track = self.song.view.selected_track
        if track.name == "DRUMS":
            self._trigger_recording(8)  # 2-bar recording
        else:
            self._trigger_recording(16)  # 4-bar recording

    @record_button.pressed_delayed
    def record_button(self, _):
        track = self.song.view.selected_track
        if track.name == "DRUMS":
            self._trigger_recording(16)  # 4-bar recording
        else:
            self._trigger_recording(32)  # 8-bar recording

    @record_button.released
    def record_button(self, _):
        self._update_record_button()

    def _update_record_button(self):
        if not self.record_button.is_pressed:
            self._blink_task.kill()
            super(SessionRecordingMixin, self)._update_record_button()

    def _set_record_button_color(self, color):
        self.record_button.color = color

    def _trigger_recording(self, record_length):
        clip_slot = self.song.view.highlighted_clip_slot
        track = self.song.view.selected_track

        if clip_slot and track.can_be_armed and track.arm:
            self._enable_metronome()  # Turn on the metronome when recording starts
            clip_slot.fire(record_length=record_length)  # Start recording with the specified length
            self._monitor_clip_recording(clip_slot)

    def _enable_metronome(self):
        self.song.metronome = True

    def _disable_metronome(self):
        self.song.metronome = False

    def _monitor_clip_recording(self, clip_slot):
        def check_recording_status():
            # Ensure we only turn off the metronome after recording finishes
            if clip_slot.has_clip and not clip_slot.clip.is_recording:
                # Schedule to turn off the metronome after 1 bar
                self._schedule_metronome_off()
                return None  # Stop the loop
            # Keep checking
            self._tasks.add(task.sequence(task.wait(0.1), task.run(check_recording_status)))

        # Start monitoring the clip recording status every 0.1 seconds
        self._tasks.add(task.sequence(task.wait(0.1), task.run(check_recording_status)))

    def _schedule_metronome_off(self):
        def turn_off_metronome():
            self._disable_metronome()

        # Schedule to turn off the metronome after 1 bar
        self._tasks.add(task.sequence(task.wait(self.song.signature_numerator), task.run(turn_off_metronome)))
