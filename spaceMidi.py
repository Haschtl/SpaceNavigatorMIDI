import pyspacenavigator
import time
import mido
import rtmidi

rtmidiBackend = mido.Backend('mido.backends.rtmidi')
# portmidi = mido.Backend('mido.backends.portmidi')
ccMapping = {"x": 11, "y": 12, "z": 13, "roll": 14, "pitch": 15, "yaw": 16, "buttons": [17,18]}
class SpaceMidi:
    def __init__(self):
        # self.axes = ["x", "y", "z", "roll", "pitch", "yaw"]
        self.axes = ["roll", "pitch", "yaw"]
        in_port, out_port = self.findPorts("SpaceMidi")
        try:
            self.input = rtmidiBackend.open_input(in_port)
            self.output = rtmidiBackend.open_output(out_port)
        except OSError as e:
            print(f'Check if these ports exist: In: {in_port}, Out: {out_port}')
        self.running=True
        success = pyspacenavigator.open()
        while not success:
            success = pyspacenavigator.open()
            time.sleep(1)
            print("Waiting for SpaceNavigator...")
        self.led=True
        self.loop()

    def findPorts(self, name="SpaceMidi"):
        out_ports = rtmidi.MidiOut().get_ports()
        in_ports = rtmidi.MidiIn().get_ports()
        print(f'In: {", ".join(in_ports)}')
        print(f'Out: {", ".join(out_ports)}')
        out_port=""
        in_port = ""
        for port in out_ports:
            if name in port:
                out_port = port
                break
        for port in in_ports:
            if name in port:
                in_port = port
                break
        return in_port,out_port
        
    def status(self):
        newState=self.read()
        print(newState["x"], newState["y"], newState["z"], newState["roll"],
              newState["pitch"], newState["yaw"], newState["buttons"])
        
    def read(self):
        rawState=pyspacenavigator.read()
        state = {"x": scale(rawState.x), "y": scale(rawState.y), "z": scale(rawState.z), "roll": scale(rawState.roll),
                 "pitch": scale(rawState.pitch), "yaw": scale(rawState.yaw), "buttons": rawState.buttons}
        return state
    def loop(self):
        led_state=True
        state={"x":0,"y":0,"z":0,"roll":0,"pitch":0,"yaw":0,"buttons":[]}
        while self.running:
            if (led_state != self.led):
                led_state=self.led
                pyspacenavigator.set_led(self.led)
            
            newState = self.read()
            for val in self.axes:
                if newState[val]!=state[val]:
                    msg = mido.Message('control_change', channel=0, control=ccMapping[val],
                                       value=newState[val])
                    # msg = mido.Message('pitchwheel', channel=0, pitch=99)
                    self.output.send(msg)
                    # print(f'{val}: {newState[val]}')
            state=newState
            # self.led= not self.led
            time.sleep(0.01)


def scale(value: float, newMax=127, newMin=0):
    oldMax=1
    oldMin=-1
    value=max(oldMin,min(oldMax,value))
    # try:
    #     assert value <= oldMax
    #     assert value >= oldMin
    # except AssertionError:
    #     print(f'AssertionError: {value} <= {oldMax}')
    #     print(f'AssertionError: {value} >= {oldMin}')
    oldRange = (oldMax - oldMin)
    if oldRange == 0:
        newValue = newMin
    else:
        newRange = (newMax - newMin)
        newValue = (((value - oldMin) * newRange) / oldRange) + newMin
    return round(newValue)
if __name__ == "__main__":
    sm=SpaceMidi()