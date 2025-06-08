package Modalities;

import scxmlgen.interfaces.IOutput;

public enum Output implements IOutput{
    
    // Redundant
    DISLIKE("[FUSION][DISLIKE]"),
    LIKE("[FUSION][LIKE]"),
    FULLSCREEN("[FUSION][FULLS]"),
    NORMALSCREEN("[FUSION][NORMALS]"),
    SLIDEDOWN("[FUSION][SLIDED]"),
    SLIDEUP("[FUSION][SLIDEUP]"),
    VOLUMEUP("[FUSION][VOLUMEU]"),
    VOLUMEDOWN("[FUSION][VOLUMED]"),

    // Complementary
    // HELP_ACTION("[FUSION][HELP]"),
    // HELP_OPERACOES_ACTION("[FUSION][HELP][OPERACOES]"),
    // HELP_GESTOS_ACTION("[FUSION][HELP][GESTOS]"),
    // HELP_TODAS_ACTION("[FUSION][HELP][TODAS]"),


    ;
    
    
    
    private String event;

    Output(String m) {
        event=m;
    }
    
    public String getEvent(){
        return this.toString();
    }

    public String getEventName(){
        return event;
    }
}
