import time
class WebAssistant():
    def __init__(self):
        self.driver = None

    def chrome_config(self):
       raise NotImplementedError
    
    def open(self):
        raise NotImplementedError
    
    def load_page(self):
          time.sleep(3)
