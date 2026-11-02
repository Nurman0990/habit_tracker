from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget  # Добавлен Widget для гибких отступов

from ui.colors import (
    CARD, TEXT, TEXT_SECONDARY, TEXT_MUTED, 
    PRIMARY, SUCCESS, DANGER, BORDER
)
from ui.styles import rounded_background
from ui.components import PrimaryButton, SecondaryButton


class HabitRow(BoxLayout):
    """
    Карточка отдельной привычки. 
    Сама управляет своим внутренним интерфейсом на основе переданных данных.
    """
    def __init__(self, habit, stats, callbacks, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(6)
        self.size_hint_y = None
        self.height = dp(120)  # Компактная, но достаточная высота для карточки

        completed_today = stats and stats.get("completed_today")

        # ==========================================
        # 1. СТРОКА: Название + Статус (Справа)
        # ==========================================
        top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        
        name = Label(
            text=habit["name"], color=TEXT, font_size=dp(16), bold=True,
            halign="left", valign="middle", size_hint_x=1  # Занимает всё свободное место
        )
        name.bind(size=name.setter("text_size"))

        if completed_today:
            status_btn = Button(
                text="Готово", color=TEXT, font_size=dp(11), bold=True,
                size_hint_x=None, width=dp(70), background_normal="", background_color=(0, 0, 0, 0)
            )
            rounded_background(status_btn, SUCCESS, radius=6)
            status_btn.bind(on_press=lambda x: callbacks["uncomplete"](habit["id"]))
        else:
            status_btn = Button(
                text="Выполнить", color=TEXT, font_size=dp(11), bold=True,
                size_hint_x=None, width=dp(80), background_normal="", background_color=(0, 0, 0, 0)
            )
            rounded_background(status_btn, PRIMARY, radius=6)
            status_btn.bind(on_press=lambda x: callbacks["complete"](habit["id"]))

        top_row.add_widget(name)
        top_row.add_widget(status_btn)
        self.add_widget(top_row)

        # ==========================================
        # 2. СТРОКА: Описание
        # ==========================================
        desc_text = habit.get("description") or "Без описания"
        description = Label(
            text=desc_text, color=TEXT_SECONDARY, font_size=dp(12),
            halign="left", valign="middle", size_hint_y=None, height=dp(20)
        )
        description.bind(size=description.setter("text_size"))
        self.add_widget(description)

        # ==========================================
        # 3. СТРОКА: Статистика
        # ==========================================
        if stats:
            stat_text = (f"Серия: {stats['current_streak']} дн.  ·  "
                         f"Лучший: {stats['best_streak']}  ·  "
                         f"Всего: {stats['total_completions']}  ·  "
                         f"{stats['completion_rate']}%")
        else:
            stat_text = "Статистика недоступна"

        statistics = Label(
            text=stat_text, color=TEXT_MUTED, font_size=dp(11),
            halign="left", valign="middle", size_hint_y=None, height=dp(20)
        )
        statistics.bind(size=statistics.setter("text_size"))
        self.add_widget(statistics)

        # ==========================================
        # 4. СТРОКА: Действия (Прижаты вправо)
        # ==========================================
        actions = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(24))
        actions.add_widget(Widget())  # Пружина, сдвигающая кнопки вправо

        details_btn = Button(text="Подробнее", color=PRIMARY, font_size=dp(11), background_color=(0,0,0,0), size_hint_x=None, width=dp(75))
        edit_btn = Button(text="Изменить", color=TEXT_SECONDARY, font_size=dp(11), background_color=(0,0,0,0), size_hint_x=None, width=dp(65))
        delete_btn = Button(text="Удалить", color=DANGER, font_size=dp(11), background_color=(0,0,0,0), size_hint_x=None, width=dp(55))

        details_btn.bind(on_press=lambda x: callbacks["details"](habit))
        edit_btn.bind(on_press=lambda x: callbacks["edit"](habit))
        delete_btn.bind(on_press=lambda x: callbacks["delete"](habit["id"]))

        actions.add_widget(details_btn)
        actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        self.add_widget(actions)


class HabitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = BoxLayout(
            orientation="vertical", 
            padding=[dp(16), dp(20), dp(16), dp(16)], 
            spacing=dp(16)
        )

        # ==========================================
        # ШАПКА: Прогресс и Выход
        # ==========================================
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45))
        
        header_text_box = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=1)
        
        today_title = Label(
            text="Сегодня", color=TEXT, font_size=dp(22), bold=True,
            halign="left", valign="bottom", size_hint_y=None, height=dp(24)
        )
        today_title.bind(size=today_title.setter("text_size"))

        stats_box = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(18))
        self.summary = Label(text="0 / 0 выполнено", color=TEXT_MUTED, font_size=dp(13), halign="left", size_hint_x=None, width=dp(105))
        self.progress_label = Label(text="0%", color=PRIMARY, font_size=dp(14), bold=True, halign="left", size_hint_x=None, width=dp(40))
        
        stats_box.add_widget(self.summary)
        stats_box.add_widget(self.progress_label)
        stats_box.add_widget(Widget())  # Спейсер

        header_text_box.add_widget(today_title)
        header_text_box.add_widget(stats_box)

        logout_button = SecondaryButton(
            text="Выйти", color=DANGER, font_size=dp(12),
            size_hint=(None, None), size=(dp(70), dp(32)), pos_hint={"center_y": 0.5}
        )
        logout_button.bind(on_press=self.logout)

        top_bar.add_widget(header_text_box)
        top_bar.add_widget(logout_button)
        self.main_layout.add_widget(top_bar)

        # ==========================================
        # СПИСОК ЗАДАЧ
        # ==========================================
        self.scroll = ScrollView(do_scroll_x=False)
        self.habits_layout = BoxLayout(
            orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[0, dp(10)]
        )
        self.habits_layout.bind(minimum_height=self.habits_layout.setter("height"))
        
        self.scroll.add_widget(self.habits_layout)
        self.main_layout.add_widget(self.scroll)

        # ==========================================
        # КНОПКА: ДОБАВИТЬ ЗАДАЧУ (на всю ширину)
        # ==========================================
        add_button = PrimaryButton(
            text="+ Добавить задачу", font_size=dp(15), bold=True,
            size_hint_y=None, height=dp(48)
        )
        add_button.bind(on_press=self.add_habit)
        self.main_layout.add_widget(add_button)

        self.add_widget(self.main_layout)

    # ==================================================
    # ЛОГИКА ДАННЫХ
    # ==================================================
    def load_habits(self):
        self.habits_layout.clear_widgets()
        app = self.manager.app

        try:
            response = app.api.get_habits()
            if response.status_code != 200:
                self.show_message("Не удалось загрузить задачи")
                return

            habits = response.json()
            if not habits:
                self.summary.text = "0 / 0 выполнено"
                self.progress_label.text = "0%"
                self.show_empty_state()
                return

            completed_count = 0
            
            # Собираем коллбеки в словарь для передачи в HabitRow
            callbacks = {
                "complete": self.complete_habit,
                "uncomplete": self.uncomplete_habit,
                "details": self.open_details,
                "edit": self.edit_habit,
                "delete": self.delete_habit
            }

            for habit in habits:
                stats = self.get_stats(habit["id"])
                if stats and stats.get("completed_today"):
                    completed_count += 1
                
                # Создаем карточку, передав ей всё необходимое
                row = HabitRow(habit, stats, callbacks)
                self.habits_layout.add_widget(row)

            total = len(habits)
            self.summary.text = f"{completed_count} / {total} выполнено"
            self.progress_label.text = f"{round(completed_count / total * 100)}%"

        except Exception as e:
            print(f"Ошибка загрузки привычек: {e}")  # Лучше логировать ошибку, чем делать pass
            self.show_message("Не удалось подключиться к серверу")

    def get_stats(self, habit_id):
        try:
            response = self.manager.app.api.get_stats(habit_id)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
        return None

    def show_empty_state(self):
        container = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(100))
        
        title = Label(
            text="Пока нет задач", color=TEXT, font_size=dp(18), bold=True,
            size_hint_y=None, height=dp(30)
        )
        subtitle = Label(
            text="Добавьте первую задачу, чтобы начать.", color=TEXT_SECONDARY, font_size=dp(13),
            halign="center", valign="middle"
        )
        subtitle.bind(size=subtitle.setter("text_size"))
        
        container.add_widget(Widget())  # Спейсер сверху
        container.add_widget(title)
        container.add_widget(subtitle)
        container.add_widget(Widget())  # Спейсер снизу
        
        self.habits_layout.add_widget(container)

    def show_message(self, text):
        self.habits_layout.clear_widgets()
        label = Label(
            text=text, color=TEXT_SECONDARY, font_size=dp(14),
            halign="center", valign="middle", size_hint_y=None, height=dp(100)
        )
        label.bind(size=label.setter("text_size"))
        self.habits_layout.add_widget(label)

    # API Действия
    def complete_habit(self, habit_id):
        try:
            if self.manager.app.api.complete_habit(habit_id).status_code == 200:
                self.load_habits()
        except Exception as e: print(e)

    def uncomplete_habit(self, habit_id):
        try:
            if self.manager.app.api.uncomplete_habit(habit_id).status_code == 200:
                self.load_habits()
        except Exception as e: print(e)

    def delete_habit(self, habit_id):
        try:
            if self.manager.app.api.delete_habit(habit_id).status_code == 200:
                self.load_habits()
        except Exception as e: print(e)

    # Навигация
    def add_habit(self, instance):
        screen = self.manager.get_screen("habit_form")
        screen.open_for_create()
        self.manager.current = "habit_form"

    def edit_habit(self, habit):
        screen = self.manager.get_screen("habit_form")
        screen.open_for_edit(habit)
        self.manager.current = "habit_form"

    def open_details(self, habit):
        screen = self.manager.get_screen("habit_details")
        screen.load_habit(habit)
        self.manager.current = "habit_details"

    def logout(self, instance):
        self.manager.app.api.logout()
        self.manager.get_screen("login").clear_fields()
        self.manager.current = "login"