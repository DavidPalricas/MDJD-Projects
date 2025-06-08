/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Modalities;

import scxmlgen.interfaces.IModality;

/**
 *
 * @author nunof
 */
public enum Touch implements IModality{
    
    DISLIKE("[GESTURES][DISLIKE]", 5000),
	LIKE("[GESTURES][LIKE]", 5000),
	FULLSCREEN("[GESTURES][FULLS]",3000),
	NORMALSCREEN("[GESTURES][NORMALS]",3000),
	SLIDEDOWN("[GESTURES][SLIDED]",7000),
	SLIDEUP("[GESTURES][SLIDEUP]",7000),
	VOLUMEUP("[GESTURES][VOLUMEU]",5000),
	VOLUMEDOWN("[GESTURES][VOLUMED]",5000),

    // HELP("[GESTURES][HELP]",0),

    ;
    
    private String event;
    private int timeout;


    Touch(String m, int time) {
        event=m;
        timeout=time;
    }

    @Override
    public int getTimeOut() {
        return timeout;
    }

    @Override
    public String getEventName() {
        //return getModalityName()+"."+event;
        return event;
    }

    @Override
    public String getEvName() {
        return getModalityName().toLowerCase()+event.toLowerCase();
    }
    
}