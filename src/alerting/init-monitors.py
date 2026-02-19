from uptime_kuma_api import UptimeKumaApi
import os
import json
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

api = UptimeKumaApi("http://uptime:3001")
api.login(os.environ["UPTIME_USERNAME"], os.environ["UPTIME_PASSWORD"])

# Load monitors from JSON file
monitors_file = "monitors.json"
try:
    with open(monitors_file, "r") as f:
        monitors = json.load(f)
    print(f"{bcolors.OKGREEN}Loaded {len(monitors)} monitor(s) from {monitors_file}")
except FileNotFoundError:
    print(f"{bcolors.FAIL}Error: {monitors_file} not found")
    raise
except json.JSONDecodeError as e:
    print(f"{bcolors.FAIL}Error parsing {monitors_file}: {e}")
    raise
except Exception as e:
    print(f"{bcolors.FAIL}Error loading monitors from {monitors_file}: {e}")
    raise

# Load notifications from JSON file
notifications_file = "notifications.json"
notifications = []
try:
    with open(notifications_file, "r") as f:
        notifications = json.load(f)
    print(
        f"{bcolors.OKGREEN}Loaded {len(notifications)} notification(s) from {notifications_file}"
    )
except FileNotFoundError:
    print(
        f"{bcolors.WARNING}Warning: {notifications_file} not found, skipping notifications"
    )
except json.JSONDecodeError as e:
    print(f"{bcolors.FAIL}Error parsing {notifications_file}: {e}")
    raise
except Exception as e:
    print(f"{bcolors.FAIL}Error loading notifications from {notifications_file}: {e}")
    raise

# Create notifications first
notification_id_mapping = {}
for notification in notifications:
    existing_notifications = api.get_notifications()
    notification_already_exists = False

    # Check if notification already exists by name
    for existing_notification in existing_notifications:
        if notification["name"] == existing_notification["name"]:
            print(
                f"{bcolors.WARNING} WARNING: Notification '{notification['name']}' already exists. Using existing ID: {existing_notification['id']}"
            )
            notification_id_mapping[notification["name"]] = existing_notification["id"]
            notification_already_exists = True
            break

    if notification_already_exists:
        continue

    try:
        result = api.add_notification(**notification)
        notification_id = result.get("id")
        notification_id_mapping[notification["name"]] = notification_id
        print(
            f"{bcolors.OKGREEN}Created notification: {notification['name']} (ID: {notification_id})"
        )
    except Exception as e:
        print(
            f"{bcolors.FAIL}Failed to create notification {notification.get('name')}: {e}"
        )
        continue

# Create each monitor
for monitor in monitors:
    existing_monitors = api.get_monitors()
    monitor_already_exists = False

    # Resolve notification names to IDs in notificationIDList
    if "notificationIDList" in monitor and "notificationNames" in monitor:
        resolved_ids = []
        for name in monitor["notificationNames"]:
            if name in notification_id_mapping:
                resolved_ids.append(notification_id_mapping[name])
            else:
                print(
                    f"{bcolors.WARNING} WARNING: Notification '{name}' not found for monitor '{monitor['name']}'"
                )
        monitor["notificationIDList"] = resolved_ids
        # Remove the helper field
        del monitor["notificationNames"]

    """
    Check if monitor already exist before adding them
    Monitor already exists if :
        - monitor with same url already exists
        - monitor with same type and hostname already exist
    """
    for existing_monitor in existing_monitors:
        print(monitor["url"])
        if (
            monitor["url"] == existing_monitor["url"]
            and monitor["name"] == existing_monitor["name"]
        ):
            print(
                f"{bcolors.WARNING} WARNING: Monitor with  url: {monitor["url"]} and name: {monitor['name']} already exists. Ignoring this monitor."
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
