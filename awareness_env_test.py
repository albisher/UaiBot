from uaibot.core.awareness.audio_awareness import AudioAwarenessManager
from uaibot.core.awareness.bluetooth_awareness import BluetoothAwarenessManager
from uaibot.core.awareness.sensor_awareness import SensorAwarenessManager
from uaibot.core.awareness.user_routine_awareness import UserRoutineAwarenessManager
from uaibot.core.awareness.app_awareness import AppAwarenessManager
from uaibot.core.awareness.network_awareness import NetworkAwarenessManager

def print_section(title):
    print(f"\n{'='*10} {title} {'='*10}")

def print_structured_response(resp, label):
    print(f"{label}: {resp.get(label.lower(), resp)}")
    print(f"  Status: {resp.get('status', 'n/a')}")
    if resp.get('message'):
        print(f"  Message: {resp['message']}")
    if 'devices' in resp:
        print(f"  Devices: {resp['devices']}")
    if 'brightness' in resp:
        print(f"  Brightness: {resp['brightness']}")
    if 'temperature' in resp:
        print(f"  Temperature: {resp['temperature']}")
    if 'battery_level' in resp:
        print(f"  Battery Level: {resp['battery_level']}")
    if 'is_charging' in resp:
        print(f"  Is Charging: {resp['is_charging']}")
    if 'apps' in resp:
        print(f"  Apps: {resp['apps'][:3]} ... (total: {len(resp['apps'])})")
    if 'app' in resp and resp['app']:
        print(f"  Foreground App: {resp['app']}")
    if 'windows' in resp:
        print(f"  Windows: {resp['windows'][:3]} ... (total: {len(resp['windows'])})")
    if 'interfaces' in resp:
        print(f"  Interfaces: {resp['interfaces']}")
    if 'usage' in resp:
        print(f"  Usage: {dict(list(resp['usage'].items())[:2])} ...")
    if 'top_processes' in resp:
        print(f"  Top Processes: {resp['top_processes']}")
    if 'online' in resp:
        print(f"  Online: {resp['online']}")
    if 'dns' in resp:
        print(f"  DNS: {resp['dns']}")

