from pygame import mixer
import os

class SoundPlayer:   
    """The SoundPlayer class is responsible for playing sounds in the game. It uses the Flyweight pattern to store shared instances of sounds.

         The class has the following attributes:
            - sounds: The list of sounds to be played
            - is_music: A flag indicating whether the sound is music or a sound effect
            - _sounds: A dictionary that stores the shared instances of sounds (Flyweight storage)
    """
    _sounds = {}

    def __init__(self, sounds, is_music):
        """ 
            Initializes a new instance of the SoundPlayer class, and initializes the mixer module (pygame.mixer) which is responsible for playing sounds.
            
            Args:
                - sounds (list): The list of sounds to be played
                - is_music (bool): A flag indicating whether the sound is music or a sound effect
        """
        mixer.init()
        self.is_music = is_music
        self.sounds = sounds

    def get_sound(self, sound_name):
        """    
            The get_sound method is responsible for returning a shared instance of a sound or creating a new one if it does not exist.
            These shared instances are stored in a dictionary with the sound name and a flag indicating whether the sound is music or a sound effect.
        
            Args:
                - sound_name (str): The name of the sound file
        """
        sound_key = (sound_name, self.is_music)
        
        if sound_key not in self._sounds:
            sound_base_path = os.path.join(os.path.dirname(__file__), "../Assets/SoundTrack/")
            sound_path = os.path.join(sound_base_path, f"{'Music' if self.is_music else 'SoundEffects'}/{sound_name}.wav")

            self._sounds[sound_key] = mixer.Sound(sound_path)
        
        return self._sounds[sound_key]

    def play(self, sound_name):
        """ The play method is responsible for playing the sound, setting the volume, and looping the sound if it is music.
            The sound is obtained from the Flyweight Factory.

            Args:
              - sound_name (str): The name of the sound file to be played
        """
        sound = self.get_sound(sound_name)

        # Set volume to 10%
        sound.set_volume(0.1)  
        
        loop = -1 if self.is_music else 0
        sound.play(loop)

    def stop(self):
        """ The stop method is responsible for stopping music playback.
            If the current sound is a sound effect an exception is raised.
        """
        if not self.is_music:
            raise Exception("SoundEffects cannot be stopped")
        
        mixer.stop()
