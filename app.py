import azure.cognitiveservices.speech as speechsdk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import os
import tempfile
import time

# ============================================================
# v56.0 WALI SETTINGS + ORIGINAL ACCENT FIX
# Value se key hata dein, khali string chor dein
AZURE_KEY = st.text_input("Azure Key", value="", type="password")
# ============================================================

# HAR VOICE KA APNA "LOCALE" (TAAKE ACCENT ORIGINAL RAHE)
VOICES = {
    # URDU (Pakistani Accent)
    "Urdu 1 - Asad (News)": {"id": "ur-PK-AsadNeural", "lang": "ur-PK"},
    "Urdu 2 - Uzma (Soft)": {"id": "ur-PK-UzmaNeural", "lang": "ur-PK"},
    "Urdu 3 - Salman (Bold)": {"id": "en-IE-ConnorNeural", "lang": "en-IE"}, # Irish fits deep Urdu tones well
    "Urdu 4 - Mature Male": {"id": "ur-PK-AsadNeural", "lang": "ur-PK"},
    "Urdu 5 - Formal Female": {"id": "ur-PK-UzmaNeural", "lang": "ur-PK"},

    # ENGLISH (US & UK Accents separated)
    "English 1 - Brian (US Narrative)": {"id": "en-US-BrianNeural", "lang": "en-US"},
    "English 2 - Andrew (US Deep)": {"id": "en-US-AndrewNeural", "lang": "en-US"},
    "English 3 - Sonia (UK Posh)": {"id": "en-GB-SoniaNeural", "lang": "en-GB"},
    "English 4 - Ryan (UK Deep)": {"id": "en-GB-RyanNeural", "lang": "en-GB"},
    "English 5 - Emma (US Story)": {"id": "en-US-EmmaNeural", "lang": "en-US"},

    # SPANISH (Spain & Mexico separated)
    "Spanish 1 - Alvaro (Spain Deep)": {"id": "es-ES-AlvaroNeural", "lang": "es-ES"},
    "Spanish 2 - Jorge (Mexico Narrator)": {"id": "es-MX-JorgeNeural", "lang": "es-MX"},
    "Spanish 3 - Elvira (Spain Mature)": {"id": "es-ES-ElviraNeural", "lang": "es-ES"},
    "Spanish 4 - Cecilio (Mexico Bold)": {"id": "es-MX-CecilioNeural", "lang": "es-MX"},
    "Spanish 5 - Dalia (Mexico Soft)": {"id": "es-MX-DaliaNeural", "lang": "es-MX"},

    # ARABIC
    "Arabic 1 - Hamed (Saudi Deep)": {"id": "ar-SA-HamedNeural", "lang": "ar-SA"},
    "Arabic 2 - Zariyah (Saudi Soft)": {"id": "ar-SA-ZariyahNeural", "lang": "ar-SA"},
    "Arabic 3 - Shakir (Egypt Serious)": {"id": "ar-EG-ShakirNeural", "lang": "ar-EG"},
    "Arabic 4 - Salma (Egypt Gentle)": {"id": "ar-EG-SalmaNeural", "lang": "ar-EG"},
    "Arabic 5 - Mouna (Morocco Story)": {"id": "ar-MA-MounaNeural", "lang": "ar-MA"},

    # FRENCH
    "French 1 - Henri (Deep Male)": {"id": "fr-FR-HenriNeural", "lang": "fr-FR"},
    "French 2 - Denise (Clear Female)": {"id": "fr-FR-DeniseNeural", "lang": "fr-FR"},
    "French 3 - Jerome (Documentary)": {"id": "fr-FR-JeromeNeural", "lang": "fr-FR"},
    "French 4 - Brigitte (Soft Story)": {"id": "fr-FR-BrigitteNeural", "lang": "fr-FR"},
    "French 5 - Alain (Mature Male)": {"id": "fr-FR-AlainNeural", "lang": "fr-FR"},

    # RUSSIAN
    "Russian 1 - Dmitry (Cinematic)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU"},
    "Russian 2 - Svetlana (Soft)": {"id": "ru-RU-SvetlanaNeural", "lang": "ru-RU"},
    "Russian 3 - Yari (Narrative)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU"},
    "Russian 4 - Dariya (Warm)": {"id": "ru-RU-SvetlanaNeural", "lang": "ru-RU"},
    "Russian 5 - Nikita (Serious)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU"},

    # CHINESE
    "Chinese 1 - Yunjian (Wise Man)": {"id": "zh-CN-YunjianNeural", "lang": "zh-CN"},
    "Chinese 2 - Yunxi (Narrative)": {"id": "zh-CN-YunxiNeural", "lang": "zh-CN"},
    "Chinese 3 - Xiaoxiao (Soft Female)": {"id": "zh-CN-XiaoxiaoNeural", "lang": "zh-CN"},
    "Chinese 4 - Yunfeng (Serious)": {"id": "zh-CN-YunfengNeural", "lang": "zh-CN"},
    "Chinese 5 - Xiaoyi (Pro)": {"id": "zh-CN-XiaoyiNeural", "lang": "zh-CN"},

    # ITALIAN
    "Italian 1 - Diego (Deep Narrative)": {"id": "it-IT-DiegoNeural", "lang": "it-IT"},
    "Italian 2 - Elsa (Sweet Story)": {"id": "it-IT-ElsaNeural", "lang": "it-IT"},
    "Italian 3 - Benigno (Serious)": {"id": "it-IT-BenignoNeural", "lang": "it-IT"},
    "Italian 4 - Isabella (News)": {"id": "it-IT-IsabellaNeural", "lang": "it-IT"},
    "Italian 5 - Marcello (Classic)": {"id": "it-IT-DiegoNeural", "lang": "it-IT"}
}

