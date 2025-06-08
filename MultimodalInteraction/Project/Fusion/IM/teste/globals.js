//var host = '192.168.0.200';
var host = 'localhost';

var mmi_im = "https://"+host+":8000/IM/USER1/";
var mmi_fusion = "https://"+host+":9876/IM/USER1/";


//var speech_service ="wss://"+host+":8888/Speech";
var tts_service = "wss://localhost:8888/TTS";
var speech_service ="wss://localhost:8888/Speech";
//var tts_service = "wss://"+host+":8888/TTS";
//var face_service = "ws://localhost:8889/Face";
var face_service = "ws://"+host+":8889/Face";
//var tts_service = "ws://localhost:8888/TTS";
//var speaker_service = "ws://localhost:8889/Speaker";
var speaker_service = "ws://"+host+":8889/Speaker";

var context_service = "https://"+host+":8081"
