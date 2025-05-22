from vosk import KaldiRecognizer
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import json
import io




def detect_words(wf, model, framerate = 16000):
    """Just a function for taking an audio stream and retrieving words from VOSK kaldi"""
    
    audio = AudioSegment.from_file(wf, format="wav")
    audio = audio.set_frame_rate(16000)
    
    
    
    rec = KaldiRecognizer(model, framerate)
    rec.AcceptWaveform(audio.raw_data)
    
    result_dict = json.loads(rec.Result())
            
    
    return result_dict['text']

def speech_to_text(filename, model):
    
    audio = AudioSegment.from_wav(filename)
    
    nonsilent_ranges = detect_nonsilent(audio, min_silence_len=200, silence_thresh=-50)
    
    if nonsilent_ranges:
        first_sound_start = nonsilent_ranges[0][0]
        start_trim = max(0, first_sound_start - 500)

        trimmed_audio = audio[start_trim:]

        # Сохраняем в памяти (в формат WAV)
        audio_io = io.BytesIO()
        trimmed_audio.export(filename, format="wav")
       
  
    result = model.transcribe(filename, language="ru")
    return result["text"]
    
    
    """
    model = Model(lang="en-gb")
    commands = str(commands).replace("'", '"')

    rec = KaldiRecognizer(model, framerate, 
    commands)

    transcription = []

    rec.SetWords(True)

    while True:
        data = wf.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result_dict = json.loads(rec.Result())
            transcription.append(result_dict.get("text", ""))

    final_result = json.loads(rec.FinalResult())
    transcription.append(final_result.get("text", ""))

    transcription_text = ' '.join(transcription)
    return transcription_text
    """