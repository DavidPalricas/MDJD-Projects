from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from consts import OUTPUT
from web_app_conextions_files.index_connections import Confirmation
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time


class Video:
    """
    The class Video is responsible for handling events related to a video on YouTube.
    The class has the following attributes:
    - is_short: a boolean that indicates if the video is short or not.
    - speed: a float that represents the speed of the video.
    - driver: an instance of the WebDriver class.
    - youtube: an instance of the WebElement class(body) that represents the YouTube page.
    - is_fullscreen: a boolean that indicates if the video is in fullscreen mode or not.
    """
    def __init__(self,is_short,driver, speed = None):
        """
         Initializes a new instance of the Video class.

         Args:
            - is_short: a boolean that indicates if the video is short or not.
            - driver: a google chrome driver.
        """
        self.confirmation = Confirmation(FusionAdd=f"https://{OUTPUT}/IM/USER1/SPEECH_ANSWER")
        self.is_short = is_short
     
        self.speed =  1 if speed is None else speed
        self.driver = driver
        self.youtube =self.driver.find_element("tag name", "body")

        self.is_fullscreen = False

    def get_video_time(self):
        """
        Retrieves the current time and total duration of the YouTube video.
        
        Returns:
            tuple: A tuple containing the current time and total duration as strings.
        """
        try:
            #print("ggllglgllglgllglglgllglg")
            #print(f"driver: {self.driver}")
            #print(f"driver url: {self.driver.current_url}")
            #print(f"drive body: {self.driver.find_element('tag name', 'body')}")
            self.youtube =self.driver.find_element("tag name", "body")

            # Pause video first
            if not self.verify_video_playing(self.driver, self.is_short):
                self.youtube.send_keys('k')

            #print(f"youtube: {self.youtube}")

            # Locate the elements containing the current and total time
            current_time_element = self.driver.find_element(By.CLASS_NAME, 'ytp-time-current')
            total_time_element = self.driver.find_element(By.CLASS_NAME, 'ytp-time-duration')
            #print(f"current_time_element: {current_time_element}, total_time_element: {total_time_element}")

            # Extract the text (time) from the elements
            current_time = current_time_element.text
            total_time = total_time_element.text
            #print(f"current_time: {current_time}, total_time: {total_time}")

            # Play video again
            self.youtube.send_keys('k')
            # Print or return the time values
            return current_time, total_time
        
        except Exception as e:
            print(f"Error while retrieving video times: {e}")
            return None, None

    def verify_video_playing(self,driver,is_short):
        """
        Verifies if the video is playing or not.

        Returns:
            bool: A boolean that indicates if the video is playing or not.
        """
        try:
            video_element = '//*[@id="movie_player"]/div[10]/div[2]' if not is_short else '//*[@id="shorts-player"]/div[8]/div[2]'
            
            # if is_short:
            #     try:
            #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="play-pause-button-shape"]/button/div/yt-icon/span/div/svg/path')))
            #         return True
            #     except Exception as e:
            #         return False

            video = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, video_element)))
            
            #print(f"Video -----------: {video.get_attribute('aria-label')}")
            return video.get_attribute('aria-label') == "Pause" or video.get_attribute('aria-label') == "Pausa"
        except Exception as e:
            print(f"Error while verifying video playing: {e}")
            return False

    def handling_play_pause(self,send_to_voice,intent):      
        """
            The method handling_play_pause is responsible for handling the player or pause of a youtube event.
            If the intent is play_video and the video is already playing, the assistant will say that the video is already playing, if is not playing, the assistant will call the play_pause method to play the video.
            If the intent is play_video and the video is already playing, the assistant will say that the video is not playing, if is playing, the assistant will call the play_pause method to pause the video.

            Args:
               - send_to_voice: a function that sends a message to the user.
               - intent: a string that represents the intent's name of the user.
        """
    
        if not self.verify_video_playing(self.driver,self.is_short) :
            if intent == "play_video":
                send_to_voice("O vídeo já está sendo reproduzido")
            else:
                self.play_pause(send_to_voice,False)
        else:
            if intent == "pause_video":
                send_to_voice("O vídeo já está pausado")
            else:
                self.play_pause(send_to_voice,intent)

    def play_pause(self,send_to_voice,play):
        """
            The method play_pause is responsible for playing or pausing a video on YouTube and updates the status of the video.
            The method also sends a message to the user to inform is  action.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - play: a boolean that indicates if it is to play the video or not.
        """                 
        if play:
            send_to_voice("Reproduzindo o vídeo")

        else:
            send_to_voice("Pausando o vídeo")
        
        self.youtube.send_keys('k')


    def change_speed(self,send_to_voice,nlu):
        """
            The method change_speed is responsible for changing the speed of a video on YouTube.
            If the video is not playing, the assistant will inform the user that the video is paused and it is not possible to change the speed.
            If the intent is increase_speed_default, the assistant will call the increase_speed method to increase the speed of the video.
            If the intent is decrease_speed_default, the assistant will call the decrease_speed method to decrease the speed of the video.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - intent: a string that represents the intent's name of the user.
            """
        
        if self.verify_video_playing(self.driver,self.is_short):
            send_to_voice("O vídeo está pausado, não é possível alterar a velocidade")
            return
         
        key_combination = ActionChains(self.driver)

        if nlu["intent"] == "increase_speed":
            if "entity"  not in nlu:
                self.increase_speed(send_to_voice,key_combination)
            else:
                self.increase_speed(send_to_voice,key_combination,nlu["entity"])

        elif nlu["intent"] == "decrease_speed":
            if "entity"  not in nlu:
                self.decrease_speed(send_to_voice,key_combination)
            else:
                self.decrease_speed(send_to_voice,key_combination,nlu["entity"])

        else: 
             self.alter_speed(send_to_voice,key_combination,nlu["entity"])

    def increase_speed(self,send_to_voice,key_combination,speed=None):
        """
            The method increase_speed is responsible for increasing the speed of a video on YouTube.
            If the speed is already at the maximum, the assistant will inform the user that the speed is already at the maximum.
            The method increases the speed by the speed passed as an argument or by 0.25x and sends a message to the user informing the current speed.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - key_combination: an instance of the ActionChains class which represents the keys pressed by the user.
                - speed: a float that represents the speed of the video, if it is not passed, the speed will be 0.25 (default value).
            """
        if self.speed == 2:
            send_to_voice("Não é possível aumentar a velocidade, pois já está no máximo")
            return
        
        speed = 0.25 if speed is None else float(speed.replace(",",".") if "," in speed else speed)

        self.speed += speed

        if self.speed > 2:
            self.speed = 2
            
        send_to_voice(f"Aumentando a velocidade em {speed}x, a velocidade atual é de {self.speed}")
        
        # Increase the speed by pressing the '.' key
        for _ in range(int(speed/0.25)):
            key_combination.key_down(Keys.SHIFT).send_keys('.').key_up(Keys.SHIFT).perform()

        if self.speed == 2:
            send_to_voice("A velocidade já está no máximo")

  
    def decrease_speed(self,send_to_voice,key_combination,speed=None):
        """
            The method decrease_speed is responsible for decreasing the speed of a video on YouTube.
            If the speed is already at the minimum, the assistant will inform the user that the speed is already at the minimum.
            The method decreases the speed by the speed passed as an argument or by 0.25x and sends a message to the user informing the current speed.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - key_combination: an instance of the ActionChains class which represents the keys pressed by the user.
                - speed: a float that represents the speed of the video, if it is not passed, the speed will be 0.25 (default value).         
        """

        if self.speed == 0.25:
            send_to_voice("Não é possível diminuir a velocidade, pois já está no mínimo")
            return 
        
        speed = 0.25 if speed is None else float(speed.replace(",",".") if "," in speed else speed)

        self.speed -= speed

        if self.speed < 0.25:
            self.speed = 0.25

        send_to_voice(f"Diminuindo a velocidade em {speed}x, a velocidade atual é de {self.speed}")
        
        # Decrease the speed by pressing the ',' key
        for _ in range(int(speed/0.25)):
            key_combination.key_down(Keys.SHIFT).send_keys(',').key_up(Keys.SHIFT).perform()

        if self.speed == 0.25:
            send_to_voice("A velocidade já está no mínimo")

    def alter_speed(self,send_to_voice,key_combination,speed):
        """
            The method alter_speed is responsible for changing the speed of a video on YouTube.
            If the speed is already at the value passed as an argument, the assistant will inform the user that the speed is already at the value passed.
            If the speed is greater than the value passed as an argument, the assistant will call the decrease_speed method to decrease the speed of the video.
            If the speed is less than the value passed as an argument, the assistant will call the increase_speed method to increase the speed of the video.
            
            Args:
                - send_to_voice: a function that sends a message to the user.
                - key_combination: an instance of the ActionChains class which represents the keys pressed by the user.
                - speed: a float that represents the speed of the video.
        """

        speed = float(speed.replace(",",".") if "," in speed else speed)

        if self.speed < speed:
            speed = speed - self.speed       
            self.increase_speed(send_to_voice,key_combination,str(speed))
        elif self.speed > speed:
            speed = self.speed - speed
            self.decrease_speed(send_to_voice,key_combination,str(speed))  
        else:
            send_to_voice(f"A velocidade já está em {speed}x")

    def on_off_video_subtitles(self,send_to_voice,intent):
        """
            The method on_off_video_subtitles is responsible for turning on or off the subtitles of a video on YouTube.
            If the intent is turn_on_subtitles, the assistant will call the turn_on_subtitles method to turn on the subtitles.
            If the intent is turn_off_subtitles, the assistant will call the turn_off_subtitles method to turn off the subtitles.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - intent: a string that represents the intent's name of the user.
        """
        if self.verify_subtitles(self.driver):
            if intent == "activate_video_subtitles":
                send_to_voice("As legendas já estão ativadas")
            else:
                self.turn_on_off_subtitles(send_to_voice,False)
        else:
            if intent == "deactivate_video_subtitles":
                send_to_voice("As legendas já estão desativadas")
            else:
                self.turn_on_off_subtitles(send_to_voice,True)

    def verify_subtitles(self,driver):
        """
            The method verify_subtitles is responsible for verifying if the subtitles are on or off.

            Returns:
                - bool: a boolean that indicates if the subtitles are on or off.
        """
        try:
            # Locate the element containing the subtitles
            subtitles_element = driver.find_element(By.XPATH, "//button[contains(@class, 'ytp-subtitles-button')]")

            return subtitles_element.get_attribute("aria-pressed") == "true"
        except Exception as e:
            print(f"Error while verifying subtitles: {e}")
            return False

    def turn_on_off_subtitles(self,send_to_voice,turn_on):
        """
            The method turn_on_off_subtitles is responsible for turning on or off the subtitles of a video on YouTube.
            The method also sends a message to the user to inform the action.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - turn_on: a boolean that indicates if it is to turn on the subtitles or not.
        """
        if turn_on:
            send_to_voice("Ativando as legendas")
        else:
            send_to_voice("Desativando as legendas")

        self.youtube.send_keys('c')

    def mute_unmute_video(self,send_to_voice,intent):
        """
            The method mute_unmute_video is responsible for muting or unmuting a video on YouTube.
            If the intent is mute_video, the assistant will call the mute_unmute method to mute the video.
            If the intent is unmute_video, the assistant will call the mute_unmute method to unmute the video.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - intent: a string that represents the intent's name of the user.
        """
        volume_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'ytp-mute-button')]")
                
        title = volume_button.get_attribute("title")

        if title == "Unmute (m)" or title == "Reativar som (m)":
            if intent == "mute_video":
                send_to_voice("O vídeo já está mudo")
            else:
                self.mute_unmute(send_to_voice,False)
        else:
            if intent == "unmute_video":
                send_to_voice("O vídeo já está com o som ativado")
            else:
                self.mute_unmute(send_to_voice,True)

    def mute_unmute(self,send_to_voice,mute):
        """
            The method mute_unmute is responsible for muting or unmuting a video on YouTube.
            The method also sends a message to the user to inform the action.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - mute: a boolean that indicates if it is to mute the video or not.
        """
        
        if mute:
            send_to_voice("Desativando o som do vídeo")
        else:
            send_to_voice("Ativando o som do vídeo")

        self.youtube.send_keys('m')

    def seek_forward_backward(self,send_to_voice,intent,entities):
        """
            The method seek_forward_backward is responsible for seeking forward or backward a video on YouTube.
            If the intent is seek_forward, the assistant will call the seek method to seek forward the video.
            If the intent is seek_backward, the assistant will call the seek method to seek backward the video.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - intent: a string that represents the intent's name of the user.
                - entities: a dictionary that contains the entities found in the user's message.
        """
        if intent == "seek_forward_video":
            return self.seek(send_to_voice,entities,True)
        else:
            return self.seek(send_to_voice,entities,False)

    def seek(self,send_to_voice,entities,forward):
        """
            The method seek is responsible for seeking forward or backward a video on YouTube.
            The method also sends a message to the user to inform the action.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - entities: a dictionary that contains the entities found in the user's message.
                - forward: a boolean that indicates if it is to seek forward or backward the video.
        """
        time, current_seconds = self.convert_time(entities,forward,send_to_voice)

        if forward:
            send_to_voice(f"Avançando {entities}")
        else:
            send_to_voice(f"Retrocedendo {entities}")

        
        if time <= 90:
            #print(f"Time2: {time}")
            for _ in range(round(abs(time-current_seconds)/10)):
                self.youtube.send_keys('l' if forward else 'j')
        else: 
            # if current_url has the time parameter, it will be updated, otherwise it will be added
            if "t=" in self.driver.current_url:
                return f"{self.driver.current_url.split('&t=')[0]}&t={time}s"
            else:
                self.driver.get(self.driver.current_url + f"&t={time}")
            
        return None

    def convert_time(self, entities, forward,send_to_voice):
        """
            The method convert_time is responsible for converting the time to seconds.

            Args:
                - entities: a string that represents the time.
                - forward: a boolean that indicates if it is to seek forward or backward the video.

            Returns:
                - int: the time converted to seconds.
        """

        time_units = ["segundos", "minutos", "horas"]

        
        try:
            type_time = entities.split(" ")[1]
            time_choosen = int(entities.split(" ")[0])
        except:
            send_to_voice("Erro ao avançar ou retroceder o vídeo")
            return 0, 0
        
        current_time, total_time = self.get_video_time()
        
        #print(f"current_time: {current_time}, total_time: {total_time}")
        current_time = current_time.split(":")
        total_time = total_time.split(":")

        current_seconds = (int(current_time[0]) * 3600 + int(current_time[1]) * 60 + int(current_time[2])) if len(current_time) == 3 else (int(current_time[0]) * 60 + int(current_time[1]))
        total_seconds = (int(total_time[0]) * 3600 + int(total_time[1]) * 60 + int(total_time[2])) if len(total_time) == 3 else (int(total_time[0]) * 60 + int(total_time[1]))

        for i in range(len(time_units)):
            if type_time == time_units[i] or type_time == time_units[i][:-1]:
                time_in_seconds = time_choosen * 60 ** i

                if forward:
                    new_time = current_seconds + time_in_seconds

                    if new_time >= total_seconds:
                        time.sleep(2)
                        send_to_voice("O vídeo chegou ao fim")
                        
                    return min(new_time, total_seconds-1), current_seconds
                else:
                    new_time = current_seconds - time_in_seconds
                    return max(new_time, 0), current_seconds

        #print(f"Time: {time}")
        return time_choosen, current_seconds

    def share_video(self,send_to_voice,entities,items_to_be_searched):
        """
            The method share_video is responsible for sharing a video on YouTube.
            The method also sends a message to the user to inform the action.

            Args:
                - send_to_voice: a function that sends a message to the user.
                - entities: a string that represents the entities found in the user's message.
        """
        send_to_voice(f"Compartilhando o vídeo com {entities}")
        youtube_link = self.driver.current_url
        contact_name = entities
        return self.send_whatsapp_message(self.driver, contact_name, youtube_link,send_to_voice,items_to_be_searched)
    
    def send_whatsapp_message(self, driver, contact_name, message_link,send_to_voice,items_to_be_searched):
        """
            The method send_whatsapp_message is responsible for sending a message to a contact on WhatsApp.
            The method also sends a message to the user to inform the action.

            Args:
                - driver: an instance of the WebDriver class.
                - contact_name: a string that represents the name of the contact.
                - message: a string that represents the message to be sent.
        """
        # Open a new tab and navigate to WhatsApp Web
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])  # Change the focus to the new tab
        driver.get("https://web.whatsapp.com/")
        
        time.sleep(2)
         
        send_to_voice("Por favor, aguarde um pouco")

        # Wait for the user to scan the QR code
        #time.sleep(13)

        # Search for the contact and send the message
        inp_xpath_search = '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div'

        input_box_search = WebDriverWait(driver,50).until(EC.presence_of_element_located((By.XPATH, inp_xpath_search)))
        input_box_search.click()
        #print(f"contact_name: {contact_name}")
        input_box_search.send_keys(contact_name)
        time.sleep(2)

        # Verify if the contact is found
        if self.verify_contact(driver):
            
            # Find the search results
            contact_spans_xpath = '//span[@dir="auto" and @title and @class="x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1rg5ohu _ao3e"]'

            # Find all matching span elements (e.g., top 3 contacts)
            contact_spans = driver.find_elements(By.XPATH, contact_spans_xpath)

            # reverse the list to display the most recent contacts first
            contact_spans.reverse()
            # Collect the names of the top three results
            for result in contact_spans[:3]:  # Limit to top 3 results
                try:
                    contact_title = result.get_attribute("title") 
                    items_to_be_searched.append(result)
                except Exception as e:
                    print(f"Error extracting contact name: {e}")

            # Display the options to the user
            message = "Contactos encontrados: "

            for i, name in enumerate(contact_spans[:3]):
                message += f"{i + 1}. {name.get_attribute('title')}, "
            
            #print(f"message")
            send_to_voice(message)

            time.sleep(10)
            
            send_to_voice("Escolha um dos contactos para enviar a mensagem, ou seja, primeiro, segundo ou terceiro")

            time.sleep(2)

            self.confirmation.confirm()
            return True, message_link
        else:
            send_to_voice("Contacto não encontrado")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return False, ""

    def verify_contact(self, driver):
        """
            The method verify_contact is responsible for verifying if a contact is found on WhatsApp.

            Args:
                - driver: an instance of the WebDriver class.

            Returns:
                - bool: a boolean that indicates if the contact is found.
        """
        try:
            # If the contact is not found
            contanct_not_found = '//*[@id="pane-side"]/div/div/span'
            contact = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, contanct_not_found)))
            #print(f"contact displayed: {contact.is_displayed()}")
            return not contact.is_displayed()
        except Exception as e:
            return True
        
    def handle_fullscreen(self, send_to_voice, change_to_fullscreen):
        """
        Handles the video fullscreen mode.
        
        Args:
            - send_to_voice: a function that sends a message to the user.
            - change_to_fullscreen: a boolean that indicates if the video should be in fullscreen mode or not.
        """      
        if self.is_short:
            send_to_voice("Alterar o modo de ecrã não é possível em shorts.")
            return
        
        if self.is_fullscreen and change_to_fullscreen:
            send_to_voice("O vídeo já está em ecrã cheio.")
            return
        
        if not self.is_fullscreen and not change_to_fullscreen:
            send_to_voice("O vídeo já está em ecrã normal.")
            return
        
        self.youtube.send_keys('f')
        self.is_fullscreen = not self.is_fullscreen
        
    def handle_volume(self,send_to_voice, entity, increase_volume):
        """
        Handles the video volume.

        Args:
            - send_to_voice: a function that sends a message to the user.
            - entity: a string that represents the entity of the user's message.
            - increase_volume: a boolean that represents if the volume should be increased or decreased.
        """
        
        current_volume = None
        player = None

        MIN_VOLUME = 0.05
        MAX_VOLUME = 1

        try: 
            current_volume =self.driver.execute_script("""
                const video = document.querySelector('video');
                return video ? video.volume : null;
            """)

            player = self.driver.find_element(By.ID, 'movie_player')

        except NoSuchElementException:
            send_to_voice("Erro ao obter o volume do vídeo.")
            return
        
        if current_volume == 0:
            send_to_voice("O vídeo está sem som, por favor ative o som.")
            return
        
        volume_to_change = None

        little_volume = ["pouco", "um pouco", "uma beca", "pedaço", "um pedaço", "um bocado", "um pouquinho"]

        medium_volume = ["bocado","mais", "mais um pouco", "mais um pedaço", "mais um bocado", "mais um pouquinho", "mais um pouco", "mais um bocado"]
        
        if entity is None:
            DEFAULT_VOLUME_VALUE = 0.15
            volume_to_change = DEFAULT_VOLUME_VALUE
        else:
            if  entity in little_volume:
                    LOW_VOLUME_VALUE = 0.10
                    volume_to_change = LOW_VOLUME_VALUE

            elif entity in medium_volume:
                    MEDIUM_VOLUME_VALUE = 0.25
                    volume_to_change = MEDIUM_VOLUME_VALUE

            elif  entity == "mínimo" and not increase_volume:                
                    volume_to_change = MIN_VOLUME

            elif entity == "máximo" and increase_volume:          
                    volume_to_change = MAX_VOLUME

            elif entity == "máximo" and not increase_volume or entity == "mínimo" and increase_volume:       
                    send_to_voice("Não percebi o que queria fazer.")
                    return  
            

        if volume_to_change is None:
            send_to_voice("Não percebi o que queria.")
            return

        key_to_send = Keys.ARROW_UP if increase_volume else Keys.ARROW_DOWN

        player.send_keys(Keys.SPACE) 

        ARROW_VOLUME_VALUE = 0.05

        steps = 0

        if volume_to_change == MIN_VOLUME:
            # To ensure that we have the maximum setps to reach the minimum volume
            volume_to_change = MAX_VOLUME + 0.05 if current_volume * 100 % 5 != 0 else MAX_VOLUME
            steps = int(volume_to_change/ ARROW_VOLUME_VALUE)
        else:
            volume_to_change = volume_to_change + 0.05 if current_volume * 100 % 5 != 0 else volume_to_change

            steps = int(abs(volume_to_change) / ARROW_VOLUME_VALUE)

        message = "Volume aumentado." if increase_volume else "Volume diminuído."
        
  
        print(f"Currrent Volume: {current_volume} && Entity: {entity} && Steps: {steps}")

        for _ in range(steps):
            if round(current_volume, 2) >= MAX_VOLUME and increase_volume:
                send_to_voice("O volume já está no máximo.")
                player.send_keys(Keys.SPACE)
                return
            elif round(current_volume, 2) <= MIN_VOLUME and not increase_volume:
                send_to_voice("O volume já está no mínimo.")
                player.send_keys(Keys.SPACE)
                return
    
            player.send_keys(key_to_send)

            current_volume  = current_volume + ARROW_VOLUME_VALUE if increase_volume else current_volume - ARROW_VOLUME_VALUE
            
            time.sleep(0.2)

            print(f"Currrent Volume: {current_volume}")

        send_to_voice(message)

        player.send_keys(Keys.SPACE)
        