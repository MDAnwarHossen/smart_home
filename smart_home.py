import flet as ft
from datetime import datetime


def main(page: ft.Page):
    page.title = "Smart Home Controller"
    page.padding = 20
    page.theme_mode = "light"
    page.window_width = 950
    page.window_height = 700

    # -------------------------
    # DEVICE STATES
    # -------------------------
    light_on = False
    door_locked = True
    thermostat_value = 22
    fan_speed = 0

    # -------------------------
    # UI CONTROLS THAT WE UPDATE
    # -------------------------
    light_status_text = ft.Text()
    door_status_text = ft.Text()
    thermostat_status_text = ft.Text()
    fan_status_text = ft.Text()

    light_card = None
    door_card = None
    thermostat_card = None
    fan_card = None

    # -------------------------
    # LOGS
    # -------------------------
    device_logs = {"light": [], "door": [], "thermostat": [], "fan": []}
    action_log = []
    power_data = []

    # -------------------------
    # POWER SIMULATION
    # -------------------------
    def calc_power():
        power = 0
        if light_on:
            power += 20
        if not door_locked:
            power += 5
        power += (thermostat_value - 18) * 2
        power += fan_speed * 10
        return power

    def record_action(device_key, device_id, action):
        time_str = datetime.now().strftime("%H:%M:%S")
        device_logs[device_key].append(f"{time_str} – {action} (User)")
        action_log.append(
            {"time": time_str, "device": device_id, "action": action, "user": "User"})
        power_data.append({"x": len(power_data), "y": calc_power()})

    # -------------------------
    # GRADIENT HELPERS
    # -------------------------
    def _lerp(a, b, t):
        return int(a + (b - a) * t)

    def _interpolate_color(hex_a, hex_b, t):
        a = int(hex_a[1:3], 16), int(hex_a[3:5], 16), int(hex_a[5:7], 16)
        b = int(hex_b[1:3], 16), int(hex_b[3:5], 16), int(hex_b[5:7], 16)
        r = _lerp(a[0], b[0], t)
        g = _lerp(a[1], b[1], t)
        bl = _lerp(a[2], b[2], t)
        return f"#{r:02x}{g:02x}{bl:02x}"

    def temp_gradient(value, min_v=15, max_v=30):
        t = (value - min_v) / (max_v - min_v)
        t = max(0.0, min(1.0, t))
        cold = "#9ad1ff"
        hot = "#ff6b6b"
        mid_color = _interpolate_color(cold, hot, t)
        light_variant = _interpolate_color(mid_color, "#ffffff", 0.6)
        return ft.LinearGradient(colors=[mid_color, light_variant])

    def fan_gradient(speed, min_s=0, max_s=3):
        t = (speed - min_s) / (max_s - min_s) if max_s != min_s else 0
        t = max(0.0, min(1.0, t))
        low = "#f0f0f0"
        high = "#ff6b6b"
        mid_color = _interpolate_color(low, high, t)
        light_variant = _interpolate_color(mid_color, "#ffffff", 0.5)
        return ft.LinearGradient(colors=[mid_color, light_variant])

    def light_gradient(is_on):
        off_color = "#FFF7CC"
        on_color = "#FFD700"
        mid_color = on_color if is_on else off_color
        light_variant = _interpolate_color(mid_color, "#ffffff", 0.4)
        return ft.LinearGradient(colors=[mid_color, light_variant])

    def door_gradient(is_locked):
        locked_color = "#98FB98"
        unlocked_color = "#FF6B6B"
        mid_color = locked_color if is_locked else unlocked_color
        light_variant = _interpolate_color(mid_color, "#ffffff", 0.4)
        return ft.LinearGradient(colors=[mid_color, light_variant])

    # -------------------------
    # HEADER TABS
    # -------------------------
    def header(tab):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Smart Home Controller", size=26, weight="bold"),
                ft.Row(
                    controls=[
                        ft.TextButton("Overview",
                                      style=ft.ButtonStyle(
                                          color=ft.Colors.BLUE if tab == "overview" else ft.Colors.BLACK),
                                      on_click=lambda e: page.go("/")),
                        ft.TextButton("Statistics",
                                      style=ft.ButtonStyle(
                                          color=ft.Colors.BLUE if tab == "stats" else ft.Colors.BLACK),
                                      on_click=lambda e: page.go("/stats")),
                    ]
                )
            ]
        )

    # -------------------------
    # ACTION FUNCTIONS
    # -------------------------
    def toggle_light(e):
        nonlocal light_on, light_card
        light_on = not light_on
        record_action("light", "light1", "Turn ON" if light_on else "Turn OFF")
        light_status_text.value = f"Status: {'ON' if light_on else 'OFF'}"
        e.control.text = "Turn OFF" if light_on else "Turn ON"
        light_card.gradient = light_gradient(light_on)
        light_status_text.update()
        light_card.update()
        e.control.update()
        page.update()

    def toggle_door(e):
        nonlocal door_locked, door_card
        door_locked = not door_locked
        record_action("door", "door1", "Unlock" if not door_locked else "Lock")
        door_status_text.value = f"Door: {'LOCKED' if door_locked else 'UNLOCKED'}"
        e.control.text = "Unlock" if door_locked else "Lock"
        door_card.gradient = door_gradient(door_locked)
        door_status_text.update()
        door_card.update()
        e.control.update()
        page.update()

    def change_temp(e):
        nonlocal thermostat_value, thermostat_card
        thermostat_value = int(e.control.value)
        record_action("thermostat", "thermo1", f"Set {thermostat_value} °C")
        thermostat_status_text.value = f"Set point: {thermostat_value} °C"
        thermostat_card.gradient = temp_gradient(thermostat_value)
        thermostat_status_text.update()
        thermostat_card.update()
        page.update()

    def change_fan(e):
        nonlocal fan_speed, fan_card
        fan_speed = int(e.control.value)
        record_action("fan", "fan1", f"Speed {fan_speed}")
        fan_status_text.value = f"Fan speed: {fan_speed}"
        fan_card.gradient = fan_gradient(fan_speed)
        fan_status_text.update()
        fan_card.update()
        page.update()

    # -------------------------
    # DETAILS PAGE
    # -------------------------
    def make_details(device_key, title, device_id, device_type, state):
        return ft.View(
            route=f"/details/{device_key}",
            controls=[
                ft.Text("Smart Home Controller", size=26, weight="bold"),
                ft.Container(height=10),
                ft.Container(
                    width=600,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(f"{title} details",
                                    size=22, weight="bold"),
                            ft.Text(f"ID: {device_id}"),
                            ft.Text(f"Type: {device_type}"),
                            ft.Text(f"State: {state}", weight="bold"),
                            ft.Container(height=10),
                            ft.Text("Recent actions:", size=20, weight="bold"),
                            ft.Column([ft.Text(x)
                                      for x in device_logs[device_key]]),
                            ft.Container(height=10),
                            ft.TextButton("Back to overview",
                                          on_click=lambda e: page.go("/"))
                        ]
                    )
                )
            ]
        )

    # -------------------------
    # PAGE ROUTING
    # -------------------------
    def route_change(route):
        nonlocal light_card, door_card, thermostat_card, fan_card
        page.views.clear()

        # always sync status text
        light_status_text.value = f"Status: {'ON' if light_on else 'OFF'}"
        door_status_text.value = f"Door: {'LOCKED' if door_locked else 'UNLOCKED'}"
        thermostat_status_text.value = f"Set point: {thermostat_value} °C"
        fan_status_text.value = f"Fan speed: {fan_speed}"

        if page.route == "/":
            # Light card
            light_card = ft.Container(
                width=360,
                gradient=light_gradient(light_on),
                border_radius=10,
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text("Living Room Light", size=18, weight="bold"),
                        light_status_text,
                        ft.Text("Tap to switch the light."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details", on_click=lambda e: page.go("/details/light")),
                                ft.FilledButton(
                                    "Turn ON" if not light_on else "Turn OFF", on_click=toggle_light)
                            ]
                        )
                    ]
                )
            )

            # Door card
            door_card = ft.Container(
                width=360,
                gradient=door_gradient(door_locked),
                border_radius=10,
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text("Front Door", size=18, weight="bold"),
                        door_status_text,
                        ft.Text("Tap to lock/unlock the door."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details", on_click=lambda e: page.go("/details/door")),
                                ft.FilledButton(
                                    "Unlock" if door_locked else "Lock", on_click=toggle_door)
                            ]
                        )
                    ]
                )
            )

            # Thermostat card
            thermostat_card = ft.Container(
                width=360,
                gradient=temp_gradient(thermostat_value),
                border_radius=10,
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text("Thermostat", size=18, weight="bold"),
                        thermostat_status_text,
                        ft.Text("Use slider to change temperature."),
                        ft.Slider(min=15, max=30, value=thermostat_value,
                                  on_change=change_temp),
                        ft.TextButton("Details", on_click=lambda e: page.go(
                            "/details/thermostat"))
                    ]
                )
            )

            # Fan card
            fan_card = ft.Container(
                width=360,
                gradient=fan_gradient(fan_speed),
                border_radius=10,
                padding=15,
                content=ft.Column(
                    controls=[
                        ft.Text("Ceiling Fan", size=18, weight="bold"),
                        fan_status_text,
                        ft.Text("0 = OFF, 3 = MAX."),
                        ft.Slider(min=0, max=3, divisions=3,
                                  value=fan_speed, on_change=change_fan),
                        ft.TextButton(
                            "Details", on_click=lambda e: page.go("/details/fan"))
                    ]
                )
            )

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        header("overview"),
                        ft.Container(height=10),
                        ft.Text("On/Off devices", size=20, weight="bold"),
                        ft.Row(controls=[light_card, door_card], spacing=20),
                        ft.Container(height=20),
                        ft.Text("Slider controlled devices",
                                size=20, weight="bold"),
                        ft.Row(controls=[thermostat_card,
                               fan_card], spacing=20),
                    ]
                )
            )

        # ------------------- STATISTICS -----------------------
        elif page.route == "/stats":
            if power_data:
                data_points = [ft.LineChartDataPoint(
                    p["x"], p["y"]) for p in power_data]
                max_x = max(p["x"] for p in power_data)
                max_y = max(p["y"] for p in power_data)
            else:
                data_points = [ft.LineChartDataPoint(0, 0)]
                max_x = 10
                max_y = 10

            chart = ft.LineChart(
                data_series=[ft.LineChartData(data_points)],
                min_x=0,
                max_x=max_x,
                min_y=0,
                max_y=max_y,
                border=ft.border.all(1, ft.Colors.GREY_400),
                expand=True
            )

            stats_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Time")),
                    ft.DataColumn(ft.Text("Device")),
                    ft.DataColumn(ft.Text("Action")),
                    ft.DataColumn(ft.Text("User")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(r["time"])),
                            ft.DataCell(ft.Text(r["device"])),
                            ft.DataCell(ft.Text(r["action"])),
                            ft.DataCell(ft.Text(r["user"])),
                        ]
                    )
                    for r in action_log
                ]
            )

            page.views.append(
                ft.View(
                    route="/stats",
                    controls=[
                        header("stats"),
                        ft.Text("Power consumption (simulated)",
                                size=20, weight="bold"),
                        ft.Container(
                            height=260,
                            padding=10,
                            bgcolor=ft.Colors.WHITE,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            content=chart
                        ),
                        ft.Container(height=20),
                        ft.Text("Action log", size=20, weight="bold"),
                        ft.Container(
                            padding=10,
                            bgcolor=ft.Colors.WHITE,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            content=stats_table
                        )
                    ]
                )
            )

        # ------------------- DETAILS -----------------------
        elif page.route.startswith("/details/"):
            key = page.route.split("/")[-1]
            details_map = {
                "light": ("Living Room Light", "light1", "light", "ON" if light_on else "OFF"),
                "door": ("Front Door", "door1", "door", "LOCKED" if door_locked else "UNLOCKED"),
                "thermostat": ("Thermostat", "thermo1", "thermostat", f"{thermostat_value}°C"),
                "fan": ("Ceiling Fan", "fan1", "fan", f"Speed {fan_speed}"),
            }
            if key in details_map:
                page.views.append(make_details(key, *details_map[key]))

        page.update()

    page.on_route_change = route_change
    page.go("/")


ft.app(target=main)
