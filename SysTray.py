# WPU Project
# written in Python3
# written by NiclasVL
from imports import *

pythoncom.CoInitialize()
AudioUtilities.GetAllSessions()  # IDK why but it fixed some errors


class UpdateThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.audioHandler = AudioHandler()
        self.arduinoHandler = ArduinoHandler()
        self.slider_apps = []

        self.open_main_window = False

    def loadApplications(self):
        try:
            with open('applications.pickle', 'rb') as file:
                self.slider_apps = pickle.load(file)
        except FileNotFoundError:
            if not self.open_main_window:
                print("Window was not run. Starting it.")
                self.open_main_window = True
                t = threading.Thread(target=main)
                t.start()
        except Exception as e:
            self.slider_apps = None
            print(f"{e}")

    # Loop
    def run(self):
        while not self.slider_apps:
            self.loadApplications()
        while True:
            try:
                self.loadApplications()
            except:
                continue

            values = self.arduinoHandler.getArduinoValues()

            if values is None:
                continue

            try:
                self.audioHandler.updateAudios(values, self.slider_apps)
            except:
                return

            try:
                with open('data.pickle', 'wb') as file:
                    pickle.dump(values, file)
            except Exception as e:
                print("Value saving failed")
                print(f"{e}")

    # Thread Stuff
    def stop(self):
        self.arduinoHandler.ser.close()
        tread_id = None
        if hasattr(self, '_thread_id'):
            thread_id = self._thread_id
        else:
            for id, thread in threading._active.items():
                if thread is self:
                    thread_id = id
                    break

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class AudioHandler:
    def __init__(self):
        pass

    def updateAudios(self, values, sliderApps):
        audio_sessions = AudioUtilities.GetAllSessions()
        for i, audio_session in enumerate(audio_sessions):
            volume = audio_session._ctl.QueryInterface(ISimpleAudioVolume)

            for i, application in enumerate(sliderApps):
                if audio_session.Process and audio_session.Process.name() == application:
                    volume.SetMasterVolume(int(values[i]) / 100, None)

    def updateSingleAudio(self, application: str, value=1):
        audio_sessions = AudioUtilities.GetAllSessions()
        for i, audio_session in enumerate(audio_sessions):
            volume = audio_session._ctl.QueryInterface(ISimpleAudioVolume)
            if audio_session.Process and audio_session.Process.name() == application:
                volume.SetMasterVolume(int(value), None)


class ArduinoHandler:
    def __init__(self):
        self.arduino_port = self.getArduinoPort()
        self.ser = serial.Serial(port=self.arduino_port, baudrate=9600)

    def getArduinoValues(self):
        if self.arduino_port is None:  # if no Arduino is found
            self.arduino_port = self.getArduinoPort()
            return

        sleep(1/96)
        try:
            rawData = self.ser.readline().decode().strip()
        except Exception as e:
            print("Reading from Arduino Port failed")
            print(f"{e}")
            return None

        values = rawData.split("|")

        if len(values) != 5:
            # print("Error: Length of values is not 5")
            return None

        for value in values:
            if isinstance(value, int):
                print("Error: Value not INTEGER")
                return None

        try:
            for i in range(len(values)):
                values[i] = int(int(values[i]) / 1023 * 100)  # just converting them to usable things
        except:
            return None

        self.ser.flush()
        self.ser.flushInput()
        self.ser.flushOutput()
        print(f"{values}")
        return values

    def getArduinoPort(self):
        portsFound = serial.tools.list_ports.comports()

        commPort = 'None'
        numConnection = len(portsFound)

        # cycles through all connected devices and searches for a device with Arduino in its "description"
        for i in range(0, numConnection):
            strPort = str(portsFound[i])
            print(strPort)
            if 'Arduino' in strPort or 'Serielles' in strPort:
                commPort = strPort.split(' ')[0]  # takes only the first part cause that's where the COM stuff is
                print(f"Found Arduino at {commPort}")

        if commPort == 'None':
            print("No Arduino found.")
            return

        return commPort


def on_quit_callback(_systray):
    global threads
    try:
        threads[0].stop()
    except:
        print("Error while stopping Thread")


def main():
    thread = UpdateThread()
    thread.start()
    threads.append(thread)
    menu_options = ()
    systray = SysTrayIcon("GUI/mixer-icon.ico", "Lautstärke Mixer", menu_options, on_quit=on_quit_callback)
    systray.start()


threads = []
if __name__ == '__main__':
    main()
