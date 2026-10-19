import base64
import getpass
import os
import io
from datetime import datetime
from PIL import Image as PILImage

import flet as ft

from entities import ImageInfo, RecentFile, KeyValueStore
from image_reader import ImageReader


class BmpReaderApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.reader = ImageReader()
        self.settings = KeyValueStore()
        self.recent_files = []
        self.login = getpass.getuser()
        self.time_in = datetime.now()
        self.current_path = ""
        self.selected_bytes = KeyValueStore()

        self.path_field = ft.TextField(label="Путь к изображению", expand=True, on_submit=self.open_from_path)
        self.format_box = ft.Dropdown(label="Формат", width=150, value="BMP", on_select=self.change_format, options=[
            ft.dropdown.Option("BMP"), ft.dropdown.Option("Все изображения")
        ])
        self.file_picker = ft.FilePicker(on_result=self.file_picked)
        self.open_button = ft.Button("Открыть файл", icon=ft.Icons.FOLDER_OPEN)
        self.preview = ft.Container(
            content=ft.Text("Выберите изображение", size=18), expand=True,
            alignment=ft.Alignment.CENTER, border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=8, padding=10
        )
        self.info = ft.Text("Изображение не выбрано")
        self.recent_list = ft.ListView(spacing=4, expand=True, width=220)
        self.status = ft.Text("Готово")
        self.build_interface()
        self.page.on_close = self.on_close

    def build_interface(self):
        self.page.title = "BMP Reader"
        self.page.window.width = 1000
        self.page.window.height = 700
        self.page.padding = 16
        self.open_button.action = ft.PickFiles(
            self.file_picker, allow_multiple=False, with_data=True,
            allowed_extensions=["bmp"] if self.format_box.value == "BMP" else ["bmp", "png", "jpg", "jpeg", "gif"]
        )
        self.page.add(
            ft.Column([
                ft.Row([self.path_field, self.format_box, self.open_button]),
                ft.Row([self.preview, ft.Container(content=self.recent_list, width=220)], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH),
                self.info,
                ft.Row([ft.Button("Очистить", on_click=self.clear_view)]),
                ft.Divider(), self.status
            ], expand=True, spacing=12)
        )

    def change_format(self, event):
        extensions = ["bmp"] if self.format_box.value == "BMP" else ["bmp", "png", "jpg", "jpeg", "gif"]
        self.open_button.action = ft.PickFiles(self.file_picker, allow_multiple=False, with_data=True, allowed_extensions=extensions)
        self.page.update()

    async def file_picked(self, event: ft.FilePickerResultEvent):
        if not event.files:
            return
        picked = event.files[0]
        data = getattr(picked, "bytes", None)
        path = getattr(picked, "path", None)
        name = picked.name
        if data:
            self.selected_bytes.set(name, data)
            await self.open_image_data(name, data)
        elif path:
            self.path_field.value = path
            await self.open_image(path)
        else:
            self.status.value = "Не удалось прочитать выбранный файл. Попробуйте открыть приложение как desktop-приложение."
            self.page.update()

    async def open_image_data(self, name, data):
        try:
            with PILImage.open(io.BytesIO(data)) as source:
                source.load()
                image = source.copy()
            info = ImageInfo(name, image.width, image.height)
            png_buffer = io.BytesIO()
            image.save(png_buffer, format="PNG")
            encoded = base64.b64encode(png_buffer.getvalue()).decode("ascii")
            self.current_path = name
            self.preview.content = ft.Image(src=f"data:image/png;base64,{encoded}", fit=ft.BoxFit.CONTAIN, expand=True)
            self.info.value = f"{info.name} — {info.width} × {info.height} пикселей"
            self.path_field.value = name
            self.add_recent(name)
            self.status.value = f"Открыт файл: {name}"
            self.page.title = f"BMP Reader — {name}"
        except Exception as error:
            self.status.value = f"Ошибка открытия: {error}"
        self.page.update()

    async def open_from_path(self, event):
        await self.open_image(self.path_field.value.strip())

    async def open_image(self, path):
        data = self.selected_bytes.get(path)
        if data is not None:
            await self.open_image_data(path, data)
            return
        image = self.reader.load(path)
        if image is None:
            self.status.value = f"Ошибка открытия: {self.reader.last_error}"
            self.page.update()
            return

        info = ImageInfo(path, image.width, image.height)
        self.current_path = os.path.abspath(path)
        try:
            with PILImage.open(path) as source:
                source.load()
                image_for_preview = source.copy()
            png_buffer = io.BytesIO()
            image_for_preview.save(png_buffer, format="PNG")
            encoded = base64.b64encode(png_buffer.getvalue()).decode("ascii")
        except Exception as error:
            self.status.value = f"Ошибка подготовки изображения: {error}"
            self.page.update()
            return
        self.preview.content = ft.Image(src=f"data:image/png;base64,{encoded}", fit=ft.BoxFit.CONTAIN, expand=True)
        self.info.value = f"{info.name} — {info.width} × {info.height} пикселей"
        self.add_recent(path)
        self.settings.set("last_file", path)
        self.status.value = f"Открыт файл: {info.name}"
        self.page.title = f"BMP Reader — {info.name}"
        self.page.update()

    def add_recent(self, path):
        path = os.path.abspath(path)
        self.recent_files = [item for item in self.recent_files if os.path.normcase(item.path) != os.path.normcase(path)]
        self.recent_files.insert(0, RecentFile(path))
        self.recent_files = self.recent_files[:10]
        self.recent_list.controls.clear()
        for recent in self.recent_files:
            saved_path = recent.path

            async def open_saved_file(event, path=saved_path):
                await self.open_recent(path)

            self.recent_list.controls.append(
                ft.TextButton(
                    recent.name,
                    tooltip=recent.path,
                    on_click=open_saved_file,
                )
            )

    async def open_recent(self, path):
        self.path_field.value = path
        await self.open_image(path)

    def clear_view(self, event):
        self.current_path = ""
        self.preview.content = ft.Text("Выберите изображение", size=18)
        self.info.value = "Изображение не выбрано"
        self.page.title = "BMP Reader"
        self.status.value = "Просмотр очищен"
        self.page.update()

    def on_close(self, event):
        time_out = datetime.now()
        time_format = "%d.%m.%Y %H:%M:%S"
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.txt")
        try:
            with open(report_path, "a", encoding="utf-8") as file:
                file.write("+----------------+---------------------+---------------------+\n")
                file.write("| login          | time_in             | time_out            |\n")
                file.write("+----------------+---------------------+---------------------+\n")
                file.write(f"| {self.login:<14} | {self.time_in.strftime(time_format):<19} | {time_out.strftime(time_format):<19} |\n")
                file.write("+----------------+---------------------+---------------------+\n\n")
        except OSError as error:
            print("Не удалось записать отчет:", error)


async def main(page: ft.Page):
    BmpReaderApp(page)


if __name__ == "__main__":
    ft.run(main)
