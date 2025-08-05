import psutil
import datetime
import requests

limited_apps = {
    "leagueclient.exe": "League of legends",
}


def main():
    print("hello world")

    for proc in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"]
            start_time = datetime.datetime.fromtimestamp(proc.info["create_time"])
            if "leagueclient.exe" in proc.info["name"].lower():
                print(f"{name} (PID {pid}) started at {start_time}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def get_open_tabs():
    try:
        response = requests.get("http://localhost:9222/json")
        tabs = response.json()

        urls = [tab.get("url", "") for tab in tabs if tab.get("url").startswith("http")]
        return urls
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    main()

    urls = get_open_tabs()
    if urls:
        print("Currently open websites:")
        for url in urls:
            print(f"- {url}")
    else:
        print("No tabs found or Chrome is not running with remote debugging.")
