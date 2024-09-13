from __future__ import absolute_import, print_function, unicode_literals

from builtins import object
from functools import partial
from ableton.v2.base import task
from ableton.v2.control_surface.control import ButtonControl

BLINK_PERIOD = 0.1
DOUBLE_TAP_TIMEOUT = 0.3  # Time window for double tap

class SessionRecordingMixin(object):
    record_button = ButtonControl(delay_time=0.5)  # Button with a 500ms delay

    def __init__(self, *a, **k):
        super(SessionRecordingMixin, self).__init__(*a, **k)
        blink_on = partial(self._set_record_button_color, 'Recording.CaptureTriggered')
        blink_off = partial(self._set_record_button_color, 'DefaultButton.Off')
        self._blink_task = self._tasks.add(task.sequence(task.run(blink_on), task.wait(BLINK_PERIOD), task.run(blink_off), task.wait(BLINK_PERIOD), task.run(blink_on), task.wait(BLINK_PERIOD), task.run(blink_off)))
        self._blink_task.kill()
        self._long_press_task = None  # To handle long press (1-second undo)
        self._undo_triggered = False  # To ensure undo is only triggered once
        self._tap_count = 0  # Track taps for double-tap detection
        self._double_tap_task = None  # Handle the double-tap timing

    @record_button.pressed
    def record_button(self, _):
        # Start a task to trigger undo after 1 second (if button is held long enough)
        self._undo_triggered = False  # Reset undo trigger
        self._long_press_task = self._tasks.add(task.sequence(task.wait(1.0), task.run(self._trigger_undo)))

    @record_button.released
    def record_button(self, _):
        if self._long_press_task is not None:
            self._long_press_task.kill()  # Kill the long press task on release
        if not self._undo_triggered:
            self._tap_count += 1
            if self._tap_count == 1:
                # Set a timeout for detecting a second tap (for double tap)
                self._double_tap_task = self._tasks.add(task.sequence(task.wait(DOUBLE_TAP_TIMEOUT), task.run(self._trigger_short_recording)))

            elif self._tap_count == 2:
                # Double tap detected, trigger long recording
                self._trigger_long_recording()
                if self._double_tap_task is not None:
                    self._double_tap_task.kill()  # Kill the task since double tap was detected
                self._tap_count = 0

    def _trigger_short_recording(self):
        # Trigger short recording (single tap)
        track = self.song.view.selected_track
        if track.name == "DRUMS":
            self._trigger_recording(8)  # 2-bar recording
        else:
            self._trigger_recording(16)  # 4-bar recording
        self._tap_count = 0  # Reset tap count

    def _trigger_long_recording(self):
        # Trigger long recording (double tap)
        track = self.song.view.selected_track
        if track.name == "DRUMS":
            self._trigger_recording(16)  # 4-bar recording
        else:
            self._trigger_recording(32)  # 8-bar recording

    def _trigger_undo(self):
        # Trigger undo action after 1 second of holding the button
        self.song.undo()  # Calls the undo action in Ableton Live
        self._undo_triggered = True  # Set undo flag to prevent recording

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
            if not clip_slot.has_clip:  # Check if the slot is empty before recording
                clip_slot.fire(record_length=record_length)  # Start recording with the specified length
            else:
                clip_slot.fire()  # If it's not empty, just launch the clip
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
            self._switch_to_session_mode()  # Switch to Session Mode when metronome turns off

        # Schedule to turn off the metronome after 1 bar
        self._tasks.add(task.sequence(task.wait(self.song.signature_numerator), task.run(turn_off_metronome)))

    def _switch_to_session_mode(self):
        sysex_message = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x00, 0xF7)  # SysEx message for session mode
        self._send_sysex(sysex_message)  # Use send_sysex for SysEx message handling

    def _send_sysex(self, sysex_message):
        try:
            self._tasks.add(task.run(lambda: self.canonical_parent._send_midi(sysex_message)))
        except AttributeError:
            self.canonical_parent.log_message("Error sending SysEx message for Session Mode.")
