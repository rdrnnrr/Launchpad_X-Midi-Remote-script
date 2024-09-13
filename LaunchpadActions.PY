from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import Live

class LaunchpadActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('note_mode', self.switch_to_note_mode)
        self.add_global_action('session_mode', self.switch_to_session_mode)
        self.add_global_action('custom1_mode', self.switch_to_custom1_mode)
        self.add_global_action('custom2_mode', self.switch_to_custom2_mode)
        self.add_global_action('custom3_mode', self.switch_to_custom3_mode)
        self.add_global_action('custom4_mode', self.switch_to_custom4_mode)
        self.add_global_action('custom5_mode', self.switch_to_custom5_mode)
        self.add_global_action('custom6_mode', self.switch_to_custom6_mode)
        self.add_global_action('custom7_mode', self.switch_to_custom7_mode)
        self.add_global_action('custom8_mode', self.switch_to_custom8_mode)
        self.add_global_action('daw_faders_mode', self.switch_to_daw_faders_mode)
        self.add_global_action('programmer_mode', self.switch_to_programmer_mode)
        self.add_global_action('intelligent_drum_mode', self.switch_to_intelligent_drum_mode)
        self.add_global_action('monitor_recording', self.monitor_recording)

        self.monitor_recording(None, None)

    def send_mode_sysex(self, sysex, mode_name):
        try:
            self.canonical_parent.schedule_message(0, self.send_sysex, sysex)
            self.canonical_parent.log_message(f"{mode_name} SysEx message sent successfully: {sysex}")
        except Exception as e:
            self.canonical_parent.log_message(f"Error sending SysEx message for {mode_name}: {str(e)}")

    def send_sysex(self, sysex):
        self.canonical_parent._send_midi(tuple(sysex))

    def switch_to_note_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x01, 0xF7), "Note mode")

    def switch_to_session_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x00, 0xF7), "Session mode")

    def switch_to_custom1_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x04, 0xF7), "Custom 1 mode")

    def switch_to_custom2_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x05, 0xF7), "Custom 2 mode")

    def switch_to_custom3_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x06, 0xF7), "Custom 3 mode")

    def switch_to_custom4_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x07, 0xF7), "Custom 4 mode")

    def switch_to_custom5_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x08, 0xF7), "Custom 5 mode")

    def switch_to_custom6_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x09, 0xF7), "Custom 6 mode")

    def switch_to_custom7_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x0A, 0xF7), "Custom 7 mode")

    def switch_to_custom8_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x0B, 0xF7), "Custom 8 mode")

    def switch_to_daw_faders_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x0D, 0xF7), "DAW Faders mode")

    def switch_to_programmer_mode(self, action_def, args):
        self.send_mode_sysex((0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x00, 0x7F, 0xF7), "Programmer mode")

    def switch_to_intelligent_drum_mode(self, action_def, args):
        position = 0  # Default position
        if args:
            try:
                position = int(args)
                if position < 0 or position > 64:
                    self.canonical_parent.log_message("Position out of range, resetting to 0")
                    position = 0
            except ValueError:
                self.canonical_parent.log_message("Invalid position argument, resetting to 0")
                position = 0

        sysex_message = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x13, position, 0xF7)
        self.canonical_parent.log_message(f"Switching to Intelligent Drum Rack mode with SysEx: {sysex_message}")
        self.send_mode_sysex(sysex_message, "Intelligent Drum Rack mode")

    def monitor_recording(self, action_def, args):
        self.canonical_parent.log_message("Monitoring recording state")
        self.song().add_tracks_listener(self.on_tracks_changed)
        self.setup_track_listeners()

    def on_tracks_changed(self):
        self.canonical_parent.log_message("Tracks changed, setting up listeners")
        self.setup_track_listeners()

    def setup_track_listeners(self):
        for track in self.song().tracks:
            if track != self.song().master_track and track.name in ["Pigments", "Analog Lab", "DRUMS", "MIDIBASS", "GUITAR"]:
                self.canonical_parent.log_message(f"Setting up listener for track {track.name}")
                if not hasattr(track, 'has_monitor_listener') or not track.has_monitor_listener:
                    track.has_monitor_listener = True
                for clip_slot in track.clip_slots:
                    if not hasattr(clip_slot, 'has_clip_slot_listener') or not clip_slot.has_clip_slot_listener:
                        clip_slot.add_is_triggered_listener(lambda cs=clip_slot, t=track: self.on_clip_slot_triggered(t, cs))
                        clip_slot.has_clip_slot_listener = True

    def on_clip_slot_triggered(self, track, clip_slot):
        self.canonical_parent.log_message(f"Clip slot on track {track.name} triggered state changed to {clip_slot.is_triggered}")
        if clip_slot.is_triggered and clip_slot.will_record_on_start:
            self.canonical_parent.log_message(f"Clip slot on track {track.name} is triggered to start recording")
            self.set_launchpad_mode(track)

    def set_launchpad_mode(self, track):
        if track.name == "Pigments":
            self.switch_to_custom8_mode(None, None)
        elif track.name == "Analog Lab":
            self.switch_to_custom7_mode(None, None)
        elif track.name == "DRUMS":
            self.switch_to_custom6_mode(None, None)
        elif track.name == "MIDIBASS":
            self.switch_to_custom5_mode(None, None)
        elif track.name == "GUITAR":
            self.switch_to_custom1_mode(None, None)
        else:
            self.switch_to_note_mode(None, None)
