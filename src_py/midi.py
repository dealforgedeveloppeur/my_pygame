import math
import atexit
import pygame
import pygame.locals
import pygame.pypm as _pypm

MIDIIN = pygame.locals.MIDIIN
MIDIOUT = pygame.locals.MIDIOUT

__all__ = [
    "Input",
    "MIDIIN",
    "MIDIOUT",
    "MidiException",
    "Output",
    "get_count",
    "get_default_input_id",
    "get_default_output_id",
    "get_device_info",
    "init",
    "midis2events",
    "quit",
    "get_init",
    "time",
    "frequency_to_midi",
    "midi_to_frequency",
    "midi_to_ansi_note",
]

__theclasses__ = ["Input", "Output"]

def _module_init(state = None):
    if state is not None:
        _module_init.value = state
        return state
    try:
        _module_init.value
    except AttributeError:
        return False
    return _module_init.value

def init():
    if not _module_init():
        _pypm.Initialize()
        _module_init(True)
        atexit.register(quit)

def quit():
    if _module_init():
        _pypm.Terminate()
        _module_init(False)


def get_init():
    return _module_init()


def _check_init():
    if not _module_init():
        raise RuntimeError("pygame.midi not initialised.")


def get_count():
    _check_init()
    return _pypm.CountDevices()


def get_default_input_id():
    _check_init()
    return _pypm.GetDefaultInputDeviceID()


def get_default_output_id():
    _check_init()
    return _pypm.GetDefaultOutputDeviceID()


def get_device_info(an_id):
    _check_init()
    return _pypm.GetDeviceInfo(an_id)


class Input:
    def __init__(self, device_id, buffer_size=4096):
        _check_init()
        if device_id == -1:
            raise MidiException(
                "Device id is -1, not a valid output id.  "
                "-1 usually means there were no default "
                "Output devices."
            )
        try:
            result = get_device_info(device_id)
        except TypeError:
            raise TypeError("an integer is required")
        except OverflowError:
            raise OverflowError("long int too large to convert to int")
        if result:
            _, _, is_input, is_output, _ = result
            if is_input:
                try:
                    self._input = _pypm.Input(device_id, buffer_size)
                except TypeError:
                    raise TypeError("an integer is required")
                self.device_id = device_id
            elif is_output:
                raise MidiException("Device id given is not a valid input id, it is an output id.")
            else:
                raise MidiException("Device id given is not a valid input id.")
        else:
            raise MidiException("Device id invalid, out of range.")

    def _check_open(self):
        if self._input is None:
            raise MidiException("midi not open.")

    def close(self):
        _check_init()
        if self._input is not None:
            self._input.Close()
        self._input = None

    def read(self, num_events):
        _check_init()
        self._check_open()
        return self._input.Read(num_events)

    def poll(self):
        _check_init()
        self._check_open()
        result = self._input.Poll()
        if result == _pypm.TRUE:
            return True
        if result == _pypm.FALSE:
            return False
        err_text = _pypm.GetErrorText(result)
        raise MidiException((result, err_text))


class Output:
    def __init__(self, device_id, latency=0, buffer_size=256):
        _check_init()
        self._aborted = 0
        if device_id == -1:
            raise MidiException(
                "Device id is -1, not a valid output id."
                "  -1 usually means there were no default "
                "Output devices."
            )
        try:
            result = get_device_info(device_id)
        except TypeError:
            raise TypeError("an integer is required")
        except OverflowError:
            raise OverflowError("long int too large to convert to int")
        if result:
            _, _, is_input, is_output, _ = result
            if is_output:
                try:
                    self._output = _pypm.Output(device_id, latency, buffer_size)
                except TypeError:
                    raise TypeError("an integer is required")
                self.device_id = device_id
            elif is_input:
                raise MidiException(
                    "Device id given is not a valid output id, it is an input id."
                )
            else:
                raise MidiException("Device id given is not a valid output id.")
        else:
            raise MidiException("Device id invalid, out of range.")

    def _check_open(self):
        if self._output is None:
            raise MidiException("midi not open.")

        if self._aborted:
            raise MidiException("midi aborted.")

    def close(self):
        _check_init()
        if self._output is not None:
            self._output.Close()
        self._output = None

    def abort(self):
        _check_init()
        if self._output:
            self._output.Abort()
        self._aborted = 1

    def write(self, data):
        _check_init()
        self._check_open()
        self._output.Write(data)

    def write_short(self, status, data1=0, data2=0):
        _check_init()
        self._check_open()
        self._output.WriteShort(status, data1, data2)

    def write_sys_ex(self, when, msg):
        _check_init()
        self._check_open()
        self._output.WriteSysEx(when, msg)

    def note_on(self, note, velocity, channel=0):
        if not 0 <= channel <= 15:
            raise ValueError("Channel not between 0 and 15.")
        self.write_short(0x90 + channel, note, velocity)

    def note_off(self, note, velocity=0, channel=0):
        if not 0 <= channel <= 15:
            raise ValueError("Channel not between 0 and 15.")
        self.write_short(0x80 + channel, note, velocity)

    def set_instrument(self, instrument_id, channel=0):
        if not 0 <= instrument_id <= 127:
            raise ValueError(f"Undefined instrument id: {instrument_id}")
        if not 0 <= channel <= 15:
            raise ValueError("Channel not between 0 and 15.")
        self.write_short(0xC0 + channel, instrument_id)

    def pitch_bend(self, value=0, channel=0):
        if not 0 <= channel <= 15:
            raise ValueError("Channel not between 0 and 15.")
        if not -8192 <= value <= 8191:
            raise ValueError(f"Pitch bend value must be between -8192 and +8191, not {value}.")
        value = value + 0x2000
        lsb = value & 0x7F
        msb = value >> 7
        self.write_short(0xE0 + channel, lsb, msb)


def time():
    _check_init()
    return _pypm.Time()


def midis2events(midis, device_id):
    evs = []
    for midi in midis:
        ((status, data1, data2, data3), timestamp) = midi
        event = pygame.event.Event(
            MIDIIN,
            status=status,
            data1=data1,
            data2=data2,
            data3=data3,
            timestamp=timestamp,
            vice_id=device_id,
        )
        evs.append(event)
    return evs


class MidiException(Exception):
    def __init__(self, value):
        super().__init__(value)
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


def frequency_to_midi(frequency):
    return int(round(69 + (12 * math.log(frequency / 440.0)) / math.log(2)))


def midi_to_frequency(midi_note):
    return round(440.0 * 2 ** ((midi_note - 69) * (1.0 / 12.0)), 1)


def midi_to_ansi_note(midi_note):
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    num_notes = 12
    note_name = notes[int((midi_note - 21) % num_notes)]
    note_number = (midi_note - 12) // num_notes
    return f"{note_name}{note_number}"