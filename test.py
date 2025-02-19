from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

# from main import FrameScreen
class DifficultyScreen(Widget):
    options = ObjectProperty(None)

    def callback(self, instance):
        # Switch screens to loading screen
        # change_page("loading")

        # N.B. The scraping needs to happen on a secondary thread, otherwise
        # the scraping will happen on the main thread and will block the
        # screens from changing until AFTER the processing completes. The
        # Thread target has to be a function/method, NOT a function/method CALL.
        # That means that the target needs to look like this:
        # Thread(target=functionName).start()
        # NOT like this:
        # Thread(target=functionName()).start()
        # That means that we can't pass any arguments because we do that via
        # function/method call. We can work around this by setting the target 
        # like this:
        # Thread(target=partial(functionName, passed_variables).start()

        # Scrape puzzle of selected difficulty
        # Thread(target=partial(scrape_puzzle, instance.text)).start()
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # for child in self.options.children:
        #     child.bind(on_press=self.callback)

class FrameScreen(Widget):
    screens = ObjectProperty(None)

class TestApp(App):
    def build(self):
        # frame = Screen(name="frame")

        screen = FrameScreen()
        # frame.add_widget(screen)

        diff_screen = DifficultyScreen()
        test = DifficultyScreen()

        # carousel = Carousel(direction='right')
        screen.screens.add_widget(diff_screen)
        screen.screens.add_widget(test)

        return screen

if __name__ == '__main__':
    pages=ScreenManager()
    TestApp().run()