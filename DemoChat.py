
import multiprocessing
import flet as ft
from datetime import datetime
from functools import partial
import time

header_message = "A 28-year-old male with multiple penetrating injuries ... "
help_message = "28-year-old male multiple penetrating injuries shrapnel after roadside ied blast. " \
"Is conscious disoriented. active arterial bleeding left thigh deep lacerations abdomen right forearm. " \
"likely femoral artery involvement. airway patent respirations shallow possible pneumothorax. " \
"breath sounds decreased right side. no obvious head trauma. tourniquet applied upper thigh. " \
"iv access established. bp 80/40, hr 132, rr 28, spo 89 percent room air. eta field hospital 10 min."

def chat_view(page: ft.Page, user, shared_messages):
    stop_flag = False

    # Header (fixed)
    back_button = ft.IconButton(ft.Icons.ARROW_BACK)
    header_message = "A 28-year-old male with multiple penetrating injuries ... "
    help_message = "28-year-old male multiple penetrating injuries shrapnel after roadside ied blast. " \
                   "Is conscious disoriented. active arterial bleeding left thigh deep lacerations abdomen right forearm. " \
                   "likely femoral artery involvement. airway patent respirations shallow possible pneumothorax. " \
                   "breath sounds decreased right side. no obvious head trauma. tourniquet applied upper thigh. " \
                   "iv access established. bp 80/40, hr 132, rr 28, spo 89 percent room air. eta field hospital 10 min."

    channel_info = ft.Text(
        header_message,
        size=16,
        weight="bold",
        max_lines=3,
        overflow=ft.TextOverflow.CLIP,
        expand=True
    )

    header = ft.Container(
        content=ft.Row(
            controls=[
                back_button,
                channel_info
            ],
            alignment=ft.MainAxisAlignment.START
        ),
        padding=10,
        bgcolor="white"
    )

    # Message list
    message_listview = ft.ListView(
        controls=[
            ft.Text(
                help_message,
                size=12,
                color="grey",
                italic=True,
                text_align=ft.TextAlign.CENTER
            )
        ],
        auto_scroll=True,
        expand=True,
        spacing=5,
        padding=10
    )

    message_scrollable = ft.Container(
        content=message_listview,
        expand=True,
        bgcolor="blue50"
    )

    text_input = ft.TextField(hint_text="Type a message...", expand=True)
    mic_icon = ft.IconButton(ft.Icons.MIC)
    send_button = ft.IconButton(icon=ft.Icons.SEND)
    input_bar = ft.Container(
        content=ft.Row([text_input, mic_icon, send_button]),
        padding=10,
        bgcolor="white"
    )

    layout = ft.Column(
        controls=[
            header,
            message_scrollable,
            input_bar
        ],
        expand=True
    )

    def send_message(e):
        if text_input.value.strip():
            shared_messages.append((user, text_input.value.strip(), datetime.now().strftime("%H:%M:%S")))
            text_input.value = ""
            page.update()

    send_button.on_click = send_message

    def update_loop():
        prev_len = 0
        while not stop_flag:
            lv: ft.ListView = message_scrollable.content
            if len(shared_messages) > prev_len:
                for i in range(prev_len, len(shared_messages)):
                    sender, text, time_sent = shared_messages[i]

                    msg = ft.Container(
                        content=ft.Text(
                            text,
                            color="white" if sender == user else "black",
                            size=14,
                            max_lines=10,
                            overflow=ft.TextOverflow.CLIP,
                        ),
                        bgcolor="blue800" if sender == user else "white",
                        padding=10,
                        border_radius=10,
                        margin=5,
                        width=250
                    )
                    alignment = ft.MainAxisAlignment.END if sender == user else ft.MainAxisAlignment.START
                    lv.controls.append(ft.Row([msg], alignment=alignment))
                prev_len = len(shared_messages)
                page.update()
            time.sleep(0.2)

    page.run_thread(update_loop)

    def on_window_event(e):
        nonlocal stop_flag
        stop_flag = True

    page.on_window_event = on_window_event

    def go_back(e):
        page.go("/")

    back_button.on_click = go_back

    return ft.View(route="/chat", controls=[layout])

def chat_app(user, shared_messages):
    def main(page: ft.Page):
        page.title = "Chat Demo"

        def route_change(e):
            page.views.clear()
            if page.route == "/":
                page.views.append(
                    ft.View(
                        route="/",
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    [ft.Text("Main Menu", size=20, weight="bold"),
                                     ft.ElevatedButton("Chat", on_click=lambda _: page.go("/chat"))],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                expand=True,
                                alignment=ft.alignment.center
                            )
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            elif page.route == "/chat":
                page.views.append(chat_view(page, user, shared_messages))
            page.update()

        page.on_route_change = route_change
        page.go(page.route)

    ft.app(target=main)

def launch_chat_windows():
    manager = multiprocessing.Manager()
    shared_messages = manager.list()

    p1 = multiprocessing.Process(target=partial(chat_app, "User 1", shared_messages), daemon=True)
    p2 = multiprocessing.Process(target=partial(chat_app, "User 2", shared_messages), daemon=True)

    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == "__main__":
    launch_chat_windows()

