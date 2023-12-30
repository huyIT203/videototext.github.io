import datetime
import json
import logging
import wave
import numpy as np
import moviepy.editor as mp
import scipy.io.wavfile as wav
import srt
from vosk import KaldiRecognizer

class funcion:
    def __init__(
        self,
        video,
        audio,
        mono_audio,
        transcript,
        words,
        subtitles,
        model,
    ) -> None:
        self.video = video
        self.audio = audio
        self.mono_audio = mono_audio
        self.transcript = transcript
        self.words = words
        self.subtitles = subtitles
        self.model = model

    def load_data(self):
        try:
            with open(self.words, "r") as json_file:
                words = json.load(json_file)
        except:
            words = []
        return words

    def save_data(self, data):
        with open(self.words, "w") as json_file:
            json.dump(data, json_file)

    def extract_transcript(self):
        if self.video != "":
            my_clip = mp.VideoFileClip(self.video)
            if my_clip.audio:
                my_clip.audio.write_audiofile(self.audio, verbose=False, logger=None)

        # transcribe audio file
        transcript, words, subtitle = self.handle_speech_2_text()

        with open(self.transcript, "w+") as fil:
            fil.write(transcript)

        # save words to file
        self.save_data(words)

        with open(self.subtitles, "w+", encoding="utf8") as f:
            f.writelines(subtitle)

    def handle_speech_2_text(self):
        sample_rate, stereo_data = wav.read(self.audio)

        if len(stereo_data.shape) == 1:
            stereo_data = np.column_stack((stereo_data, stereo_data))

        left_channel, right_channel = np.hsplit(stereo_data, 2)
        mono_data = (left_channel + right_channel) / 2
        mono_data = mono_data.astype("int16")
        wav.write(self.mono_audio, sample_rate, mono_data)

        wf = wave.open(self.mono_audio, "rb")
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getcomptype() != "NONE"
        ):
            logging.error("Audio phải là l WAV hoặc mp3 .")
            return "", "", ""

        rec = KaldiRecognizer(self.model, wf.getframerate())

        rec.SetWords(True)
        rec.SetPartialWords(True)

        transcript = []  #
        results = []
        subs = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        results.append(rec.FinalResult())

        WORDS_PER_LINE = 14
        total = []
        total_words = []
        for res in results:
            jres = json.loads(res)
            if not "result" in jres:
                continue
            words = jres["result"]
            total_words.extend(words)
            for j in range(0, len(words), WORDS_PER_LINE):
                line = words[j : j + WORDS_PER_LINE]
                s = srt.Subtitle(
                    index=len(subs),
                    content=" ".join([l["word"] for l in line]),
                    start=datetime.timedelta(seconds=line[0]["start"]),
                    end=datetime.timedelta(seconds=line[-1]["end"]),
                )
                total.append(s.content)
                subs.append(s)

        transcript = " ".join(total)
        subtitle = srt.compose(subs)

        return (transcript, total_words, subtitle)
