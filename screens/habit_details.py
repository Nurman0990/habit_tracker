import calendar
from datetime import date

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from ui.colors import (
    TEXT, TEXT_SECONDARY, TEXT_MUTED,
    PRIMARY, SUCCESS, DANGER
)
from ui.styles import rounded_background
from ui.components import SecondaryButton

# Локализация для календаря
RU_MONTHS = [
    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]
RU_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class HabitDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.habit = None
        self.year = date.today().year
        self.month = date.today().month

        self.layout = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(20), dp(16), dp(16)],
            spacing=dp(20)
        )

        # ==========================================
        # ШАПКА (Кнопка Назад + Название)
        # ==========================================
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
        
        back_button = SecondaryButton(
            text="< Назад", font_size=dp(13), size_hint_x=None, width=dp(75)
        )
        back_button.bind(on_press=self.go_back)

        self.title = Label(
            text="Привычка", color=TEXT, font_size=dp(20), bold=True,
            halign="center", valign="middle", size_hint_x=1
        )
        
        # Правый спейсер для идеального центрирования заголовка
        right_spacer = Widget(size_hint_x=None, width=dp(75))

        header.add_widget(back_button)
        header.add_widget(self.title)
        header.add_widget(right_spacer)
        
        self.layout.add_widget(header)

        # ==========================================
        # СТАТИСТИКА (Сетка 2x2)
        # ==========================================
        self.stats_layout = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(120))
        self.layout.add_widget(self.stats_layout)

        # ==========================================
        # КАЛЕНДАРЬ
        # ==========================================
        calendar_container = BoxLayout(orientation="vertical", spacing=dp(12))

        # Управление месяцами
        cal_header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        
        prev_btn = SecondaryButton(text="<", size_hint_x=None, width=dp(44))
        prev_btn.bind(on_press=self.previous_month)
        
        self.month_label = Label(
            text="", color=TEXT, font_size=dp(16), bold=True, size_hint_x=1
        )
        
        next_btn = SecondaryButton(text=">", size_hint_x=None, width=dp(44))
        next_btn.bind(on_press=self.next_month)

        cal_header.add_widget(prev_btn)
        cal_header.add_widget(self.month_label)
        cal_header.add_widget(next_btn)
        
        calendar_container.add_widget(cal_header)

        # Сетка календаря
        self.calendar_layout = GridLayout(cols=7, spacing=dp(4), size_hint_y=None)
        self.calendar_layout.bind(minimum_height=self.calendar_layout.setter("height"))
        calendar_container.add_widget(self.calendar_layout)

        # Добавляем пружину вниз, чтобы контент не растягивался на весь экран
        calendar_container.add_widget(Widget())
        
        self.layout.add_widget(calendar_container)
        self.add_widget(self.layout)

    # ==================================================
    # ЛОГИКА ЗАГРУЗКИ
    # ==================================================
    def load_habit(self, habit):
        self.habit = habit
        self.title.text = habit["name"]
        
        today = date.today()
        self.year = today.year
        self.month = today.month

        self.load_stats()
        self.load_calendar()

    def load_stats(self):
        self.stats_layout.clear_widgets()
        app = self.manager.app

        try:
            response = app.api.get_stats(self.habit["id"])
            if response.status_code == 200:
                stats = response.json()
                
                # Создаем карточки статистики
                self._add_stat_card("Текущая серия", f"{stats['current_streak']} дн.", PRIMARY)
                self._add_stat_card("Лучшая серия", f"{stats['best_streak']} дн.", SUCCESS)
                self._add_stat_card("Всего выполнено", str(stats['total_completions']), TEXT)
                self._add_stat_card("Процент успеха", f"{stats['completion_rate']}%", TEXT)
                return
                
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

        # Fallback при ошибке или пустых данных
        error_label = Label(
            text="Статистика недоступна", color=TEXT_MUTED, font_size=dp(14),
            size_hint_x=2 # Растягиваем на 2 колонки
        )
        self.stats_layout.add_widget(error_label)

    def _add_stat_card(self, title, value, value_color):
        """Вспомогательный метод для рендера красивой ячейки статистики"""
        box = BoxLayout(orientation="vertical", spacing=dp(2))
        
        val_lbl = Label(
            text=value, color=value_color, font_size=dp(22), bold=True,
            size_hint_y=None, height=dp(28)
        )
        title_lbl = Label(
            text=title, color=TEXT_SECONDARY, font_size=dp(11),
            size_hint_y=None, height=dp(18)
        )
        
        box.add_widget(val_lbl)
        box.add_widget(title_lbl)
        self.stats_layout.add_widget(box)

    def load_calendar(self):
        app = self.manager.app
        try:
            response = app.api.get_calendar(self.habit["id"], self.year, self.month)
            if response.status_code == 200:
                data = response.json()
                completed_dates = {
                    item["date"] for item in data["days"] if item.get("completed")
                }
                self.render_calendar(completed_dates)
                return
        except Exception as e:
            print(f"Ошибка загрузки календаря: {e}")

        self.calendar_layout.clear_widgets()
        self.calendar_layout.add_widget(Label(text="Календарь недоступен", color=TEXT_MUTED))

    # ==================================================
    # РЕНДЕР КАЛЕНДАРЯ
    # ==================================================
    def render_calendar(self, completed_dates):
        self.calendar_layout.clear_widgets()
        self.month_label.text = f"{RU_MONTHS[self.month]} {self.year}"

        # Рендер дней недели
        for weekday in RU_WEEKDAYS:
            self.calendar_layout.add_widget(
                Label(
                    text=weekday, color=TEXT_SECONDARY, font_size=dp(12), bold=True,
                    size_hint_y=None, height=dp(30)
                )
            )

        # Рендер сетки дней
        month_calendar = calendar.monthcalendar(self.year, self.month)
        
        for week in month_calendar:
            for day in week:
                if day == 0:
                    self.calendar_layout.add_widget(Widget(size_hint_y=None, height=dp(40)))
                    continue

                current_date = date(self.year, self.month, day).isoformat()
                is_completed = current_date in completed_dates

                # Если день выполнен, используем цвет SUCCESS, иначе обычный TEXT
                color = SUCCESS if is_completed else TEXT
                bold = is_completed

                day_label = Label(
                    text=str(day), color=color, font_size=dp(16), bold=bold,
                    size_hint_y=None, height=dp(40)
                )
                
                # Дополнительно: если используете стили фонов, можно раскомментировать строку ниже:
                # if is_completed: rounded_background(day_label, SUCCESS, radius=8)
                
                self.calendar_layout.add_widget(day_label)

    # ==================================================
    # НАВИГАЦИЯ
    # ==================================================
    def previous_month(self, instance):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.load_calendar()

    def next_month(self, instance):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.load_calendar()

    def go_back(self, instance):
        self.manager.current = "habits"