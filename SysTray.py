# WPU Project
# written in Python3
# written by NiclasVL
from imports import *  # importiert alle Bibliotheken

pythoncom.CoInitialize()
AudioUtilities.GetAllSessions()


class UpdateThread(threading.Thread):  # Dies ist der Thread der immer laufen wird
    def __init__(self):
        threading.Thread.__init__(self)
        self.audioHandler = AudioHandler()  # Erstellt ein Objekt der Klasse AudioHandler
        self.arduinoHandler = ArduinoHandler()  # Erstellt ein Objekt der Klasse ArduinoHandler
        self.slider_apps = []

        self.open_main_window = False

    def loadApplications(self):  # lädt alle Programme
        try:
            # lädt die Config-Datei, welche Programme gesteuert werden sollen
            with open('applications.pickle', 'rb') as file:
                self.slider_apps = pickle.load(file)
        except Exception as e:  # Falls es irgendwelche Fehler gibt
            self.slider_apps = None
            print(f"{e}")

    # läuft durchgehend
    def run(self):
        while not self.slider_apps:
            self.loadApplications()  # stellt sicher, dass die Programme geladen werden
        while True:
            try:
                self.loadApplications()  # stellt sicher, dass die Programme immer UpToDate sind (könnten währendessen geändert werden)
            except:
                continue  # fang von vorne an (beim while True)

            values = self.arduinoHandler.getArduinoValues()  # holt sich die Daten vom Arduino

            if values is None:  # Falls es einen Fehler gab beim auslesen (kein Arduino etc.)
                continue  # fang von vorne an (beim while True)

            try:
                self.audioHandler.updateAudios(values, self.slider_apps)  # updated die Audioeinstellungen der Programme
            except:
                continue

            try:
                with open('data.pickle', 'wb') as file:  # schreibt sie für das Fenster in eine Datei
                    pickle.dump(values, file)
            except Exception as e:  # falls irgendein Fehler auftritt
                print("Value saving failed")
                print(f"{e}")

    # Zum Stoppen
    def stop(self):
        self.arduinoHandler.ser.close()  # schließt die Verbindung zum Arduino
        # versucht den Thread zu finden und zu schließen
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


class AudioHandler:  # Handelt die Lautstärken
    def __init__(self):
        pass  # Es gibt an dieser Stelle nichts zu initialisieren

    def updateAudios(self, values, sliderApps):  # nimmt Daten und Programmnamen an
        audio_sessions = AudioUtilities.GetAllSessions()  # holt sich alle Audiosessions in eine liste
        for i, audio_session in enumerate(audio_sessions):  # geht durch alle durch
            for i, application in enumerate(sliderApps):  # geht durch alle Programme durch
                if audio_session.Process and audio_session.Process.name() == application:  # kuckt ob der Name der Audiosession mit einem der Programme übereinstimmt
                    volume = audio_session._ctl.QueryInterface(ISimpleAudioVolume)  # holt sich das Volume
                    volume.SetMasterVolume(int(values[i]) / 100, None)  # verändert die Lautstärke nach den Daten

    def updateSingleAudio(self, application: str, value=1):  # nimmt ein Programmnamen und eine (optional) Lautstärke an (Default = 1)
        audio_sessions = AudioUtilities.GetAllSessions()  # holt sich alle Audiosessions in eine liste
        for i, audio_session in enumerate(audio_sessions):  # geht durch alle durch
            if audio_session.Process and audio_session.Process.name() == application:  # kuckt ob der Name der Audiosession dem Programm übereinstimmt
                volume = audio_session._ctl.QueryInterface(ISimpleAudioVolume)  # holt sich das Volume
                volume.SetMasterVolume(int(value), None)  # verändert die Lautstärke nach den Daten


class ArduinoHandler:  # geht mit dem Arduino um
    def __init__(self):
        self.arduino_port = self.getArduinoPort()  # versucht einen Arduino zu finden
        self.ser = serial.Serial(port=self.arduino_port, baudrate=9600)  # baut eine Verbindung auf

    def getArduinoValues(self):  # gibt die Daten vom Arduino aus
        if self.arduino_port is None:  # wenn kein Arduino gefunden wurde
            self.arduino_port = self.getArduinoPort()
            return

        sleep(1/96)  # warte auf Daten
        try:
            rawData = self.ser.readline().decode().strip()  # liest den serriellen Port und macht ihn benutzbar
        except Exception as e:  # falls ein Fehler auftritt
            print("Reading from Arduino Port failed")
            print(f"{e}")
            return None

        values = rawData.split("|")  # teilt die Daten in eine Liste

        if len(values) != 5:  # falls die Liste nicht 5 lang ist
            return None

        for value in values:  # schaut nach ob alle Daten auch wirklich benutzbar sind
            if isinstance(value, int):
                return None

        try:
            for i in range(len(values)):
                values[i] = int(int(values[i]) / 1023 * 100)  # umrechnen zu Prozent
        except:
            return None

        # macht den serriellen Port leer damit kein Lag entsteht
        self.ser.flush()
        self.ser.flushInput()
        self.ser.flushOutput()

        return values

    def getArduinoPort(self):  # versucht den Arduino zu finden
        portsFound = serial.tools.list_ports.comports()  # listet alle angeschlossenen Geräte auf

        commPort = 'None'
        numConnection = len(portsFound)

        # geht durch alle angeschlossenen Geräte und sucht nach einem Gerät mit Arduino o.ä. in der "Beschreibung"
        for i in range(0, numConnection):
            strPort = str(portsFound[i])
            print(strPort)
            if 'Arduino' in strPort or 'Serielles' in strPort:
                commPort = strPort.split(' ')[0]  # nimmt nur den ersten Teil, weil dort die COM-Daten stehen
                print(f"Found Arduino at {commPort}")

        if commPort == 'None':
            print("No Arduino found.")
            return

        return commPort


def on_quit_callback(_systray):  # falls der Systray gestoppt wird
    global threads
    try:
        threads[0].stop()
    except:
        print("Error while stopping Thread")


def main():  # Main Funktion
    thread = UpdateThread()
    thread.start()
    threads.append(thread)
    menu_options = ()
    systray = SysTrayIcon("GUI/mixer-icon.ico", "Lautstärke Mixer", menu_options, on_quit=on_quit_callback)
    systray.start()


threads = []
if __name__ == '__main__':
    main()