class AdnanPerfectV60:
    def __init__(self, root):
        self.root = root
        self.root.title("Adnan Riaz | v56.0 Logic + Fixed Accents (v60)")
        self.root.geometry("1100x900")
        self.root.configure(bg="#020617")

        tk.Label(root, text="ADNAN RIAZ STUDIO", font=("Impact", 50), bg="#020617", fg="#38bdf8").pack(pady=20)
        tk.Label(root, text="v56 STRONG ENGINE + CORRECT LANGUAGE DICTIONARIES", font=("Arial", 10, "bold"), bg="#020617", fg="#94a3b8").pack()

        self.text_area = tk.Text(root, height=12, width=100, bg="#1e293b", fg="white", font=("Georgia", 15), padx=25, pady=25, border=0)
        self.text_area.pack(pady=20)

        self.voice_combo = ttk.Combobox(root, values=list(VOICES.keys()), state="readonly", width=55, font=("Arial", 12))
        self.voice_combo.set("Urdu 1 - Asad (News)")
        self.voice_combo.pack(pady=10)

        self.status_label = tk.Label(root, text="Ready", bg="#020617", fg="#38bdf8")
        self.status_label.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#020617")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="▶ PREVIEW", command=self.start_synth, bg="#0f172a", fg="white", width=22, height=2, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=15)
        tk.Button(btn_frame, text="💾 SAVE MASTER", command=lambda: self.start_synth(save=True), bg="#0284c7", fg="white", width=22, height=2, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=15)

    def start_synth(self, save=False):
        threading.Thread(target=self.process, args=(save,), daemon=True).start()

    def process(self, save_mode):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text: return
        
        selection = VOICES[self.voice_combo.get()]
        voice_id = selection["id"]
        lang_code = selection["lang"]
        
        # --- v56.0 LOGIC (BUT WITH CORRECT LANGUAGE CODE) ---
        # Pehle yahan xml:lang='en-US' fix tha, jis se accent kharab ho raha tha.
        # Ab ye dynamic hai: Urdu k liye 'ur-PK', English k liye 'en-GB/US'
        
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{lang_code}'>
            <voice name='{voice_id}'>
                <mstts:express-as style="narration-professional" styledegree="2">
                    <prosody pitch="-4Hz" rate="-5%" volume="+20.00%">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """
        
        try:
            self.status_label.config(text="Processing Strong Audio...")
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
            speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3)
            
            temp_file = os.path.join(tempfile.gettempdir(), f"master_v60_{int(time.time())}.mp3")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file if not save_mode else None)
            
            if save_mode:
                save_path = filedialog.asksaveasfilename(defaultextension=".mp3")
                if not save_path: return
                audio_config = speechsdk.audio.AudioOutputConfig(filename=save_path)

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if not save_mode: os.startfile(temp_file)
            else:
                # Fallback for voices that don't support narration style
                if "Does not support" in result.error_details:
                    print("Falling back to simple style...")
                    fallback_ssml = f"""
                    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{lang_code}'>
                        <voice name='{voice_id}'>
                            <prosody pitch="-4Hz" rate="-5%" volume="+20.00%">
                                {text}
                            </prosody>
                        </voice>
                    </speak>
                    """
                    synthesizer.speak_ssml_async(fallback_ssml).get()
                    if not save_mode: os.startfile(temp_file)
                else:
                    messagebox.showerror("Error", result.error_details)
        except Exception as e:
            messagebox.showerror("Crash", str(e))
        
        self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdnanPerfectV60(root)
    root.mainloop()
