from __future__ import absolute_import, print_function, unicode_literals
from builtins import next
from ableton.v2.base import liveobj_valid
from novation.channel_strip import ChannelStripComponent as ChannelStripComponentBase  # Corrected the import

class ChannelStripComponent(ChannelStripComponentBase):  # Ensure this is inheriting from the correct class

    def update(self):
        super(ChannelStripComponent, self).update()  # Call the base class's update method
        self._update_static_color_control()  # Call your custom method

    def _update_static_color_control(self):
        valid_track = liveobj_valid(self._track)  # Check if the track is valid
        color_value = self._static_color_value if valid_track else 0  # Set the color value
        if valid_track:
            if self._send_controls:
                send_index = next((i for i, x in enumerate(self._send_controls) if x), None)  # Get the first valid send control index
                if send_index is not None:
                    if send_index >= len(self._track.mixer_device.sends):  # Ensure the send index is within the track's sends
                        color_value = 0
        if self.static_color_control:  # Check if static_color_control exists
            self.static_color_control.value = color_value  # Assign the color value to the control
