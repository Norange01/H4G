import flet as ft
import Algorithm as algo



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





    # ========== PAGE COMPONENTS ==========

    def landing_view():
        return ft.View(
            "/",
            controls=[
                ft.Text("Welcome! Select your role:", size=24, weight="bold"),
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
                                ft.ListTile(title=ft.Text("Case A"), on_click=lambda e: page.go("/chat"))
                            ])
                        ),
                        ft.Tab(
                            text="New Cases",
                            content=ft.Column([
                                ft.ListTile(title=ft.Text("Case B - New"), on_click=lambda e: page.go("/new_case_popup"))
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
                ft.ElevatedButton("Help Request", on_click=lambda e: page.go("/help_request")),
                ft.ElevatedButton("Connect Device", on_click=lambda e: page.go("/connect_device")),
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Current Cases", content=ft.Column([
                            ft.ListTile(title=ft.Text("Doctor Smith"), on_click=lambda e: page.go("/chat"))
                        ])),
                        ft.Tab(text="Pending Cases", content=ft.Column([
                            ft.ListTile(title=ft.Text("New Pending Case"), on_click=lambda e: page.go("/chat"))
                        ])),
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
        return ft.View(
            "/new_case_popup",
            controls=[
                ft.AppBar(title=ft.Text("New Case"), leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/international_main"))),
                ft.Text("Details about this case"),
                ft.Row([
                    ft.ElevatedButton("Accept", on_click=lambda e: page.go("/chat")),
                    ft.OutlinedButton("Decline", on_click=lambda e: page.go("/international_main")),
                ])
            ]
        )

    def help_request_view():
        return ft.View(
            "/help_request",
            controls=[
                ft.AppBar(title=ft.Text("Help Request")),
                ft.Text("Type or record your help request"),
                ft.TextField(label="Your message"),
                ft.ElevatedButton("Send", on_click=lambda e: page.go("/gazan_main")),
            ]
        )

    def connect_device_view():
        return ft.View(
            "/connect_device",
            controls=[
                ft.AppBar(title=ft.Text("Connect Device"), leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/gazan_main"))),
                ft.Text("LoRa Connection Interface (To be implemented)"),
                ft.ElevatedButton("Scan Devices"),
                ft.Text("Connected: No"),
            ]
        )

ft.app(target=main, view=ft.FLET_APP)

