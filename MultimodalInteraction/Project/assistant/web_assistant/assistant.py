import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from web_assistant.web_assistant import WebAssistant
from consts import OUTPUT
from web_app_conextions_files.index_connections import TTS, Confirmation
from video import Video
import time

class Assistant(WebAssistant):
    """
      The Assistant class is responsible for handling the assistant's actions and interactions with the user.
      The class has the following attributes:
        - tts: an instance of the TTS class.
        - driver: a google chrome driver.
        - video: an instance of the Video class.
        - running: a boolean that indicates if the assistant is running or not.
        - action_to_be_confirmed: a dictionary that contains the nlu to be confirmed.
    """

    def __init__(self): 
        """
          Initializes a new instance of the Assistant class, and initializes the TTS class and initializes the chrome driver by calling the chrome_config. 
          The construcotr calls the initialize_assistant method.
        """
        self.tts = TTS(FusionAdd=f"https://{OUTPUT}/IM/USER1/APPSPEECH")
        self.confirmation = Confirmation(FusionAdd=f"https://{OUTPUT}/IM/USER1/SPEECH_ANSWER")
        self.send_to_voice("Iniciando o  assistente, aguarde um pouco")
        super().__init__()
        self.driver = self.chrome_config()
        self.video = None
        self.running = True
        self.user_subscibed_channel = False
        self.wait = WebDriverWait(self.driver, 5)
        self.intent_to_be_confirmed = None

        self.items_to_be_searched = []
        
        self.video_or_contact = None

        self.message_to_be_sent = ""


        self.initialize_assistant()
      
    def chrome_config(self):
       """ The chrome_config method is responsible for configuring the chrome options.
          The method will add the user data directory and the profile directory to the chrome options.
         Returns:
              - An instance of the WebDriver class which repsents a chorme driver.
       """
       chrome_options = Options()
       
       # This line is equivalant to this : C:\Users\{user}\AppData\Local\Google\Chrome\User Data
       user_data_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")

       chrome_options.add_argument(f"user-data-dir={user_data_dir}")

       profile_directory = "Default"

       chrome_options.add_argument(f"--profile-directory={profile_directory}")
       #chrome_options.add_argument("--disable-extensions")
    
       return webdriver.Chrome(options=chrome_options)
    
    def initialize_assistant(self):
        """
        The initialize_assistant method is responsible for initializing the assistant by opening the browser and sending a message to the user.
        """
        self.open("https://www.youtube.com")
        self.send_to_voice("Olá, como posso te ajudar?")
            
    def send_to_voice(self, message):
        """
        The send_to_voice method is responsible for sending a message to the user using the TTS class's sendo_voice method.
        """
        self.tts.sendToVoice(message) 

    def open(self, url) :
        """
        The open method is responsible for opening a URL in the browser, accepting the cookies by calling the 
         accept_cookies method and maximizing the window.

         Args:
            - url: a string that represents the URL to be opened.
        """
        self.driver.get(url)
        self.driver.maximize_window()
        self.accept_cookies()
        time.sleep(2)

    def accept_cookies(self):
        """
        The accept_cookies method is responsible for accepting the cookies on the page.
        """
        try:
            # Identify and click the button to accept cookies using text content or classes
            accept_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(), 'Aceitar tudo')] or .//span[contains(text(), 'Accept all')]]")
            ))
            accept_button.click()
        except Exception:
            pass
   

  
    def get_add_time(self):
        """
        The get_add_time method is responsible for getting the time of the ad.
        The method will try to find the ad time, if the time is found, the method will return the time.
        Otherwise, the method will return 5 seconds.
        """
        try:
            add_current_time = self.driver.find_element(By.XPATH, '//div[@class="ytp-ad-preview-container"]//span[@class="ytp-ad-preview-time"]')
            add_max_time = self.driver.find_element(By.XPATH, '//div[@class="ytp-ad-preview-container"]//span[@class="ytp-ad-preview-total-time"]')
             
            add_current_time = add_current_time.text.split(":")[1]
            add_max_time = add_max_time.text.split(":")[1]

            return int(add_max_time) - int(add_current_time)
    
        except Exception:
            return  None
         
                                       
    def handling_search_message(self, query):
        """
        The handling_search_message method is responsible for handling the search message.
        If the query contains the word "vídeo" or "vídeos", the method will remove the word from the query.
        And send a message to the user informing that the assistant is searching for the video.

        Args:
            - query: a string that represents the video to be searched.
        """
        if "vídeo" in query:
            query = query.replace("vídeo", "")  

        elif "vídeos" in query:
            query = query.replace("vídeos", "")  
            self.send_to_voice(f"Pesquisando por vídeos {query}")
            return 
        
        self.send_to_voice(f"Pesquisando pelo vídeo {query}")

    def search_video(self, query):
        """
        Searches for a video on YouTube and lets the user choose one of the top three results.
        This method searches YouTube for the provided query, presents the top three results to the user,
        and lets them choose which video to play.

        Args:
            - query: a string that represents the video to be searched.
        """
        self.handling_search_message(query)

        if self.video is not None and self.video.is_fullscreen:
            self.video.youtube.send_keys("f")

        # Open YouTube search results page
        self.driver.get('https://www.youtube.com/results?search_query={}'.format(str(query)))
        
        time.sleep(5)

        visible = EC.visibility_of_element_located
        self.wait.until(visible((By.ID, "video-title")))

        # Get all visible video elements
        videos = self.driver.find_elements(By.ID, "video-title")
        
        time.sleep(2.5)

        # Extract the top three non-promoted videos
        for video in videos:
            if "promoted" not in video.get_attribute("class"):
                self.items_to_be_searched.append(video)
            if len(self.items_to_be_searched) == 3:  # Limit to top 3 videos
                break

        if self.items_to_be_searched == []:
            self.send_to_voice("Nenhum vídeo encontrado")
            return
        
        self.video_or_contact = False

        # Display the options to the user
        message = "Vídeos encontrados:\n"

        for i, title in enumerate(self.items_to_be_searched):
            message += f"{i + 1} - {title.text}\n"
        print(message)

        self.send_to_voice(message)
        
        # Delay to wait to assistant to finish speaking
        time.sleep(15)

        self.send_to_voice("Escolha um dos vídeos por ordem, ou seja, primeiro, segundo ou terceiro")
        
        # Delay to wait to assistant to finish speaking
        time.sleep(2)

        self.confirmation.confirm()

    def select_item(self, choice):
        """
        The select_item method is responsible for selecting the item based on the user's choice.
        The method will check the user's choice and select the video based on the choice.
        If the choice is invalid, the method will send a message to the user informing that the choice is invalid and ask the user to try again.
        """

       # possible_choices = ["primeiro", "segundo", "terceiro", "1º", "2º", "3º", "Selecionar o primeiro", "Selecionar o segundo", "Selecionar o terceiro", "Seleciona o primeiro", "Seleciona o segundo", "Seleciona o terceiro"]

       
        if "1º" in choice.lower() or "primeiro" in choice.lower():
            choice = 0
        elif "2º" in choice.lower() or "segundo" in choice.lower():
            choice = 1
        elif "3º" in choice.lower() or "terceiro" in choice.lower():
            choice = 2
        else:
            self.send_to_voice("Escolha inválida, tente novamente")
            self.confirmation.confirm()
            return
        if self.video_or_contact:
            chosen_span = self.items_to_be_searched[choice]
            chosen_span.click()
            
             # Confirm the user wants to send the respective message
            self.intent_to_be_confirmed = {"intent": "send_message"}
            self.send_to_voice("Deseja enviar a mensagem?")
            self.confirmation.confirm()   
        else:
            video = self.items_to_be_searched[choice]
            self.send_to_voice(f"Selecionando o vídeo {video.text}")
            self.items_to_be_searched = []
            self.video_or_contact = None

            video.click()
                
            if "shorts" in self.driver.current_url:
                self.video = Video(True, self.driver)
            else:

                   
                self.video = Video(False, self.driver) if self.video is None else Video(False, self.driver, self.video.speed)
                print(f"speed {self.video.speed}")
                self.video.url = self.driver.current_url

    def send_message_to_contact(self):
        inp_xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]'
        input_box = WebDriverWait(self.driver,50).until(EC.presence_of_element_located((By.XPATH, inp_xpath)))
        time.sleep(2)

        # write message
        input_box.send_keys(self.message_to_be_sent)
        input_box.send_keys(Keys.ENTER)
         
        self.send_to_voice("Vídeo enviado com sucesso")
    
        time.sleep(2)

        # Close the WhatsApp tab
        self.driver.close()

        # Return to the YouTube tab
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.items_to_be_searched = []
        self.video_or_contact = None

    def close_whatsapp_tab(self):
        """
        The close_whatsapp_tab method is responsible for closing the whatsapp tab.
        """
        self.driver.close()

        self.driver.switch_to.window(self.driver.window_handles[0])
        self.items_to_be_searched = []
        self.video_or_contact = None

    def shutdown(self) :
        """
        The shutdown method is responsible for shutting down the assistant.
        Before shutting down the assistant, the method will send a message to the user informing that the assistant is shutting down.
        """
        self.send_to_voice("Adeus, espero ter o ajudado")
        time.sleep(2)
        self.running = False  
        print("Shutting down assistant...")

        # To check if the user by mistake closes the browser, otherwise the browser will be closed
        if self.driver:
            self.driver.quit()  

    def write_comment(self, comment):
        """
        The write_comment method is responsible for calling the right method to  write a comment on a YouTube video, and warning the user that the assistant is writing the comment.
        If the video is a short video, the method will call the write_comment_short_video method otherwise it will call the write_comment_long_video method.
    
        Args:
            - comment: a string that represents the comment to be written.
        """

        self.send_to_voice(f"Escrevendo o comentário {comment}")

        if self.video.is_short:
            self.write_comment_short_video(comment)

        else:
            self.write_comment_long_video(comment)
        
    def write_comment_short_video(self, comment):
        """
        The write_comment_short_video method is responsible for writing a comment on a short video.
        The method will click on the comment button, and try to find the comment box, if the comment box is not found, the method will send a message to the user informing that the comment box was not found or the comments are disabled.
        Otherwise, the find_comment_box method will be called to write the comment.

        Args:
            - comment: a string that represents the comment to be written.
   
        """

        comment_button = self.driver.find_element(By.ID, "comments-button")
        comment_button.click()
       
        # Time to the comment box to load
        time.sleep(3)

        try:
            self.find_comment_box(comment)

        except NoSuchElementException:
            self.send_to_voice("Erro ao escrever o comentário, a caixa de comentários não foi encontrada ou os comentários estão desativados")

    def write_comment_long_video(self, comment):
        """
        The write_comment_long_video method is responsible for writing a comment on a long video.
        The method will scroll down the yotube page to find the comment box, if the comment box is not found, the method will send a message to the user informing that the comment box was not found or the comments are disabled.
        Otherwise, the find_comment_box method will be called to write the comment.
        In the end, the method will scroll to the beginning of the page.

        Args:
            - comment: a string that represents the comment to be written. 
        """

        scroll_to_comments = 0
        old_position = 0

        while True:
            # To give time to the comment box to load
            time.sleep(3)
            
            try:
                self.find_comment_box(comment)
                 
                # Time to the user to see the comment
                time.sleep(5)
                break

            except NoSuchElementException:
                old_position = scroll_to_comments 
                scroll_to_comments += 500
                self.driver.execute_script(f"window.scrollTo({old_position},{scroll_to_comments});")

                if scroll_to_comments > 8000:
                    self.send_to_voice("Erro ao escrever o comentário, a caixa de comentários não foi encontrada ou os comentários estão desativados")
                    break

        # Scroll to the beginning of the page
        self.driver.execute_script("window.scrollTo(0,0);")
           
    def find_comment_box(self, comment):
        """
        The find_comment_box method is responsible for finding the comment box, clicking on it, and writing the comment in this box.
    
        After that, the method will send a message to the user informing that the comment was written successfully.

        Args:
            - comment: a string that represents the comment to be written.

        """

        comment_box = self.driver.find_element(By.ID, "simplebox-placeholder")

        comment_box.click()

        add_comment_box = self.driver.find_element(By.ID, "contenteditable-root")

        add_comment_box.send_keys(comment)
        
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.RETURN).key_up(Keys.CONTROL).perform()
            
        self.send_to_voice("Comentário escrito com sucesso")

    def save_to_playlist(self, playlist):
        """The save_to_playlist method is responsible for trying to save a video into a playlist.
           This methods starts to inform the user that the video is being saved in the playlist.
           The method will call the find_save_option method to find the save option, and the playlist to save the video.
           If the save option is not found, the method will send a message to the user informing that the save option was not found.

            Args:
                - playlist: a string that represents the name of the  playlist to save the video.
        """
        
        self.send_to_voice(f"Guardando o vídeo na playlist {playlist}")

        try:
            self.find_save_option(playlist)
           
        except NoSuchElementException:
            self.send_to_voice("Erro ao guardar o vídeo na playlist, o botão para guardar o vídeo não foi encontrado")
        
    def find_save_option(self, playlist):
        """
            The find_save_option method is responsible for finding the save option and the playlist to save the video.
            After the save option is found, the method will store the playlists names ands its checkboxes in a list, and  call the playlist_exits method to check if the searched playlist exists.
            If the searched playlist does not exist, the method will send a message to the user informing that the playlist was not found.
            In the end, the method will call the close_playlist_menu method to close the playlist menu.

            Args:
                - playlist: a string that represents the name of the playlist to save the video.   
        """

        more_options = self.driver.find_element(By.XPATH, '//*[@id="button-shape"]/button')

        more_options.click()

        save_option = self.driver.find_element(By.XPATH, '//*[@id="items"]/ytd-menu-service-item-renderer[2]')

    
        save_option.click()

        time.sleep(2)

        playlists_container = self.driver.find_elements(By.XPATH, '//ytd-playlist-add-to-option-renderer//tp-yt-paper-checkbox[@id="checkbox"]')
        
        # Not use is not, becuase this method can return a None value
        if self.playlist_exits(playlists_container, playlist) == False:
            self.send_to_voice(f"Erro ao guardar o vídeo na playlist, a playlist {playlist} não foi encontrada")

        time.sleep(2)

        self.close_playlist_menu()

    def close_playlist_menu(self):
        """
        The close_playlist_menu method is responsible for closing the playlist menu.
        The method will try to find the close palylist menu button in two different languages(english and portuguese), if the button is found, the method will click on it.
        Otherwise, the method will send a message to the user informing that there was an error closing the menu, and refresh the page.
        """
        try:
            close_menu = self.driver.find_element(By.XPATH, '//*[@id="button" and @aria-label="Cancel"]')
        except NoSuchElementException:
            try:    
                close_menu = self.driver.find_element(By.XPATH, '//*[@id="button" and @aria-label="Cancelar"]')
            except NoSuchElementException:
                 self.send_to_voice("Erro ao fechar o menu de opções, dando refresh na página")
                 self.driver.refresh()

        try:
            close_menu.click()
        except Exception as ex:
            self.send_to_voice("Erro ao fechar o menu de opções, dando refresh na página")
            self.driver.refresh()
           

    def playlist_exits(self, playlists_container, playlist):
       """
         The playlist_exits method is responsible for checking if the playlist exists.
         The method will iterate over the playlists founded and check if the searched playlist name matches for any playlist.
         If the playlist is found, the method will click on the playlist checkbox and send a message to the user informing that the video was saved in the playlist.

         Args:
            - playlists_container: a list that contains the container of the playlists(names and checkboxes).
            - playlist: a string that represents the name of the playlist to save the video.

        Returns:
            - True if the playlist was found, otherwise False.
       """

       for playlist_container in playlists_container:
            playlist_name = playlist_container.find_element(By.XPATH, './/yt-formatted-string[@id="label"]').text.lower()

            if playlist_name == playlist.lower():
                if playlist_container.get_attribute("aria-checked") == "true":
                    self.send_to_voice("Este vídeo já está guardado nesta playlist")
                    return None
                
                playlist_container.click()
                self.send_to_voice("Vídeo guardado na playlist com sucesso")
                return True
            
       return False
    
    def close_playlist_menu(self):
        """
        The close_playlist_menu method is responsible for closing the playlist menu.
        The method will try to find the close palylist menu button in two different languages(english and portuguese), if the button is found, the method will click on it.
        Otherwise, the method will send a message to the user informing that there was an error closing the menu, and refresh the page.

        """
        try:
            close_menu = self.driver.find_element(By.XPATH, '//*[@id="button" and @aria-label="Cancel"]')

        except NoSuchElementException:
            try:    
                close_menu = self.driver.find_element(By.XPATH, '//*[@id="button" and @aria-label="Cancelar"]')

            except NoSuchElementException:
                close_menu = None  

        if close_menu:
            close_menu.click()
        else:
            self.send_to_voice("Erro ao fechar o menu de opções, dando refresh na página")
            self.driver.refresh()

    def handle_channel_subscription(self,intent):
        """
        The subscribe_channel method is responsible for subscribing to a YouTube channel.
        The method will try to find the subscribe button, if the button is found, the method will click on it and send a message to the user informing that the channel was subscribed successfully.
        Otherwise, the method will send a message to the user informing that there was an error subscribing to the channel.
        """
        try:
            subscribe_button = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/div/ytd-subscribe-button-renderer")

        except Exception as ex:
            self.send_to_voice("Erro ao se inscrever no canal, botão de inscrição não encontrado")
            print(f"Exception {ex}")
            return
            
        if intent == "subscribe_channel":
            self.subscribe_channel(subscribe_button)
        else:
            self.unsubscribe_channel(subscribe_button)
            
        
    def subscribe_channel(self, subscribe_button): 
        if  subscribe_button.get_attribute("subscribed")== "true":
            self.send_to_voice("Você já está inscrito neste canal")
            time.sleep(2)
            self.intent_to_be_confirmed = {"intent":"unsubscribe_channel"}
            self.send_to_voice("Deseja cancelar a inscrição?")
            self.confirmation.confirm()
            return
        
        subscribe_button.click()
        self.send_to_voice("Canal inscrito com sucesso")

        time.sleep(2)

        self.send_to_voice("Desja ativar todas as notifcações do canal,desativa-las ou manter as configurações atuais?")
       
        self.user_subscibed_channel = True

        self.confirmation.confirm()


    def handling_notifications(self, intent):

        if intent == "mantain_notifications":
            self.send_to_voice("Preferências atuais, mantida com sucesso")     
        else:   
           xpath = None

           if intent == "activate_notifications":
              xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/div/ytd-subscribe-button-renderer"
           else:
                xpath = "/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-menu-popup-renderer/tp-yt-paper-listbox/ytd-menu-service-item-renderer[3]"
            
           self.desactive_activate_notifications(xpath,intent)
   
        self.user_subscibed_channel = False

    
    def desactive_activate_notifications(self, xpath,intent):
        try:
          subscribe_button = self.driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/div/ytd-subscribe-button-renderer")
          subscribe_button.click()

          time.sleep(2)

          activate_notifications_button = self.driver.find_element(By.XPATH, xpath)
          activate_notifications_button.click()

        except Exception as ex:
            self.send_to_voice("Erro ao alterar as notificações do canal")
            print(f"Exception {ex}")
            return
        
        if intent == "activate_notifications":
          self.send_to_voice("Todas as notificações do canal foram ativadas com sucesso")

        else:
            self.send_to_voice("Todas as notificações do canal foram desativadas com sucesso")

    def unsubscribe_channel(self, subscribe_button):
        if  subscribe_button.get_attribute("subscribed")== "false":
            self.send_to_voice("Você não está inscrito neste canal")
            return
        
        subscribe_button.click()

        try:
            unsubscribe_button = self.driver.find_element(By.XPATH, "/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-menu-popup-renderer/tp-yt-paper-listbox/ytd-menu-service-item-renderer[4]")
            unsubscribe_button.click()

        except Exception as ex:
            self.send_to_voice("Erro ao cancelar a inscrição no canal, botão de inscrição não encontrado") 
            print(f"Exception {ex}")
            return
        
        time.sleep(2)
        
        try:
            confirm_unsubscribe_button = self.driver.find_element(By.XPATH, '//*[@id="confirm-button"]')
            confirm_unsubscribe_button.click()

        except Exception as ex:
            self.send_to_voice("Erro ao cancelar a inscrição no canal, botão de confirmação não encontrado")
            print(f"Exception {ex}")
            return
        
 
        self.send_to_voice("Inscrição cancelada com sucesso")
   
    def confirm_action(self, nlu):
        """The confirm_action method is responsible for confirming the action based on the user's intent.
            If the entity's confidence is less than 45 or the assistant did not recognize any entity, the method will call the not_understood method.
            Otherwise, the method will call the ask_confirmation method to ask the user to confirm the action.
            These entiy confidance values are based on the values given by the slides of the course.

            Args:
                - nlu: a dictionary that contains the intent , entity and the entiy's confidance of the user's message.
        """

        if "confidence" not in nlu or nlu["confidence"] < 45:
            self.not_understood(nlu["intent"])
        else: 
           self.intent_to_be_confirmed = nlu
           self.ask_confirmation(nlu["intent"], nlu["entity"])
    
    def ask_confirmation(self, intent, entity):
        """ The ask_confirmation method is responsible for asking the user to confirm the action.
            The method will load the confirmation_messages.json file, and send a message to the user asking for confirmation.

            Args:
                - intent: a string that represents the intent of the user's message.
                - entity: a string that represents the entity of the user's message.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "confirmation_messages.json")

            with open(file_path, "r", encoding = "utf-8") as file:
                message = json.load(file)
                
                if entity is None:
                    self.send_to_voice(message[intent])
                else:
                    self.send_to_voice(message[intent].format(entity = entity))
            

            self.confirmation.confirm()

        except Exception as ex:
            print(f"Exception {ex}")
            self.send_to_voice("Erro ao confirmar o seu pedido")
            return

    def not_understood(self, intent):
        """The not_understood method is responsible for sending a message to the user informing that the assistant did not understand the user's message.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "not_understood_messages.json")

            with open(file_path, "r", encoding = "utf-8") as file:
                message = json.load(file)
                self.send_to_voice(message[intent])

        except Exception as ex:
            print(f"Exception {ex}")
            self.send_to_voice("Erro ao entender o seu pedido")
            return
        
    def read_help_options(self, entity):
        """
        The read_help_options method is responsible for reading the help options based on the user's choice.
        
        Args:
            - entity: a string that represents the user's choice.
            
        """

        print(f"Entity: {entity}")
       
        files_to_read = []

        if "voz" in entity:
            files_to_read.append("voice.txt")

        if "gestos" in entity:
            files_to_read.append("gestures.txt")

        if "fusão" in entity:
            files_to_read.append("fusion.txt")

        if "todas" in entity or "todos" in entity:
            files_to_read = ["voice.txt", "gesture.txt", "fusion.txt"]

        if files_to_read == []:
            self.send_to_voice("Desculpe, pelo incómodo")
            return
    
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            help_messages_dir = os.path.join(current_dir, "help_messages")

            for file in files_to_read:

                print(f"File: {file}")
                file_path = os.path.join(help_messages_dir, file)
        
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line != "\n":
                            self.send_to_voice(line)
                            time.sleep(3.5)

        except Exception as ex:
            print(f"Exception {ex}")
            self.send_to_voice("Erro ao mostrar a ajuda")

    
    def speech_action(self, nlu):
        """
        The speech_action method is responsible for executing the action based on the user's intent.

        Args:
            - nlu: a dictionary that contains the intent and entity of the user's message.
        """
        match nlu["intent"]:
            case "choose_item":
                if "confidence" not in nlu or nlu["confidence"] < 80:
                    self.confirm_action(nlu)
                else:
                    self.select_item(nlu["entity"])

            case "send_message":
                self.send_message_to_contact()

            case "search_video":
                if "confidence" not in nlu or nlu["confidence"] < 80:
                    self.confirm_action(nlu)
                else:
                    self.search_video(nlu["entity"])

            case "skip_ad":
                self.skip_ad()

            case "shutdown_assistant":
                if self.intent_to_be_confirmed  == {"intent":"shutdown_assistant"}:
                    self.shutdown()
                else:
                    self.intent_to_be_confirmed = {"intent":"shutdown_assistant"}
                    self.ask_confirmation(nlu["intent"], None)

            case "pause_video" | "play_video":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para pausar")
                else:
                   self.video.handling_play_pause(self.send_to_voice,nlu["intent"])

            case "increase_speed" | "decrease_speed" | "alternate_speed":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para alterar a velocidade")
                else:
                    if self.video.is_short:
                        self.send_to_voice("Não é possível alterar a velocidade de shorts")
                        return
                    
                    if "confidence" not in nlu or nlu["confidence"] < 80:
                        self.confirm_action(nlu)
                    else:
                        del nlu["confidence"]
                        self.video.change_speed(self.send_to_voice,nlu)
            
            case "write_comment":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para comentar")
                else:
                      if "confidence" not in nlu or nlu["confidence"] < 80:
                        self.confirm_action(nlu)
                      else:
                        self.write_comment(nlu["entity"])

            case "activate_video_subtitles" | "deactivate_video_subtitles":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para ativar ou desativar as legendas")
                else:
                    self.video.on_off_video_subtitles(self.send_to_voice,nlu["intent"])
            
            case "mute_video" | "unmute_video":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para ativar ou desativar o som")
                else:
                    self.video.mute_unmute_video(self.send_to_voice,nlu["intent"])

            case "seek_forward_video" | "seek_backward_video":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para avançar ou retroceder")
                else:
                    if "confidence" not in nlu or nlu["confidence"] < 80:
                        self.confirm_action(nlu)
                    else:
                        video_url = self.video.seek_forward_backward(self.send_to_voice,nlu["intent"], nlu["entity"])

                        if video_url is not None:
                            self.open(video_url)
                            self.video.youtube = self.driver.find_element("tag name", "body")

            case "save_to_playlist":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para salvar na playlist")
                else:
                    if "confidence" not in nlu or nlu["confidence"] < 80:
                        self.confirm_action(nlu)
                    else:
                        self.save_to_playlist(nlu["entity"])

            case "share_video":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para compartilhar")
                else:
                    if "confidence" not in nlu or nlu["confidence"] < 80:
                        self.confirm_action(nlu)
                    else:
                        self.video_or_contact, self.message_to_be_sent = self.video.share_video(self.send_to_voice,nlu["entity"], self.items_to_be_searched)

            case "subscribe_channel" | "unsubscribe_channel":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para se inscrever")
                else:
                    self.handle_channel_subscription(nlu["intent"])       

            case  "activate_notifications" | "mantain_notifications" | "desactivate_notifications":
                if not self.user_subscibed_channel:
                    self.send_to_voice("Não se subscreveu a nenhum canal. para gerir as notificações")
                else:
                    self.handling_notifications(nlu["intent"])

            case "affirm":
                if self.intent_to_be_confirmed is None:
                    self.send_to_voice("Não há nenhuma ação para confirmar")

                else:
                    if "confidence" in self.intent_to_be_confirmed:
                        self.intent_to_be_confirmed["confidence"] = 100

                    self.speech_action(self.intent_to_be_confirmed)
                    self.intent_to_be_confirmed = None

            case "deny":
                if self.intent_to_be_confirmed is None:
                    self.send_to_voice("Não há nenhuma ação para negar")
                elif self.intent_to_be_confirmed == {"intent":"send_message"}:
                    self.send_to_voice("Desculpe pelo engano")
                    self.close_whatsapp_tab()
                    self.intent_to_be_confirmed = None
                else:
                    self.intent_to_be_confirmed = None
                    self.send_to_voice("Peço desculpa pela confusão")

            case "help":
                self.intent_to_be_confirmed = nlu["intent"]

                self.send_to_voice("Que modalides de ajuda deseja, voz, gestos, fusão ou todas?") 
                self.confirmation.confirm()

            case "choose_help_options":
                if self.intent_to_be_confirmed != "help":
                    self.send_to_voice("Para obter ajuda, primeiro peça ajuda")                    
                    return
                
                self.intent_to_be_confirmed = None
                self.read_help_options(nlu["entity"])

            case _:
                self.send_to_voice("Desculpe, não entendi o que você disse")

    def gesture_action(self, gesture):
        match gesture:
            case "DISLIKE":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para dar dislike")
                else:
                    self.video.dislike_video(self.send_to_voice)

            case "LIKE":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para dar like")
                else:
                    self.video.like_video(self.send_to_voice)
         
            case _:
                print(f"Gesture:", gesture)
                print(gesture)
                self.send_to_voice("Desculpe, não entendi o que você disse")


    def dislike_video(self, send_to_voice):
        """
        The method dislike_video is responsible for disliking a video on YouTube.
        The method also sends a message to the user to inform the action.

        Args:
            - send_to_voice: a function that sends a message to the user.
        """
        try:
            # Locate the dislike button using XPath
            dislike_button = self.driver.find_element(By.XPATH, "//button[@title='I dislike this' or @title='Não gosto disto']")
            

            if "aria-pressed" in dislike_button.get_attribute("outerHTML"):
                if dislike_button.get_attribute("aria-pressed") == "true":
                    send_to_voice("Já deu dislike no vídeo.")
                    return
                
            ActionChains(self.driver).move_to_element(dislike_button).perform()
            dislike_button.click()
            send_to_voice("Dislike dado no vídeo.")

        except NoSuchElementException:
            send_to_voice("Não foi possível encontrar o botão de dislike.")

        except ElementClickInterceptedException:
            send_to_voice("O botão de descurtir não pôde ser clicado.")

    def like_video(self, send_to_voice):
        """
        The method like_video is responsible for liking a video on YouTube.
        The method also sends a message to the user to inform the action.

        Args:
            - send_to_voice: a function that sends a message to the user.
            
        """
        try :

            video_liked = self.driver.find_element(By.XPATH, "Unlike" or '@title= "Anular \"gosto\""')

            if video_liked:
                send_to_voice("Já deu like neste vídeo.")
                return
                                                                                          
        except NoSuchElementException:
            try:
                # Locate the like button using XPath
                like_button = self.driver.find_element(By.XPATH, "//button[@title='I like this' or @title='Gosto disto']")

                if "aria-pressed" in like_button.get_attribute("outerHTML"):
                    if like_button.get_attribute("aria-pressed") == "true":
                        send_to_voice("O vídeo já foi curtido.")
                        return
                ActionChains(self.driver).move_to_element(like_button).perform()
                like_button.click()
                send_to_voice("Like dado no vídeo.")
            except NoSuchElementException:
                send_to_voice("Não foi possível encontrar o botão de like.")
            except ElementClickInterceptedException:
                send_to_voice("O botão de like não pôde ser clicado.")

    def slide_page(self, slide_up,entity):
        """
        The slide_page method is responsible for sliding the page up or down based on the user's message.

        Args:
            - slide_up: a boolean that represents if the page should be slided up or down.
            - entity: a string that represents the entity of the user's message.
        """

        print(f"Slide Page")

        DEFAULT_SCROLL_VALUE = 400

        small_scroll = ["pouco", "um pouco", "uma beca", "pedaço", "um pedaço", "um bocado", "um pouquinho"]

        medium_scroll = ["mais", "mais um pouco", "mais um pedaço", "mais um bocado", "mais um pouquinho", "mais um pouco", "mais um bocado"]

        scroll_value = DEFAULT_SCROLL_VALUE

        if entity is not None:
            if entity in small_scroll:
                SMALL_SCROLL_VALUE = 200
                scroll_value = SMALL_SCROLL_VALUE
            elif entity in medium_scroll:
                MEDIUM_SCROLL_VALUE = 600
                scroll_value = MEDIUM_SCROLL_VALUE
            else: 
                self.send_to_voice("Erro a dar scroll na página")
                return

        message = ""

        if slide_up:
            scroll_value = -scroll_value
            message = "Scroll para cima efetuado com sucesso."
        else:    
            message = "Scroll para baixo efetuado com sucesso."


        print(f"Scroll Value: {scroll_value}")
    
        self.driver.execute_script(f"window.scrollBy(0, {scroll_value});")
    
        self.send_to_voice(message)
               
    def fusion_action(self,recognized_message, nlu):
        """
        The fusion_action method is responsible for executing the action based on the user's command.
        The method will check if the command is a gesture or a speech command, and call the right method to execute the action.
        """
        print(f"Recognized Message: {recognized_message}")

        match recognized_message[0]:
            case "FULLS" | "NORMALS":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para alterar o modo de ecrã")
                    return

                change_to_fullscreen = True if recognized_message[0] == "FULLS" else False

                self.video.handle_fullscreen(self.send_to_voice, change_to_fullscreen)
        
            case "SLIDED" | "SLIDEUP":
                slide_up = True if recognized_message[0] == "SLIDEUP" else False

                entity = nlu["entity"] if "entity" in nlu else None

                print("boas")
                print("Entity:", entity)
                print("Slide Up:", slide_up)

                self.slide_page(slide_up,entity)

            case "VOLUMED" | "VOLUMEU":
                if self.video is None:
                    self.send_to_voice("Não há nenhum vídeo para alterar o volume")
                    return
                
                increase_voulme = True if recognized_message[0] == "VOLUMEU" else False

                entity = nlu["entity"] if "entity" in nlu else None

                self.video.handle_volume(self.send_to_voice, entity, increase_voulme)

            case _:
                self.send_to_voice("Desculpe, não entendi o que voocê queria")
    