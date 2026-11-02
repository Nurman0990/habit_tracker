import json
import os

import requests


API_URL = "http://127.0.0.1:8000"

TOKEN_FILE = "token.json"


class API:

    def __init__(self):
        self.token = None
        self.load_token()

    # ==================================================
    # TOKEN STORAGE
    # ==================================================

    def load_token(self):

        if not os.path.exists(TOKEN_FILE):
            return

        try:

            with open(
                TOKEN_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.token = data.get(
                "access_token"
            )

        except Exception:

            self.token = None

    def save_token(self, token):

        self.token = token

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "access_token": token
                },
                file
            )

    def delete_token(self):

        self.token = None

        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    # ==================================================
    # AUTH
    # ==================================================

    def login(self, username, password):

        response = requests.post(
            f"{API_URL}/login",
            data={
                "username": username,
                "password": password
            },
            timeout=10
        )

        if response.status_code != 200:
            return False, "Invalid username or password"

        data = response.json()

        self.save_token(
            data["access_token"]
        )

        return True, data

    def register(self, username, password):

        response = requests.post(
            f"{API_URL}/register",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )

        return response

    def get_me(self):

        if not self.token:
            return None

        try:

            response = requests.get(
                f"{API_URL}/me",
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code == 401:
                self.delete_token()

        except Exception:
            pass

        return None

    def logout(self):

        self.delete_token()

    # ==================================================
    # HEADERS
    # ==================================================

    def get_headers(self):

        return {
            "Authorization": f"Bearer {self.token}"
        }

    # ==================================================
    # HABITS
    # ==================================================

    def get_habits(self):

        response = requests.get(
            f"{API_URL}/habits",
            headers=self.get_headers(),
            timeout=10
        )

        return response

    def create_habit(
        self,
        name,
        description=""
    ):

        response = requests.post(
            f"{API_URL}/habits",
            json={
                "name": name,
                "description": description
            },
            headers=self.get_headers(),
            timeout=10
        )

        return response

    def update_habit(
        self,
        habit_id,
        name,
        description=""
    ):

        response = requests.put(
            f"{API_URL}/habits/{habit_id}",
            json={
                "name": name,
                "description": description
            },
            headers=self.get_headers(),
            timeout=10
        )

        return response

    def delete_habit(
        self,
        habit_id
    ):

        response = requests.delete(
            f"{API_URL}/habits/{habit_id}",
            headers=self.get_headers(),
            timeout=10
        )

        return response

    # ==================================================
    # COMPLETION
    # ==================================================

    def complete_habit(
        self,
        habit_id
    ):

        response = requests.post(
            f"{API_URL}/habits/{habit_id}/complete",
            headers=self.get_headers(),
            timeout=10
        )

        return response

    def uncomplete_habit(
        self,
        habit_id
    ):

        response = requests.delete(
            f"{API_URL}/habits/{habit_id}/complete",
            headers=self.get_headers(),
            timeout=10
        )

        return response

    # ==================================================
    # STATISTICS
    # ==================================================

    def get_stats(
        self,
        habit_id
    ):

        response = requests.get(
            f"{API_URL}/habits/{habit_id}/stats",
            headers=self.get_headers(),
            timeout=10
        )

        return response

    # ==================================================
    # CALENDAR
    # ==================================================

    def get_calendar(
        self,
        habit_id,
        year,
        month
    ):

        response = requests.get(
            f"{API_URL}/habits/{habit_id}/calendar",
            params={
                "year": year,
                "month": month
            },
            headers=self.get_headers(),
            timeout=10
        )

        return response

        # ==================================================
    # DASHBOARD
    # ==================================================

    def get_dashboard(self):

        response = requests.get(
            f"{API_URL}/dashboard",
            headers=self.get_headers(),
            timeout=10
        )

        return response