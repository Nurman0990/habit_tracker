from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from ui.colors import BG

from services.api import API

from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.habits import HabitsScreen
from screens.habit_form import HabitFormScreen
from screens.habit_details import HabitDetailsScreen
from screens.dashboard import DashboardScreen

Window.clearcolor = BG

class HabitTrackerApp(App):

    def build(self):

        self.api = API()

        manager = ScreenManager()

        manager.add_widget(
            LoginScreen(
                name="login"
            )
        )

        manager.add_widget(
            RegisterScreen(
                name="register"
            )
        )

        manager.add_widget(
            HabitsScreen(
                name="habits"
            )
        )

        manager.add_widget(
            HabitFormScreen(
                name="habit_form"
            )
        )

        manager.add_widget(
            HabitDetailsScreen(
                name="habit_details"
            )
        )

        manager.add_widget(
            DashboardScreen(
                name="dashboard"
            )
        )

        manager.app = self

        # Проверяем сохранённый токен
        if self.api.token:

            user = self.api.get_me()

            if user:

                manager.current = "habits"

                manager.get_screen(
                    "habits"
                ).load_habits()

            else:

                manager.current = "login"

        else:

            manager.current = "login"

        return manager


if __name__ == "__main__":
    HabitTrackerApp().run()