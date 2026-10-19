import flet as ft


class AppLabel(ft.Text):
    def __init__(self, value=""):
        super().__init__(value=value)


class AppButton(ft.Button):
    def __init__(self, text, on_click=None):
        super().__init__(text, on_click=on_click)
