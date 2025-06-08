/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import java.io.IOException;
import scxmlgen.Fusion.FusionGenerator;
//import FusionGenerator;

import Modalities.Output;
import Modalities.Speech;
import Modalities.Touch;

/**
 *
 * @author nunof
 */
public class GenFusionSCXML {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws IOException {

    FusionGenerator fg = new FusionGenerator();
  
    fg.Redundancy(Touch.FULLSCREEN, Speech.FULLSCREEN, Output.FULLSCREEN);
    fg.Redundancy(Touch.NORMALSCREEN, Speech.NORMALSCREEN, Output.NORMALSCREEN);
  
    
    fg.Complementary(Touch.VOLUMEUP, Speech.VOLUMEUP, Output.VOLUMEUP);
    fg.Complementary(Touch.VOLUMEDOWN, Speech.VOLUMEDOWN, Output.VOLUMEDOWN);
    fg.Complementary(Touch.SLIDEDOWN, Speech.SLIDEDOWN, Output.SLIDEDOWN);
    fg.Complementary(Touch.SLIDEUP, Speech.SLIDEUP, Output.SLIDEUP);


    fg.Build("fusion_novo.scxml");

  /*  
    fg.Sequence(Speech.SQUARE, SecondMod.RED, Output.SQUARE_RED);
    fg.Sequence(Speech.SQUARE, SecondMod.BLUE, Output.SQUARE_BLUE);
    fg.Sequence(Speech.SQUARE, SecondMod.YELLOW, Output.SQUARE_YELLOW);
    fg.Sequence(Speech.TRIANGLE, SecondMod.RED, Output.TRIANGLE_RED);
    fg.Sequence(Speech.TRIANGLE, SecondMod.BLUE, Output.TRIANGLE_BLUE);
    fg.Sequence(Speech.TRIANGLE, SecondMod.YELLOW, Output.TRIANGLE_YELLOW);
    fg.Redundancy(Speech.CIRCLE, SecondMod.RED, Output.CIRCLE_RED);
    fg.Redundancy(Speech.CIRCLE, SecondMod.BLUE, Output.CIRCLE_BLUE);
    fg.Redundancy(Speech.CIRCLE, SecondMod.YELLOW, Output.CIRCLE_YELLOW);
    
    fg.Single(Speech.CIRCLE, Output.CIRCLE);
    
    
    fg.Redundancy(Speech.OPEN_SOCIAL, SecondMod.RED, Output.OPEN_SOCIAL);
    fg.Single(Speech.OPEN_SOCIAL, Output.OPEN_SOCIAL);
   
  
    fg.Redundancy(Speech.OPEN_SOCIAL, SecondMod.SOCIAL, Output.OPEN_SOCIAL);
  
    fg.Redundancy(Speech.OPEN_LIXO, SecondMod.LIXO, Output.OPEN_LIXO);
    fg.Single(Speech.OPEN_LIXO, Output.OPEN_LIXO);
    
    
    fg.Build("fusion.scxml");
       
  

    fg.Complementary(Speech.LIGHT_ON, Touch.LOCATION_LIVINGROOM, Output.LIGHT_LIVINGROOM_ON);
    fg.Complementary(Speech.LIGHT_ON, Touch.LOCATION_ROOM, Output.LIGHT_ROOM_ON);
    fg.Complementary(Speech.LIGHT_ON, Touch.LOCATION_KITCHEN, Output.LIGHT_KITCHEN_ON);
    fg.Complementary(Speech.LIGHT_OFF, Touch.LOCATION_LIVINGROOM, Output.LIGHT_LIVINGROOM_OFF);
    fg.Complementary(Speech.LIGHT_OFF, Touch.LOCATION_ROOM, Output.LIGHT_ROOM_OFF);
    fg.Complementary(Speech.LIGHT_OFF, Touch.LOCATION_KITCHEN, Output.LIGHT_KITCHEN_OFF);  
    
    fg.Complementary(Touch.LOCATION_LIVINGROOM, Speech.LIGHT_ON, Output.LIGHT_LIVINGROOM_ON);
    fg.Complementary(Touch.LOCATION_ROOM, Speech.LIGHT_ON, Output.LIGHT_ROOM_ON);
    fg.Complementary(Touch.LOCATION_KITCHEN, Speech.LIGHT_ON, Output.LIGHT_KITCHEN_ON);
    fg.Complementary(Touch.LOCATION_LIVINGROOM, Speech.LIGHT_OFF, Output.LIGHT_LIVINGROOM_OFF);
    fg.Complementary(Touch.LOCATION_ROOM, Speech.LIGHT_OFF, Output.LIGHT_ROOM_OFF);
    fg.Complementary(Touch.LOCATION_KITCHEN, Speech.LIGHT_OFF, Output.LIGHT_KITCHEN_OFF);  
    
    //
    fg.Complementary(Speech.TEMPERATURE_UP, Touch.LOCATION_LIVINGROOM, Output.TEMP_LIVINGROOM_UP);
    fg.Complementary(Speech.TEMPERATURE_UP, Touch.LOCATION_ROOM, Output.TEMP_ROOM_UP);
    fg.Complementary(Speech.TEMPERATURE_UP, Touch.LOCATION_KITCHEN, Output.TEMP_KITCHEN_UP);
    fg.Complementary(Speech.TEMPERATURE_DOWN, Touch.LOCATION_LIVINGROOM, Output.TEMP_LIVINGROOM_DOWN);
    fg.Complementary(Speech.TEMPERATURE_DOWN, Touch.LOCATION_ROOM, Output.TEMP_ROOM_DOWN);
    fg.Complementary(Speech.TEMPERATURE_DOWN, Touch.LOCATION_KITCHEN, Output.TEMP_KITCHEN_DOWN);  
    
    fg.Complementary(Touch.LOCATION_LIVINGROOM, Speech.TEMPERATURE_UP, Output.TEMP_LIVINGROOM_UP);
    fg.Complementary(Touch.LOCATION_ROOM, Speech.TEMPERATURE_UP, Output.TEMP_ROOM_UP);
    fg.Complementary(Touch.LOCATION_KITCHEN, Speech.TEMPERATURE_UP, Output.TEMP_KITCHEN_UP);
    fg.Complementary(Touch.LOCATION_LIVINGROOM, Speech.TEMPERATURE_DOWN, Output.TEMP_LIVINGROOM_DOWN);
    fg.Complementary(Touch.LOCATION_ROOM, Speech.TEMPERATURE_DOWN, Output.TEMP_ROOM_DOWN);
    fg.Complementary(Touch.LOCATION_KITCHEN, Speech.TEMPERATURE_DOWN, Output.TEMP_KITCHEN_DOWN); 
    

    fg.Single(Speech.LIGHT_ON, Output.LIGHT_ON);
    fg.Single(Speech.LIGHT_OFF, Output.LIGHT_OFF);
    fg.Single(Touch.LOCATION_LIVINGROOM, Output.LOCATION_LIVINGROOM);
    fg.Single(Touch.LOCATION_ROOM, Output.LOCATION_ROOM);
    fg.Single(Touch.LOCATION_KITCHEN, Output.LOCATION_KITCHEN);
    
    fg.Single(Speech.TEMPERATURE_UP, Output.TEMP_UP);
    fg.Single(Speech.TEMPERATURE_DOWN, Output.TEMP_DOWN);
    */
    
    
   //fg.Complementary(Touch.OPEN_NEWS_TITLE, Speech.ACTION_NEWS_NIMAGE, Output.OPEN_NEWS_AS_IMAGE);
   // fg.Complementary(Speech.ACTION_NEWS_NTEXT,Touch.OPEN_NEWS_TITLE, Output.OPEN_NEWS_AS_TEXT);
   // fg.Complementary(Speech.ACTION_NEWS_NIMAGE,Touch.OPEN_NEWS_TITLE, Output.OPEN_NEWS_AS_IMAGE);
   // fg.Single(Touch.OPEN_NEWS_TITLE, Output.OPEN_NEWS_AS_TEXT);
    
   // fg.Redundancy(Touch.GO_BACK, Speech.ACTION_GENERICENTITY_BACK, Output.GO_BACK);
    
        
    }
    
}
