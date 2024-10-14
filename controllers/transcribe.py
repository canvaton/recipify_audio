import json
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment
from pydub.effects import normalize


"""
There are multiple audio treatment libraries installed, check requirements.txt,
play around with them if you are having a hard time getting a good result.
"""

def enhance_audio(input_path, output_path):
    # Load the audio file
    audio = AudioSegment.from_wav(input_path)
    
    # 1. Normalize the audio 
    normalized_audio = normalize(audio)
    
    # 2. Noise reduction 
    filtered_audio = normalized_audio.low_pass_filter(3000).high_pass_filter(300)
    
    # 3. Compress the audio 
    compressed_audio = filtered_audio.compress_dynamic_range()
    
    # 4. Remove silent gaps
    silence_threshold = -50  # dB
    min_silence_length = 1000 
    final_audio = compressed_audio.strip_silence(silence_thresh=silence_threshold, silence_len=min_silence_length)
    
    final_audio.export(output_path, format="wav")
    
    return output_path


def transcribe_audio(path):
    model = Model(model_path=r"ml_models\vosk-model-en-us-0.42-gigaspeech") 
    
    wf = wave.open(path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    
    result = ""
    while True:
        """
        The timeframe will need to be calculated in between words for now it's 4seconds, but it can be problematic,
        we might need to remove the treatment for silent gaps and instead use those silent gaps as timeframes.
        """
        data = wf.readframes(20000) 
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result += json.loads(rec.Result())["text"] + " "
    
    result += json.loads(rec.FinalResult())["text"]
    
    return result.strip()


enhanced_audio_path = enhance_audio("audio/test2.wav", "audio/enhanced_test2.wav")
print(transcribe_audio('audio/enhanced_test2.wav'))