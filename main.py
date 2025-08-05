import psutil
import datetime
import time
import requests

from lib.winnotif import WindowsNotifier
from lib.pushover import PushOver

limited_apps = {
    "leagueclient.exe": "League of Legends",
    "valorant.exe": "Valorant",
    # add more if needed
}
limited_websites = {"www.youtube.com": "YouTube"}

APP_LIMITS = 45  # mins
WEB_LIMITS = 60  # mins

LOOP_SLEEP = 5 * 60  # seconds


def get_open_tabs():
    try:
        response = requests.get("http://localhost:9222/json")
        tabs = response.json()

        urls = [
            tab.get("url", "")
            for tab in tabs
            if tab.get("url").startswith("http") and "sw.js" not in tab.get("url", "")
        ]
        return urls
    except Exception as e:
        print(f"Error: {e}")
        return []


class Detector:
    def __init__(self):
        self.webmemory = {}  # site -> datetime
        self.appmemory = {}  # exe -> datetime
        self.sentbook = set()  # label -> notified
        self.winnotif = WindowsNotifier()
        self.pushnotify = PushOver()

        self.loop()

    def notify(self, message: str):
        self.winnotif.send_notification("Limits", message)
        self.pushnotify.send(message)

    def check_limited_websites(self) -> list:
        now = datetime.datetime.now()
        running_limited_websites = []
        urls = get_open_tabs()

        for url in urls:
            for site, label in limited_websites.items():
                if site in url:
                    if site not in self.webmemory:
                        self.webmemory[site] = now  # First seen

                    duration_minutes = (now - self.webmemory[site]).total_seconds() / 60

                    print(
                        f"{label} ({site}) has been open for {duration_minutes:.1f} minutes"
                    )

                    running_limited_websites.append(
                        {
                            "site": site,
                            "label": label,
                            "url": url,
                            "duration_minutes": duration_minutes,
                        }
                    )

        # Cleanup memory for closed tabs
        to_remove = [
            site for site in self.webmemory if all(site not in url for url in urls)
        ]
        for site in to_remove:
            del self.webmemory[site]

        return running_limited_websites

    def check_limited_apps(self) -> list:
        now = datetime.datetime.now()
        running_limited_apps = []

        # Track currently running limited apps
        running_exes = set()

        for proc in psutil.process_iter(["pid", "name", "create_time"]):
            try:
                name = proc.info["name"].lower()
                for exe, label in limited_apps.items():
                    if exe in name:
                        running_exes.add(exe)

                        if exe not in self.appmemory:
                            self.appmemory[exe] = now  # First time we saw it

                        duration_minutes = (
                            now - self.appmemory[exe]
                        ).total_seconds() / 60

                        print(
                            f"{label} ({exe}) has been running for {duration_minutes:.1f} minutes"
                        )

                        running_limited_apps.append(
                            {
                                "exe": exe,
                                "label": label,
                                "duration_minutes": duration_minutes,
                            }
                        )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Clean up appmemory for apps that are no longer running
        to_remove = [exe for exe in self.appmemory if exe not in running_exes]
        for exe in to_remove:
            del self.appmemory[exe]

        return running_limited_apps

    def loop(self):
        while True:
            time.sleep(LOOP_SLEEP)

            app_data = self.check_limited_apps()
            web_data = self.check_limited_websites()

            for app in app_data:
                if (
                    app["duration_minutes"] > APP_LIMITS
                    and app["label"] not in self.sentbook
                ):
                    self.notify(f"Time limit reached for app: {app['label']}")
                    print("User notified of time limit breach")
                    self.sentbook.add(app["label"])

            for webapp in web_data:
                if (
                    webapp["duration_minutes"] > WEB_LIMITS
                    and webapp["label"] not in self.sentbook
                ):
                    self.notify(f"Time limit reached for web app: {webapp['label']}")
                    print("User notified of time limit breach")
                    self.sentbook.add(webapp["label"])


if __name__ == "__main__":
    d = Detector()
