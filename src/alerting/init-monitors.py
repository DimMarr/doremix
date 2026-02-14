from uptime_kuma_api import UptimeKumaApi
import os
from uptime_kuma_api.api import _convert_monitor_input, _check_arguments_monitor, Event


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Check if env variables exist
if not os.environ.get("UPTIME_USERNAME"):
    print(f"{bcolors.FAIL} ENV variable UPTIME_USERNAME missing in .env")
    raise Exception("ENV variable UPTIME_USERNAME missing in .env")
if not os.environ.get("UPTIME_PASSWORD"):
    print(f"{bcolors.FAIL} ENV variable UPTIME_PASSWORD missing in .env")
    raise Exception("ENV variable UPTIME_PASSWORD missing in .env")

api = UptimeKumaApi(os.environ.get("UPTIME_URL", "http://localhost:3001"))
api.login(os.environ["UPTIME_USERNAME"], os.environ["UPTIME_PASSWORD"])

# Define monitors to create
monitors = [
    {
        "name": "Production API",
        "type": "http",
        "url": "https://api.example.com/health",
        "interval": 60,
        "maxretries": 3,
    }
]

# Create each monitor
for monitor in monitors:
    existing_monitors = api.get_monitors()
    monitor_already_exists = False

    """
    Check if monitor already exist before adding them
    Monitor already exists if :
        - monitor with same url already exists
        - monitor with same type and hostname already exist
    """
    for existing_monitor in existing_monitors:
        if (
            ("key" not in monitor or monitor["url"] == existing_monitor["url"])
            and "type" not in monitor
            or monitor["type"] == existing_monitor["type"]
            and "hostname" not in monitor
            or monitor["hostname"] == existing_monitor["hostname"]
        ):
            url = ("url : " + monitor["url"] + " ") if "url" in monitor else ""
            url += (
                ("hostname : " + monitor["hostname"] + " ")
                if "hostname" in monitor
                else ""
            )
            url += ("type : " + monitor["type"]) if "type" in monitor else ""

            print(
                f"{bcolors.WARNING} WARNING: Monitor with {url} already exists. Ignoring this monitor."
            )
            monitor_already_exists = True
            break

    if monitor_already_exists:
        continue

    try:
        data = api._build_monitor_data(**monitor)
        # ensures a conditions attribute
        if "conditions" not in data or data.get("conditions") is None:
            data["conditions"] = []

        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        with api.wait_for_event(Event.MONITOR_LIST):
            result = api._call("add", data)
        print(
            f"{bcolors.OKGREEN}Created monitor: {monitor['name']} (ID: {result.get('monitorID')})"
        )
    except Exception as e:
        print(f"{bcolors.FAIL}Failed to create monitor {monitor.get('name')}: {e}")

api.disconnect()
