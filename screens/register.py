from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ui.colors import PRIMARY, DANGER, SUCCESS
from ui.components import PrimaryButton, SecondaryButton


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Главный контейнер
        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(32), dp(20), dp(32), dp(20)],
            spacing=dp(16)
        )

        # Пружина сверху (выравнивает контент по вертикали)
        layout.add_widget(Widget(size_hint_y=1))

        # ==========================================
        # ЗАГОЛОВОК
        # ==========================================
        title = Label(
            text="Создать аккаунт",
            color=PRIMARY,
            font_size=dp(28),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign="center",
            valign="middle"
        )
        title.bind(size=title.setter("text_size"))
        layout.add_widget(title)
        
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
            padding=[dp(16), dp(14)]
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

        self.confirm_password = TextInput(
            hint_text="Подтвердите пароль",
            password=True,
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), dp(14)]
        )

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.confirm_password)

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
        register_button = PrimaryButton(
            text="Зарегистрироваться",
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(48)
        )
        register_button.bind(on_press=self.register)

        back_button = SecondaryButton(
            text="Назад ко входу",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(48)
        )
        back_button.bind(on_press=self.back_to_login)

        layout.add_widget(register_button)
        layout.add_widget(back_button)

        # Пружина снизу
        layout.add_widget(Widget(size_hint_y=1))

        self.add_widget(layout)

    # ==================================================
    # ЛОГИКА РЕГИСТРАЦИИ
    # ==================================================
    def register(self, instance):
        username = self.username.text.strip()
        password = self.password.text
        confirm_password = self.confirm_password.text

        # Валидация
        if not username or not password:
            self.show_error("Заполните все поля")
            return

        if password != confirm_password:
            self.show_error("Пароли не совпадают")
            return

        if len(password) < 6:
            self.show_error("Пароль должен быть не менее 6 символов")
            return

        app = self.manager.app

        try:
            response = app.api.register(username, password)

            if response.status_code == 200:
                self.clear_fields()
                
                # Показываем сообщение об успехе на экране логина
                login_screen = self.manager.get_screen("login")
                login_screen.status.color = SUCCESS
                login_screen.status.text = "Аккаунт успешно создан. Войдите!"
                
                self.manager.current = "login"
            else:
                try:
                    error_msg = response.json().get("detail", "Ошибка регистрации")
                    self.show_error(error_msg)
                except Exception:
                    self.show_error("Ошибка регистрации")

        except Exception as e:
            print(f"Registration error: {e}")
            self.show_error("Не удалось подключиться к серверу")

    def show_error(self, message):
        """Вспомогательный метод для вывода ошибок"""
        self.status.color = DANGER
        self.status.text = message

    # ==================================================
    # НАВИГАЦИЯ И ОЧИСТКА
    # ==================================================
    def back_to_login(self, instance):
        self.clear_fields()
        login_screen = self.manager.get_screen("login")
        login_screen.clear_fields()  # Очищаем экран логина перед возвратом
        self.manager.current = "login"

    def clear_fields(self):
        self.username.text = ""
        self.password.text = ""
        self.confirm_password.text = ""
        self.status.text = ""