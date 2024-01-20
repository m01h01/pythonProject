from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from kivy.core.window import Window

class NameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        name_container = BoxLayout(orientation='vertical', spacing=10, padding=10,size_hint_y=None)

        # Title
        title_label = MDLabel(text="Weekly Wellness Check-in", font_style='H4', size_hint_y=None, height=dp(100))
        name_container.add_widget(title_label)

        name_label = MDLabel(text="Enter your name:")
        self.name_input = MDTextField(hint_text="Your Name")
        name_container.add_widget(name_label)
        name_container.add_widget(self.name_input)


        next_button = MDRaisedButton(text="Next", on_release=self.switch_to_checkin_screen)

        # Set the position of name_container to the center of the screen
        name_container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.add_widget(name_container)
        self.add_widget(next_button)

    def switch_to_checkin_screen(self, instance):
        # Switch to the CheckInScreen
        self.manager.current = 'checkin'

class CheckInScreen(Screen):
    def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.day_inputs = {}

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            # Create a BoxLayout for the content with orientation='vertical'
            content_layout = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)

            # Set the height of the content_layout to match the height of the ScrollView
            content_layout.bind(minimum_height=content_layout.setter('height'))

            for day in days:
                label = MDLabel(text=day, size_hint_y=None, height=30)
                text_input = MDTextField(hint_text=f"How is your mood on {day}? (1 to 5)", size_hint_y=None, height=30)
                content_layout.add_widget(label)
                content_layout.add_widget(text_input)

                self.day_inputs[day] = text_input

            check_in_button = MDRaisedButton(text="Check-in", on_release=self.show_summary)
            content_layout.add_widget(check_in_button)

            # Create a ScrollView and add the content_layout to it
            scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
            scroll_view.add_widget(content_layout)

            self.add_widget(scroll_view)


    def show_summary(self, instance):
        app = MDApp.get_running_app()
        name = app.root.get_screen('name').name_input.text

        # Collect mood ratings for each day
        mood_ratings = {}

        # Iterate over the items in self.day_inputs
        for day, text_input in self.day_inputs.items():

            # Get the mood rating from the text input
            mood_rating = text_input.text

            # Check if mood_rating is a digit before attempting to convert to int
            if mood_rating.isdigit():
                mood_ratings[day] = int(mood_rating)
            else:
                self.show_error_dialog(f"Please enter a valid integer mood rating for {day}")

        # Perform any necessary validation or further processing
        if all(1 <= rating <= 5 for rating in mood_ratings.values()):
            self.save_check_in(name, mood_ratings)

            # Calculate the average mood rating
            average_rating = sum(mood_ratings.values()) / len(mood_ratings)

            # Get additional information based on the average rating
            additional_info = self.get_additional_info(average_rating)

            # Display the summary pop-up with average rating and additional information
            self.show_summary_popup(name, mood_ratings, average_rating, additional_info)
        else:
            self.show_error_dialog("Please enter valid mood ratings between 1 and 5 for each day.")

    def show_error_dialog(self, message):
        dialog = MDDialog(title="Error", text=message, size_hint=(0.8, 0.4))
        dialog.open()

    def save_check_in(self, name, mood_ratings):
        today = datetime.now().date()
        with open(f"check_ins_{today}.txt", "a") as file:
            file.write(f"{name}: Mood ratings - {mood_ratings}\n")

    def get_additional_info(self, average_rating):
        if 1 <= average_rating < 3:
            return "Your mood indicates it's a challenging time for you. Reach out for support if needed."
        elif 3 <= average_rating < 5:
            return "You're doing okay. Keep up the good work!"
        elif average_rating == 5:
            return "Fantastic! Your mood suggests you're having a great week!"
        else:
            return ""

    def show_summary_popup(self, name, mood_ratings, average_rating, additional_info):
        summary_text = f"Check-in summary for {name}:\n {mood_ratings}\n\n" \
                       f"Average Mood Rating: {average_rating:.2f}\n" \
                       f"{additional_info}"

        dialog = MDDialog(
            title="Check-in Summary",
            text=summary_text,
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda *args: self.dialog_dismiss(dialog))
            ],
        )

        dialog.open()

    def dialog_dismiss(self, dialog):
        dialog.dismiss()
class MentalApp(MDApp):
    def build(self):
        sm = ScreenManager()
        name_screen = NameScreen(name='name')
        checkin_screen = CheckInScreen(name='checkin')

        sm.add_widget(name_screen)
        sm.add_widget(checkin_screen)

        return sm
if __name__ == "__main__":
    MentalApp().run()
