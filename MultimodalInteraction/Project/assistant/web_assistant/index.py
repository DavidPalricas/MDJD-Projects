from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from web_assistant.web_assistant import WebAssistant

class Index(WebAssistant):
    def __init__(self):
        super().__init__()
        self.driver = self.chrome_config()
        self.open()
    
    def chrome_config(self):

        chrome_options = Options()
        
        # Giving the browser permission to use only the microphone
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1, 
            "profile.default_content_setting_values.media_stream_camera": 0,  
            "profile.default_content_setting_values.geolocation": 0  
        })

        return webdriver.Chrome(options=chrome_options)
    
    def open(self) :
         self.driver.get("https://127.0.0.1:8082/index.htm")
         self.driver.maximize_window()
         self.load_page()
    
    

    def load_page(self):
        time.sleep(3)