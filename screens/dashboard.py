from datetime import datetime

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

from ui.colors import (
    TEXT, TEXT_SECONDARY, TEXT_MUTED, PRIMARY, DANGER
)
from ui.components import PrimaryButton, SecondaryButton

# Словарик для красивого вывода месяцев на русском
RU_MONTHS = {
    1: "янв", 2: "фев", 3: "мар", 4: "апр", 5: "мая", 6: "июн",
    7: "июл", 8: "авг", 9: "сен", 10: "окт", 11: "ноя", 12: "дек"
}


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(20), dp(16), dp(16)],
            spacing=dp(20)
        )

        # ==========================================
        # ШАПКА (Назад + Заголовок)
        # ==========================================
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
        
        back_button = SecondaryButton(
            text="< Назад", font_size=dp(13), size_hint_x=None, width=dp(75)
        )
        back_button.bind(on_press=self.go_back)

        title = Label(
            text="Статистика", color=TEXT, font_size=dp(20), bold=True,
            halign="center", valign="middle", size_hint_x=1
        )

        right_spacer = Widget(size_hint_x=None, width=dp(75))

        header.add_widget(back_button)
        header.add_widget(title)
        header.add_widget(right_spacer)

        self.main_layout.add_widget(header)

        # ==========================================
        # СЕГОДНЯ
        # ==========================================
        today_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(80))
        
        today_title = Label(
            text="Сегодня", color=TEXT, font_size=dp(18), bold=True,
            halign="left", valign="middle", size_hint_y=None, height=dp(24)
        )
        today_title.bind(size=today_title.setter("text_size"))
        
        self.today_label = Label(
            text="Загрузка...", color=PRIMARY, font_size=dp(24), bold=True,
            halign="left", valign="middle", size_hint_y=None, height=dp(36)
        )
        self.today_label.bind(size=self.today_label.setter("text_size"))

        self.today_sub_label = Label(
            text="", color=TEXT_SECONDARY, font_size=dp(13),
            halign="left", valign="top", size_hint_y=None, height=dp(20)
        )
        self.today_sub_label.bind(size=self.today_sub_label.setter("text_size"))

        today_box.add_widget(today_title)
        today_box.add_widget(self.today_label)
        today_box.add_widget(self.today_sub_label)
        
        self.main_layout.add_widget(today_box)

        # ==========================================
        # ПОСЛЕДНИЕ 7 ДНЕЙ (Список)
        # ==========================================
        week_box = BoxLayout(orientation="vertical", spacing=dp(8))
        
        week_title = Label(
            text="Последние 7 дней", color=TEXT, font_size=dp(18), bold=True,
            halign="left", valign="middle", size_hint_y=None, height=dp(30)
        )
        week_title.bind(size=week_title.setter("text_size"))
        week_box.add_widget(week_title)

        self.scroll = ScrollView(do_scroll_x=False)
        self.week_layout = BoxLayout(
            orientation="vertical", spacing=dp(6), size_hint_y=None
        )
        self.week_layout.bind(minimum_height=self.week_layout.setter("height"))
        
        self.scroll.add_widget(self.week_layout)
        week_box.add_widget(self.scroll)

        self.main_layout.add_widget(week_box)

        # ==========================================
        # ИТОГО ЗА НЕДЕЛЮ
        # ==========================================
        self.total_label = Label(
            text="", color=TEXT_SECONDARY, font_size=dp(14),
            halign="center", valign="middle", size_hint_y=None, height=dp(30)
        )
        self.total_label.bind(size=self.total_label.setter("text_size"))
        self.main_layout.add_widget(self.total_label)

        # ==========================================
        # КНОПКА ОБНОВИТЬ
        # ==========================================
        refresh_button = PrimaryButton(
            text="Обновить данные", font_size=dp(15), bold=True,
            size_hint_y=None, height=dp(48)
        )
        refresh_button.bind(on_press=self.load_dashboard)
        self.main_layout.add_widget(refresh_button)

        self.add_widget(self.main_layout)

    # ==================================================
    # ЛОГИКА ЗАГРУЗКИ ДАННЫХ
    # ==================================================
    def load_dashboard(self, instance=None):
        self.today_label.text = "Загрузка..."
        self.today_label.color = PRIMARY
        self.today_sub_label.text = ""
        self.week_layout.clear_widgets()
        self.total_label.text = ""

        app = self.manager.app

        try:
            response = app.api.get_dashboard()

            if response.status_code != 200:
                self.show_error("Не удалось загрузить данные")
                return

            data = response.json()

            # --- СЕГОДНЯ ---
            today = data.get("today", {})
            completed = today.get("completed", 0)
            total = today.get("total", 0)
            percentage = today.get("percentage", 0)

            self.today_label.text = f"{percentage}% выполнено"
            self.today_sub_label.text = f"Завершено {completed} из {total} задач"

            # --- НЕДЕЛЯ (Построение строк) ---
            for day in data.get("week", []):
                date_string = day.get("date", "")
                
                try:
                    parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
                    display_date = f"{parsed_date.day} {RU_MONTHS[parsed_date.month]}"
                except ValueError:
                    display_date = date_string

                d_completed = day.get("completed", 0)
                d_total = day.get("total", 0)
                d_percentage = day.get("percentage", 0)

                self.add_week_row(display_date, d_completed, d_total, d_percentage)

            # --- ИТОГО ---
            total_week = data.get("total_week_completions", 0)
            self.total_label.text = f"Всего выполнено за неделю: {total_week}"

        except Exception as e:
            print(f"Dashboard error: {e}")
            self.show_error("Ошибка подключения к серверу")

    def add_week_row(self, date_text, completed, total, percentage):
        """Создает аккуратную строку для конкретного дня"""
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        
        # Дата (Слева)
        lbl_date = Label(
            text=date_text, color=TEXT, font_size=dp(14),
            halign="left", valign="middle", size_hint_x=1
        )
        lbl_date.bind(size=lbl_date.setter("text_size"))
        
        # Прогресс (Справа, прижат)
        lbl_stats = Label(
            text=f"{completed}/{total}  ({percentage}%)", 
            color=TEXT_SECONDARY, font_size=dp(13),
            halign="right", valign="middle", size_hint_x=1
        )
        lbl_stats.bind(size=lbl_stats.setter("text_size"))

        row.add_widget(lbl_date)
        row.add_widget(lbl_stats)
        self.week_layout.add_widget(row)

    def show_error(self, text):
        self.today_label.color = DANGER
        self.today_label.text = text
        self.today_sub_label.text = ""

    # ==================================================
    # НАВИГАЦИЯ
    # ==================================================
    def go_back(self, instance):
        self.manager.current = "habits"