import flet as ft
import Algorithm as algo
from BackEnd import message_condenser, unpack_message, doctor_matching
import uuid
import time

cases = [] #This list will store all the help cases.


def main(page: ft.Page):
    #print(algo.specialty_to_subspecialties)
    page.title = "Doctor Communication App"
    page.theme_mode = "light"
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = False
    page.update()

    #Variables
    global current_user_type
    current_user_type = None  # 'international' or 'gazan'
    global user_profile
    user_profile = {
        "username": "",
        "password": "",
        "specialties": [],
        "languages": [],
        "available": True  # This is the default value
    }
    global new_cases
    new_cases = []  # Store new cases to be shown to international doctors

  
    global profile_edit_mode
    profile_edit_mode = False


    def route_change(e):
        page.views.clear()
        route = page.route

        if route == "/":
            page.views.append(landing_view())
        elif route == "/login":
            page.views.append(login_view())
        elif route == "/profile_setup":
            page.views.append(profile_setup_view())
        elif route == "/international_main":
            page.views.append(international_main_view())
        elif route == "/gazan_main":
            page.views.append(gazan_main_view())
        elif route == "/chat":
            page.views.append(chat_view())
        elif route == "/new_case_popup":
            page.views.append(new_case_popup_view())
        elif route == "/help_request":
            page.views.append(help_request_view())
        elif route == "/connect_device":
            page.views.append(connect_device_view())
        elif route == "/profile":
            page.views.append(profile_view())
        page.update()

    page.on_route_change = route_change
    page.go("/")

    # ========= Helper Functions =========
    def set_user_type_and_go(user_type, route):
        global current_user_type
        current_user_type = user_type
        page.go(route)
    
    def build_profile_editor(is_editing, on_submit, initial_data):
        specialties = list(algo.specialty_to_subspecialties.keys())

        selected_specialties = initial_data.get("specialties", []).copy()
        selected_languages = initial_data.get("languages", []).copy()

        username_field = ft.TextField(label="Username", width=360, value=initial_data.get("username", ""), read_only=not is_editing)
        password_field = ft.TextField(label="Password", password=True, width=360, value=initial_data.get("password", ""), read_only=not is_editing)
        language_input = ft.TextField(label="Language", width=360, visible=is_editing)

        specialty_dropdown = ft.Dropdown(
            label="Specialty",
            width=360,
            visible=is_editing,
            options=[ft.dropdown.Option(s) for s in specialties],
        )
        subspecialty_dropdown = ft.Dropdown(label="Subspecialty", width=360, visible=is_editing, options=[])

        specialty_chips = ft.Row(wrap=True, spacing=5)
        language_chips = ft.Row(wrap=True, spacing=5)

        def update_subspecialties(e):
            subs = algo.specialty_to_subspecialties.get(specialty_dropdown.value, [])
            subspecialty_dropdown.options = [ft.dropdown.Option(s) for s in subs]
            page.update()

        def make_remove_specialty_callback(spec, sub):
            def remove(e):
                if (spec, sub) in selected_specialties:
                    selected_specialties.remove((spec, sub))
                    specialty_chips.controls[:] = [chip for chip in specialty_chips.controls if chip.label.value != f"{spec} > {sub}"]
                    page.update()
            return remove

        def add_specialty(e):
            spec = specialty_dropdown.value
            sub = subspecialty_dropdown.value
            if spec and sub and (spec, sub) not in selected_specialties:
                selected_specialties.append((spec, sub))
                chip = ft.Chip(label=ft.Text(f"{spec} > {sub}"), on_delete=make_remove_specialty_callback(spec, sub))
                specialty_chips.controls.append(chip)
                page.update()

        def remove_language(lang):
            selected_languages.remove(lang)
            language_chips.controls[:] = [chip for chip in language_chips.controls if chip.label.value != lang]
            page.update()

        def add_language(e):
            lang = language_input.value.strip()
            if lang and lang not in selected_languages:
                selected_languages.append(lang)
                chip = ft.Chip(label=ft.Text(lang), on_delete=lambda e, l=lang: remove_language(l))
                language_chips.controls.append(chip)
                language_input.value = ""
                page.update()

        specialty_dropdown.on_change = update_subspecialties

        # Create specialty chips
        for spec, sub in selected_specialties:
            specialty_chips.controls.append(
                ft.Chip(
                    label=ft.Text(f"{spec} > {sub}", weight="bold", size=14), 
                    on_delete=make_remove_specialty_callback(spec, sub) if is_editing else None
                )
            )


        # Create language chips
        for lang in selected_languages:
            language_chips.controls.append(
                ft.Chip(
                    label=ft.Text(lang, weight="bold", size=14),
                    on_delete=lambda e, l=lang: remove_language(l) if is_editing else None
                )
            )

        controls = [
            username_field,
            password_field,
            specialty_dropdown,
            subspecialty_dropdown,
            ft.ElevatedButton("Add Specialty", on_click=add_specialty, visible=is_editing),
            specialty_chips,
            language_input,
            ft.ElevatedButton("Add Language", on_click=add_language, visible=is_editing),
            language_chips
        ]

                
        if initial_data.get("is_new", False):
            # Show only for account creation
            controls.append(
                ft.ElevatedButton(
                    text="Save and Continue",
                    on_click=lambda e: on_submit({
                        "username": username_field.value,
                        "password": password_field.value,
                        "specialties": selected_specialties.copy(),
                        "languages": selected_languages.copy()
                    })
                )
            )
        else:
            # Show only for profile view
            if is_editing:
                controls.append(
                    ft.ElevatedButton(
                        text="Update Profile",
                        on_click=lambda e: on_submit({
                            "username": username_field.value,
                            "password": password_field.value,
                            "specialties": selected_specialties.copy(),
                            "languages": selected_languages.copy()
                        })
                    )
                )
            else:
                controls.append(
                    ft.ElevatedButton(
                        text="Edit Profile",
                        icon=ft.Icons.EDIT,
                        on_click=on_submit
                    )
                )

        return controls

    def send_help_request(message):
        condensed = message_condenser(message)
        unpacked = unpack_message(condensed)
        matched = doctor_matching(unpacked)

        case = {
            "id": str(uuid.uuid4()),
            "message": message,
            "status": "pending",
            "sender": "gazan",
            "receivers": [doc["first_name"] for doc in matched],
            "accepted_by": None
        }
        cases.append(case)


    def get_pending_cases():
        return [c for c in cases if c["sender"] == "gazan" and c["status"] == "pending"]

    def get_new_cases(doctor_name):
        return [c for c in cases if doctor_name in c["receivers"] and c["status"] == "pending"]
    

    def get_current_cases(username):
        return [c for c in cases if c["status"] == "current" and c["assigned_doctor"] == username]

    def decline_case(case_id, doctor_username):
        for c in cases:
            if c["id"] == case_id and doctor_username in c["receivers"]:
                c["receivers"].remove(doctor_username)
                print(f"[Decline] {doctor_username} declined case {case_id}")
                break


    def accept_case(case_id, username):
        print("[Action] Accepting case...")

        # Update the global case status and assign the doctor
        for c in cases:
            if c["id"] == case_id:
                c["status"] = "current"
                c["assigned_doctor"] = username
                print(f"[Update] Case {case_id} now assigned to {username} with status 'current'")
                break


    def handle_case_popup(case):
        def on_accept(e):
            accept_case(case["id"], user_profile["username"])
            page.views.pop()
            page.views.clear()  # clear old views
            page.views.append(international_main_view())  # rebuild main page
            page.go("/international_main")  # navigate there

        def on_decline(e):
            decline_case(case["id"], user_profile["username"])
            page.views.pop()  # Go back one view
            page.views.clear()  # clear old views
            page.views.append(international_main_view())  # rebuild main page
            page.go("/international_main")  # Rebuilds the view

        page.views.append(
            ft.View(
                "/new_case_popup",
                controls=[
                    ft.AppBar(title=ft.Text("New Case")),
                    ft.Text(case["message"]),
                    ft.Row([
                        ft.ElevatedButton("Accept", on_click=on_accept),
                        ft.OutlinedButton("Decline", on_click=on_decline),
                    ])
                ]
            )
        )
        page.update()

    def get_current_cases_gazan():
        return [c for c in cases if c["sender"] == "gazan" and c["status"] == "current"]



    # ========== PAGE COMPONENTS ==========

    def landing_view():
        return ft.View(
            "/",
            controls=[
                ft.Text("Welcome to Healix!", size=30, weight="bold"),
                ft.Text("Select your role:", size=24, weight="bold"),
                ft.ElevatedButton("International Doctor", on_click=lambda e: set_user_type_and_go("international", "/login")),
                ft.ElevatedButton("Gazan Doctor", on_click=lambda e: set_user_type_and_go("gazan", "/gazan_main")),
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def login_view():
        return ft.View(
            "/login",
            controls=[
                ft.Text("Login", size=20),
                ft.TextField(label="Username"),
                ft.TextField(label="Password", password=True),
                ft.Row([
                    ft.ElevatedButton("Login", on_click=lambda e: page.go("/international_main")),
                    ft.TextButton("New Doctor? Create Profile", on_click=lambda e: page.go("/profile_setup")),
                ]),
            ],
        )
    
    def profile_setup_view():
        def save_profile(data):
            user_profile.update(data)
            page.go("/international_main")

        return ft.View(
            "/profile_setup",
            controls=[
                ft.AppBar(title=ft.Text("New Doctor Profile")),
                ft.Column(
                    build_profile_editor(
                        is_editing=True,
                        on_submit=save_profile,
                        initial_data={**user_profile, "is_new": True}  # This flag disables Update/Edit buttons
                    ),
                    scroll=ft.ScrollMode.AUTO
                )
            ]
        )

    def profile_view():
        editor_container = ft.Ref[ft.Container]()

        def refresh_editor():
            editor_container.current.content = ft.Column(
                build_profile_editor(
                    is_editing=profile_edit_mode,
                    on_submit=handle_submit,
                    initial_data=user_profile
                ),
                scroll=ft.ScrollMode.AUTO
            )

        def handle_submit(data_or_event):
            global profile_edit_mode, user_profile

            if profile_edit_mode:
                # Update profile
                user_profile.update(data_or_event)
                profile_edit_mode = False
            else:
                # Enter edit mode
                profile_edit_mode = True

            refresh_editor()
            page.update()

        view = ft.View(
            "/profile",
            controls=[
                ft.AppBar(
                    title=ft.Text("My Profile"),
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda e: page.go("/international_main")
                    ),
                    actions=[]  # no AppBar buttons
                ),
                ft.Container(ref=editor_container)
            ]
        )

        refresh_editor()
        return view



    def international_main_view():
        def update_availability(value):
            user_profile["available"] = value
            page.update()

        availability_row = ft.Row(
            controls=[
                ft.Text("Available:", size=16),
                ft.Switch(
                    scale=0.75,
                    value=user_profile.get("available", True),
                    on_change=lambda e: update_availability(e.control.value)
                )
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        return ft.View(
            "/international_main",
            controls=[
                ft.AppBar(
                    title=ft.Text("International Doctor"),
                    actions=[
                        availability_row,
                        ft.IconButton(
                            ft.Icons.ACCOUNT_CIRCLE,
                            tooltip="Profile",
                            on_click=lambda e: page.go("/profile")
                        ),
                        ft.IconButton(
                            ft.Icons.LOGOUT,
                            tooltip="Log out",
                            on_click=lambda e: page.go("/")
                        )
                    ]
                ),
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(
                            text="Current Cases",
                            content=ft.Column([
                                ft.ListTile(title=ft.Text(c["message"]), on_click=lambda e: page.go("/chat"))
                                for c in get_current_cases(user_profile["username"])
                            ])
                        ),
                        ft.Tab(
                            text="New Cases",
                            content=ft.Column([
                                ft.ListTile(title=ft.Text(c["message"]), on_click=lambda e, c=c: handle_case_popup(c))
                                for c in get_new_cases(user_profile["username"])
                            ])
                        ),
                    ]
                )
            ]
        )

   

    def gazan_main_view():
        return ft.View(
            "/gazan_main",
            controls=[
                ft.AppBar(
                    title=ft.Text("Gazan Doctor"),
                    actions=[
                        ft.Text("ID: 12345"),
                        ft.IconButton(ft.Icons.LOGOUT, tooltip="Log out", on_click=lambda e: page.go("/"))
                    ]
                ),
                ft.Container(
                    alignment=ft.alignment.bottom_center,
                    padding=20,
                    content=ft.ElevatedButton(
                        text="Help Request",
                        bgcolor="red",
                        color="white",
                        width=page.width,  # makes it span full width
                        height=50,
                        on_click=lambda e: page.go("/help_request"),  # your existing function
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    )
                ),

                #ft.ElevatedButton("Help Request", on_click=lambda e: page.go("/help_request")),
                ft.ElevatedButton("Connect Device", on_click=lambda e: page.go("/connect_device")),
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Current Cases", content=ft.Column([
                            ft.ListTile(title=ft.Text(c["message"]), on_click=lambda e, c=c: page.go("/chat"))
                            for c in get_current_cases_gazan()
                        ])),
                        ft.Tab(
                            text="Pending Cases",
                            content=ft.Column([
                                ft.ListTile(title=ft.Text(c["message"]), on_click=lambda e, cid=c["id"]: page.go("/chat"))
                                for c in get_pending_cases()
                            ])
                        ),
                    ]
                )
            ]
        )
    

    def chat_view():
        back_route = "/international_main" if current_user_type == "international" else "/gazan_main"
        return ft.View(
            "/chat",
            controls=[
                ft.AppBar(
                    title=ft.Text("Chat"),
                    leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go(back_route))
                ),
                ft.Column([
                    ft.Text("Conversation will go here"),
                    ft.TextField(label="Type a message", multiline=False),
                    ft.ElevatedButton("Send"),
                ])
            ]
        )

    def new_case_popup_view():
        last_case = new_cases[-1] if new_cases else {"details": "No case data available."}

        return ft.View(
            "/new_case_popup",
            controls=[
                ft.AppBar(title=ft.Text("New Case"), leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/international_main"))),
                ft.Text(last_case["details"]),
                ft.Row([
                    ft.ElevatedButton("Accept", on_click=lambda e: page.go("/chat")),
                    ft.OutlinedButton("Decline", on_click=lambda e: page.go("/international_main")),
                ])
            ]
        )

    
    def help_request_view():
        help_input = ft.TextField(label="Your message", multiline=True)

        def send_message(e):
            message = help_input.value.strip()
            if message:
                send_help_request(message)
                page.go("/gazan_main")

        return ft.View(
            "/help_request",
            controls=[
                ft.AppBar(title=ft.Text("Help Request")),
                ft.Text("Type or record your help request"),
                help_input,
                ft.ElevatedButton("Send", on_click=send_message),
            ]
        )
    
    def connect_device_view():
        devices = ["LoRa-Device-1", "LoRa-Device-2", "LoRa-Device-3"]
        device_list = ft.Column()
        lora_enabled = ft.Switch(value=True)

        info_panel = ft.Container(
            bgcolor="blue50",
            border_radius=10,
            padding=20,
            content=ft.Column([
                # Centered content block
                ft.Column([
                    ft.Image(
                        src="loraIcon.png",  # <- use the file ID Flet recognizes
                        width=80,
                        height=80,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text("Set Up Your Off-the-Grid Communication", size=20, weight="bold", text_align="center"),
                    ft.Text(
                        "Connect to devices using long-range, low-power LoRa technology for reliable communication in remote areas.",
                        text_align="center",
                        size=14
                    )
                ], alignment="center", horizontal_alignment="center"),
                
                ft.Divider(height=20, color="transparent"),

                # Toggle row (not centered)
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Text("Connect via Bluetooth", size=16),
                        ft.Switch(value=True)
                    ]
                )
            ])
        )


        '''
        info_panel = ft.Container(
            bgcolor="blue50",
            padding=15,
            border_radius=10,
            content=ft.Row(
                controls=[
                    ft.Image(
                        src="loraIcon.png",  # Use your LoRa icon path here
                        width=40,
                        height=40,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Enable LoRa to search for nearby medical relay devices.",
                            size=14
                        ),
                        expand=True
                    ),
                    lora_enabled
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        '''

        # Device list logic
        for device_name in devices:
            status_text = ft.Text("Not Connected", color="red")
            
            loading = ft.ProgressRing(visible=False, width=16, height=16)

            def on_click(e, name=device_name, status=status_text, loader=loading):
                loader.visible = True
                status.value = "Connecting..."
                status.color = "grey"
                page.update()

                import time
                time.sleep(1)

                loader.visible = False
                status.value = "Connected"
                status.color = "blue800"
                page.update()

            tile = ft.Container(
                content=ft.ListTile(
                    title=ft.Text(device_name),
                    subtitle=status_text,
                    trailing=loading,
                    on_click=on_click
                ),
                bgcolor="white",
                border=ft.border.all(1, "grey300"),
                border_radius=5,
                padding=10
            )
            device_list.controls.append(tile)

        return ft.View(
            "/connect_device",
            controls=[
                ft.AppBar(
                    title=ft.Text("Connect to Device"),
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: page.go("/gazan_main")  # or whatever page you want to go back to
                    )
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        info_panel,
                        ft.Text("Available Devices", size=16, weight="bold"),
                        device_list
                    ])
                )
            ]
        )


ft.app(target=main, view=ft.FLET_APP)

