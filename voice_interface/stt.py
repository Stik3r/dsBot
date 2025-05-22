from pydub import AudioSegment
from io import BytesIO




def speech_to_text(wf, model):
    """Just a function for taking an audio stream and retrieving words from VOSK kaldi"""
    
    audio = AudioSegment.from_file(wf, format="wav")
    audio.export("temp.wav", format="wav")
    
    result = model.transcribe("temp.wav", language="ru")
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