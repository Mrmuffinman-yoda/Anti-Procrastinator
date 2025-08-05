from win10toast import ToastNotifier


class WindowsNotifier:
    """Class for sending Windows toast notifications."""

    def __init__(self):
        self.toaster = ToastNotifier()

    def send_notification(self, title: str, message: str, duration: int = 5):

        self.toaster.show_toast(title, message, duration=duration, threaded=True)


if __name__ == "__main__":
    w = WindowsNotifier()
    w.send_notification("Anti Procrastinator", "Stop playing")