def main():
    # Audio Awareness
    print_section("Audio Devices")
    audio_mgr = AudioAwarenessManager()
    audio_all = audio_mgr.get_audio_devices()
    audio_in = audio_mgr.get_input_devices()
    audio_out = audio_mgr.get_output_devices()
    print_structured_response(audio_all, "Devices")
    print_structured_response(audio_in, "Input Devices")
    print_structured_response(audio_out, "Output Devices")

    # Bluetooth Awareness
    print_section("Bluetooth Devices")
    bt_mgr = BluetoothAwarenessManager()
    bt_all = bt_mgr.get_bluetooth_devices()
    bt_connected = bt_mgr.get_connected_devices()
    print_structured_response(bt_all, "Bluetooth Devices")
    print_structured_response(bt_connected, "Connected Bluetooth Devices")

    # Sensor Awareness
    print_section("Sensor Data")
    sensor_mgr = SensorAwarenessManager()
    sensor_brightness = sensor_mgr.get_screen_brightness()
    sensor_temp = sensor_mgr.get_system_temperature()
    sensor_battery = sensor_mgr.get_battery_status()
    sensor_all = sensor_mgr.get_all_sensors()
    print_structured_response(sensor_brightness, "Screen Brightness")
    print_structured_response(sensor_temp, "System Temperature")
    print_structured_response(sensor_battery, "Battery Status")
    print_structured_response(sensor_all, "All Sensors")

    # App Awareness
    print_section("Application Awareness")
    app_mgr = AppAwarenessManager()
    running_apps = app_mgr.get_running_apps()
    foreground_app = app_mgr.get_foreground_app()
    app_windows = app_mgr.get_app_windows()
    print_structured_response(running_apps, "Running Apps")
    print_structured_response(foreground_app, "Foreground App")
    print_structured_response(app_windows, "App Windows")

    # Network Awareness
    print_section("Network Awareness")
    net_mgr = NetworkAwarenessManager()
    net_ifaces = net_mgr.get_active_interfaces()
    net_usage = net_mgr.get_network_usage()
    net_top = net_mgr.get_top_network_processes()
    net_status = net_mgr.get_connection_status()
    print_structured_response(net_ifaces, "Active Interfaces")
    print_structured_response(net_usage, "Network Usage")
    print_structured_response(net_top, "Top Network Processes")
    print_structured_response(net_status, "Connection Status")

    # User Routine Awareness
    print_section("User Routine")
    user_mgr = UserRoutineAwarenessManager()
    user_routine = user_mgr.get_user_routine()
    user_active = user_mgr.is_user_active()
    print("User routine:", user_routine)
    print("Is user active?", user_active)

    # Summary of what the system DOES know
    print_section("SYSTEM AWARENESS SUMMARY")
    if audio_all.get('status') == 'ok' and audio_all['devices']:
        print(f"Audio devices detected: {[d['name'] for d in audio_all['devices']]}")
    if audio_in.get('status') == 'ok' and audio_in['devices']:
        print(f"Input audio devices: {[d['name'] for d in audio_in['devices']]}")
    if audio_out.get('status') == 'ok' and audio_out['devices']:
        print(f"Output audio devices: {[d['name'] for d in audio_out['devices']]}")
    if bt_all.get('status') == 'ok' and bt_all['devices']:
        print(f"Bluetooth devices detected: {[d['address'] for d in bt_all['devices']]}")
    if bt_connected.get('status') == 'ok' and bt_connected['devices']:
        print(f"Connected Bluetooth devices: {[d['address'] for d in bt_connected['devices']]}")
    if sensor_brightness.get('status') == 'ok' and sensor_brightness.get('brightness') is not None:
        print(f"Screen brightness: {sensor_brightness['brightness']}")
    if sensor_temp.get('status') == 'ok' and sensor_temp.get('temperature') is not None:
        print(f"System temperature: {sensor_temp['temperature']}°C")
    if sensor_battery.get('status') == 'ok' and sensor_battery.get('battery_level') is not None:
        print(f"Battery level: {sensor_battery['battery_level']}% (Charging: {sensor_battery.get('is_charging')})")
    if sensor_all.get('status') in ('ok', 'partial'):
        print(f"Sensor summary: {sensor_all}")
    if running_apps.get('status') == 'ok' and running_apps.get('apps'):
        app_samples = []
        for a in running_apps['apps'][:3]:
            app_samples.append(f"{a['name']} (PID {a['pid']}, CPU {a['cpu_percent']}%, RSS {a['memory_rss']})")
        print(f"Running apps (sample): [{', '.join(app_samples)}] ... (total: {len(running_apps['apps'])})")
    if foreground_app.get('status') == 'ok' and foreground_app.get('app'):
        fa = foreground_app['app']
        print(f"Foreground app: {fa['name']} (PID {fa['pid']}, Title: {fa['window_title']}, CPU: {fa['cpu_percent']}%, RSS: {fa['memory_rss']})")
    if app_windows.get('status') == 'ok' and app_windows.get('windows'):
        print(f"Open app windows (sample): {app_windows['windows'][:3]} ... (total: {len(app_windows['windows'])})")
    if net_ifaces.get('status') == 'ok' and net_ifaces.get('interfaces'):
        print(f"Active network interfaces: {[i['name'] for i in net_ifaces['interfaces']]}")
    if net_usage.get('status') == 'ok' and net_usage.get('usage'):
        print(f"Network usage (sample): {dict(list(net_usage['usage'].items())[:2])}")
    if net_top.get('status') == 'ok' and net_top.get('top_processes'):
        print(f"Top network processes: {net_top['top_processes']}")
    if net_status.get('status') == 'ok':
        print(f"Network online: {net_status['online']}, DNS: {net_status['dns']}")
    print(f"User routine: {user_routine}")
    print(f"User is currently {'active' if user_active else 'inactive'}.")

if __name__ == "__main__":
    main() 