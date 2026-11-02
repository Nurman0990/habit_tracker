from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ui.colors import PRIMARY, DANGER, TEXT
from ui.components import PrimaryButton, SecondaryButton


class HabitFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.editing_habit_id = None

        # Главный контейнер
        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(32), dp(20), dp(20)],
            spacing=dp(16)
        )

        # ==========================================
        # ЗАГОЛОВОК
        # ==========================================
        self.title = Label(
            text="Добавить привычку",
            color=PRIMARY,
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(50),
            halign="center",
            valign="middle"
        )
        self.title.bind(size=self.title.setter("text_size"))
        layout.add_widget(self.title)
        
        layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # ==========================================
        # ПОЛЯ ВВОДА
        # ==========================================
        self.name_input = TextInput(
            hint_text="Название привычки",
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), dp(14)]
        )

        self.description_input = TextInput(
            hint_text="Описание (необязательно)",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            padding=[dp(16), dp(14)]
        )

        layout.add_widget(self.name_input)
        layout.add_widget(self.description_input)

        # ==========================================
        # СТАТУС / ОШИБКИ
        # ==========================================
        self.status = Label(
            text="",
            color=DANGER,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20),
            halign="center"
        )
        layout.add_widget(self.status)

        # ==========================================
        # КНОПКИ
        # ==========================================
        buttons_layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )

        cancel_button = SecondaryButton(text="Отмена")
        cancel_button.bind(on_press=self.cancel)

        save_button = PrimaryButton(text="Сохранить", bold=True)
        save_button.bind(on_press=self.save_habit)

        # Порядок кнопок: Отмена слева, Сохранить справа (стандартный UX)
        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(save_button)

        layout.add_widget(buttons_layout)

        # Пружина снизу (прижимает форму наверх экрана)
        layout.add_widget(Widget(size_hint_y=1))

        self.add_widget(layout)

    # ==================================================
    # ПОДГОТОВКА ФОРМЫ
    # ==================================================
    def open_for_create(self):
        self.editing_habit_id = None
        self.title.text = "Новая привычка"
        self.name_input.text = ""
        self.description_input.text = ""
        self.status.text = ""

    def open_for_edit(self, habit):
        self.editing_habit_id = habit["id"]
        self.title.text = "Редактирование"
        self.name_input.text = habit["name"]
        self.description_input.text = habit.get("description", "") or ""
        self.status.text = ""

    # ==================================================
    # ЛОГИКА СОХРАНЕНИЯ
    # ==================================================
    def save_habit(self, instance):
        name = self.name_input.text.strip()
        description = self.description_input.text.strip()

        if not name:
            self.show_error("Укажите название привычки")
            return

        app = self.manager.app

        try:
            # Создание или обновление в зависимости от наличия ID
            if self.editing_habit_id is None:
                response = app.api.create_habit(name, description)
            else:
                response = app.api.update_habit(self.editing_habit_id, name, description)

            if response.status_code in (200, 201):
                # Успешное сохранение -> переход на главный экран и обновление списка
                self.manager.current = "habits"
                self.manager.get_screen("habits").load_habits()
            else:
                try:
                    error_msg = response.json().get("detail", "Не удалось сохранить привычку")
                    self.show_error(error_msg)
                except Exception:
                    self.show_error("Не удалось сохранить привычку")

        except Exception as e:
            print(f"Save habit error: {e}")
            self.show_error("Не удалось подключиться к серверу")

    def show_error(self, message):
        """Вспомогательный метод для отображения ошибок"""
        self.status.text = message

    # ==================================================
    # ОТМЕНА И НАВИГАЦИЯ
    # ==================================================
    def cancel(self, instance):
        self.manager.current = "habits"