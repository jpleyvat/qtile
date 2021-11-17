from subprocess import CalledProcessError, Popen

# qtile
from libqtile.widget import base


class CheckMicrophone(base.InLoopPollText):
    """Widget to show microphone status."""

    defaults = [
        ("custom_command", None, "Custom shell command for checking microphone status. use {source} placeholder for the source to monitor."),
        ("update_interval", 60, "Update interval in seconds."),
        ('execute', None, 'Command to execute on click'),
        ('source', None, 'Source to check for.'),
        ("get_status", (lambda x: x), "Lambda function to modify line count from custom_command"),
        ("muted_str", "","String to show when muted"),
        ("unmuted_str", "","String to show when unmuted"),
    ]


    def __init__(self, **config):
        super().__init__('',**config)
        self.add_defaults(CheckMicrophone.defaults)

        # Helpful to have this as a variable as we can shorten it for testing
        self.execute_polling_interval = 1

        if self.custom_command:
            # Use custom_command
            self.cmd = self.custom_command.format(source=self.source)
        else:
            # Default command for pulseaudio
            self.cmd = f"pactl get-source-mute {self.source}"

        if self.execute:
            self.add_callbacks({'Button1': self.do_execute})


    def _checK_mic_status(self):
        """Check microphone mute status."""

        try:
            check_mic_status = self.call_process(self.cmd, shell=True)
        except CalledProcessError:
            check_mic_status = ""

        mic_mute_status = self.custom_command_get_status(check_mic_status)

        if isinstance(mic_mute_status, str):
            return mic_mute_status

        if mic_mute_status:
            return self.muted_str

        return self.unmuted_str


    def poll(self):
        if not self.cmd:
            return "N/A"
        return self._checK_mic_status()


    def do_execute(self):
        self._process = Popen(self.execute, shell=True)
        self.timeout_add(self.execute_polling_interval, self._refresh_count)


    def _refresh_count(self):
        if self._process.poll() is None:
            self.timeout_add(self.execute_polling_interval, self._refresh_count)

        else:
            self.timer_setup()


    def cmd_update(self):
        """Updates widget from script console."""

        self.tick()
