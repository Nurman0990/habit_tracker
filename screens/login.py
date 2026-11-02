from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ui.colors import TEXT, PRIMARY, DANGER, TEXT_SECONDARY
from ui.components import PrimaryButton, SecondaryButton


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Основной контейнер с отступами по бокам
        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(32), dp(20), dp(32), dp(20)],
            spacing=dp(16)
        )

        # Пружина сверху (занимает доступное место, центрируя контент)
        layout.add_widget(Widget(size_hint_y=1))

        # ==========================================
        # ЗАГОЛОВОК
        # ==========================================
        title = Label(
            text="Habit Tracker",
            color=PRIMARY,
            font_size=dp(32),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign="center",
            valign="middle"
        )
        title.bind(size=title.setter("text_size"))
        layout.add_widget(title)
        
        # Небольшой отступ между заголовком и формой
        layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # ==========================================
        # ПОЛЯ ВВОДА
        # ==========================================
        self.username = TextInput(
            hint_text="Имя пользователя",
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), dp(14)] # Центрирование текста внутри поля
        )

        self.password = TextInput(
            hint_text="Пароль",
            password=True,
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), dp(14)]
        )

        layout.add_widget(self.username)
        layout.add_widget(self.password)

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
        login_button = PrimaryButton(
            text="Войти",
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(48)
        )
        login_button.bind(on_press=self.login)

        register_button = SecondaryButton(
            text="Создать аккаунт",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(48)
        )
        register_button.bind(on_press=self.open_register)

        layout.add_widget(login_button)
        layout.add_widget(register_button)

        # Пружина снизу (занимает доступное место)
        layout.add_widget(Widget(size_hint_y=1))

        self.add_widget(layout)

    # ==================================================
    # ЛОГИКА АВТОРИЗАЦИИ
    # ==================================================
    def login(self, instance):
        username = self.username.text.strip()
        password = self.password.text

        if not username or not password:
            self.status.text = "Введите имя пользователя и пароль"
            return

        app = self.manager.app

        try:
            success, result = app.api.login(username, password)

            if success:
                self.status.text = ""
                
                # Переход и загрузка данных
                self.manager.current = "habits"
                self.manager.get_screen("habits").load_habits()
            else:
                # API должно возвращать текст ошибки в result
                self.status.text = str(result)

        except Exception as e:
            print(f"Login error: {e}")
            self.status.text = "Не удалось подключиться к серверу"

    # ==================================================
    # НАВИГАЦИЯ И ОЧИСТКА
    # ==================================================
    def open_register(self, instance):
        self.manager.get_screen("register").clear_fields()
        self.manager.current = "register"

    def clear_fields(self):
        self.username.text = ""
        self.password.text = ""
        self.status.text = ""