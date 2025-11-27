from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import requests

class Dashboard(BoxLayout):
    def load_kpis(self):
        r = requests.get("https://analystic.a/api/kpis")
        data = r.json()
        self.ids.members.text = str(data["members"])

class AnalysticAApp(App):
    def build(self):
        return Dashboard()

AnalysticAApp().run()
