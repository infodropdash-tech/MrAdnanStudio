import streamlit as st  # <--- Sab se pehle ye aana chahiye
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import time

# 1. Page Config (Ye hamesha imports ke foran baad aati hai)
st.set_page_config(page_title="Adnan Riaz Studio", page_icon="🎙️")

# 2. Password Protection (Ye Page Config ke baad aana chahiye)
# -----------------------------------------------------------
password = st.text_input("🔒 Enter Password to Login:", type="password")

if password != "Adnan123":  # <--- Yahan apni marzi ka password rakh lo
    st.info("Please enter the correct password to access the studio.")
    st.stop()  # <--- Ye command app ko yahin rok degi jab tak password sahi na ho
# -----------------------------------------------------------

# 3. Baqi App Yahan Se Shuru Hogi
st.title("🎙️ Adnan Riaz Global Studio")
st.caption("Professional Azure Neural Engine | 40 Unique Voices")
# --- SECRET KEY MANAGEMENT ---
if "AZURE_KEY" in st.secrets:
    AZURE_KEY = st.secrets["AZURE_KEY"]
    AZURE_REGION = st.secrets["AZURE_REGION"]
else:
    st.warning("⚠️ Azure Key not found in Secrets. Please add it in Settings > Secrets.")
    AZURE_KEY = st.text_input("Enter Azure Key manually:", type="password")
    AZURE_REGION = st.text_input("Enter Region (e.g., eastus):", value="eastus")

# --- 40 UNIQUE VOICES WITH CUSTOM TONES ---
# Har voice ka apna Pitch, Rate aur Style hai taake wo different lagen
VOICES = {
    # --- URDU (Pakistani & Deep Tones) ---
    "Urdu 1 - Asad (News Anchor)": {"id": "ur-PK-AsadNeural", "lang": "ur-PK", "pitch": "-2Hz", "rate": "-5%", "style": "narration-professional"},
    "Urdu 2 - Uzma (Soft Story)": {"id": "ur-PK-UzmaNeural", "lang": "ur-PK", "pitch": "0Hz", "rate": "-10%", "style": "cheerful"},
    "Urdu 3 - Salman (Heavy/Bold)": {"id": "en-IE-ConnorNeural", "lang": "en-IE", "pitch": "-5Hz", "rate": "-8%", "style": "whispering"}, # Irish accent maps well to deep Urdu
    "Urdu 4 - Mature Male": {"id": "ur-PK-AsadNeural", "lang": "ur-PK", "pitch": "-4Hz", "rate": "-5%", "style": "sad"},
    "Urdu 5 - Formal Female": {"id": "ur-PK-UzmaNeural", "lang": "ur-PK", "pitch": "+2Hz", "rate": "-5%", "style": "newscast"},

    # --- ENGLISH (US & UK Accents) ---
    "English 1 - Brian (US Deep Narrative)": {"id": "en-US-BrianNeural", "lang": "en-US", "pitch": "-5Hz", "rate": "-5%", "style": "narration-professional"},
    "English 2 - Sonia (UK Posh/Royal)": {"id": "en-GB-SoniaNeural", "lang": "en-GB", "pitch": "0Hz", "rate": "-5%", "style": "cheerful"},
    "English 3 - Andrew (US Mystery)": {"id": "en-US-AndrewNeural", "lang": "en-US", "pitch": "-6Hz", "rate": "-8%", "style": "sad"},
    "English 4 - Ryan (UK Bold)": {"id": "en-GB-RyanNeural", "lang": "en-GB", "pitch": "-3Hz", "rate": "0%", "style": "shouting"},
    "English 5 - Ava (US Smooth News)": {"id": "en-US-AvaNeural", "lang": "en-US", "pitch": "0Hz", "rate": "0%", "style": "newscast"},

    # --- SPANISH (Spain & Mexico) ---
    "Spanish 1 - Alvaro (Spain Deep)": {"id": "es-ES-AlvaroNeural", "lang": "es-ES", "pitch": "-4Hz", "rate": "-5%", "style": "narration-professional"},
    "Spanish 2 - Jorge (Mexico Narrator)": {"id": "es-MX-JorgeNeural", "lang": "es-MX", "pitch": "-2Hz", "rate": "-2%", "style": "newscast"},
    "Spanish 3 - Elvira (Spain Mature)": {"id": "es-ES-ElviraNeural", "lang": "es-ES", "pitch": "-2Hz", "rate": "-8%", "style": "friendly"},
    "Spanish 4 - Cecilio (Mexico Bold)": {"id": "es-MX-CecilioNeural", "lang": "es-MX", "pitch": "-5Hz", "rate": "-5%", "style": "shouting"},
    "Spanish 5 - Dalia (Mexico Soft)": {"id": "es-MX-DaliaNeural", "lang": "es-MX", "pitch": "0Hz", "rate": "-5%", "style": "cheerful"},

    # --- ARABIC (Saudi, Egypt, Morocco) ---
    "Arabic 1 - Hamed (Saudi Deep)": {"id": "ar-SA-HamedNeural", "lang": "ar-SA", "pitch": "-4Hz", "rate": "-5%", "style": "narration-professional"},
    "Arabic 2 - Shakir (Egypt Strong)": {"id": "ar-EG-ShakirNeural", "lang": "ar-EG", "pitch": "-3Hz", "rate": "0%", "style": "shouting"},
    "Arabic 3 - Zariyah (Saudi Soft)": {"id": "ar-SA-ZariyahNeural", "lang": "ar-SA", "pitch": "0Hz", "rate": "-5%", "style": "cheerful"},
    "Arabic 4 - Salma (Egypt Gentle)": {"id": "ar-EG-SalmaNeural", "lang": "ar-EG", "pitch": "+1Hz", "rate": "-5%", "style": "friendly"},
    "Arabic 5 - Mouna (Morocco Story)": {"id": "ar-MA-MounaNeural", "lang": "ar-MA", "pitch": "-2Hz", "rate": "-10%", "style": "narration-professional"},

    # --- FRENCH ---
    "French 1 - Henri (Cinema Deep)": {"id": "fr-FR-HenriNeural", "lang": "fr-FR", "pitch": "-4Hz", "rate": "-5%", "style": "narration-professional"},
    "French 2 - Denise (Clear)": {"id": "fr-FR-DeniseNeural", "lang": "fr-FR", "pitch": "0Hz", "rate": "0%", "style": "cheerful"},
    "French 3 - Jerome (Pro)": {"id": "fr-FR-JeromeNeural", "lang": "fr-FR", "pitch": "-2Hz", "rate": "-5%", "style": "newscast"},
    "French 4 - Brigitte (Soft)": {"id": "fr-FR-BrigitteNeural", "lang": "fr-FR", "pitch": "+1Hz", "rate": "-8%", "style": "friendly"},
    "French 5 - Alain (Mature)": {"id": "fr-FR-AlainNeural", "lang": "fr-FR", "pitch": "-3Hz", "rate": "-5%", "style": "sad"},

    # --- RUSSIAN ---
    "Russian 1 - Dmitry (Heavy)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU", "pitch": "-5Hz", "rate": "-5%", "style": "narration-professional"},
    "Russian 2 - Svetlana (Soft)": {"id": "ru-RU-SvetlanaNeural", "lang": "ru-RU", "pitch": "0Hz", "rate": "-5%", "style": "cheerful"},
    "Russian 3 - Yari (Story)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU", "pitch": "-2Hz", "rate": "-8%", "style": "sad"},
    "Russian 4 - Dariya (Warm)": {"id": "ru-RU-SvetlanaNeural", "lang": "ru-RU", "pitch": "+1Hz", "rate": "-2%", "style": "friendly"},
    "Russian 5 - Nikita (Bold)": {"id": "ru-RU-DmitryNeural", "lang": "ru-RU", "pitch": "-6Hz", "rate": "-2%", "style": "shouting"},

    # --- CHINESE ---
    "Chinese 1 - Yunjian (Wise)": {"id": "zh-CN-YunjianNeural", "lang": "zh-CN", "pitch": "-5Hz", "rate": "-10%", "style": "narration-professional"},
    "Chinese 2 - Yunxi (Narrator)": {"id": "zh-CN-YunxiNeural", "lang": "zh-CN", "pitch": "-2Hz", "rate": "-5%", "style": "cheerful"},
    "Chinese 3 - Xiaoxiao (Soft)": {"id": "zh-CN-XiaoxiaoNeural", "lang": "zh-CN", "pitch": "+1Hz", "rate": "-5%", "style": "friendly"},
    "Chinese 4 - Yunfeng (Serious)": {"id": "zh-CN-YunfengNeural", "lang": "zh-CN", "pitch": "-4Hz", "rate": "-2%", "style": "shouting"},
    "Chinese 5 - Xiaoyi (Pro)": {"id": "zh-CN-XiaoyiNeural", "lang": "zh-CN", "pitch": "0Hz", "rate": "0%", "style": "newscast"},

    # --- ITALIAN ---
    "Italian 1 - Diego (Deep)": {"id": "it-IT-DiegoNeural", "lang": "it-IT", "pitch": "-3Hz", "rate": "-5%", "style": "narration-professional"},
    "Italian 2 - Elsa (Sweet)": {"id": "it-IT-ElsaNeural", "lang": "it-IT", "pitch": "0Hz", "rate": "-5%", "style": "cheerful"},
    "Italian 3 - Benigno (Serious)": {"id": "it-IT-BenignoNeural", "lang": "it-IT", "pitch": "-4Hz", "rate": "-2%", "style": "sad"},
    "Italian 4 - Isabella (News)": {"id": "it-IT-IsabellaNeural", "lang": "it-IT", "pitch": "0Hz", "rate": "0%", "style": "newscast"},
    "Italian 5 - Marcello (Classic)": {"id": "it-IT-DiegoNeural", "lang": "it-IT", "pitch": "-2Hz", "rate": "-8%", "style": "friendly"}
}

# --- MAIN UI ---
voice_name = st.selectbox("Choose a Voice Model:", list(VOICES.keys()))
text_input = st.text_area("Enter your Script here:", height=200, placeholder="Type something...")

if st.button("▶ GENERATE AUDIO"):
    if not text_input or not AZURE_KEY:
        st.error("Please enter text and ensure Azure Key is connected.")
    else:
        # Get settings for the selected voice
        profile = VOICES[voice_name]
        
        # --- DYNAMIC SSML LOGIC (Different Tone for Each Voice) ---
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{profile["lang"]}'>
            <voice name='{profile["id"]}'>
                <mstts:express-as style="{profile["style"]}" styledegree="2">
                    <prosody pitch="{profile["pitch"]}" rate="{profile["rate"]}" volume="+20.00%">
                        {text_input}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """

        try:
            with st.spinner("Processing with Neural Engine..."):
                speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
                speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3)
                
                temp_file = os.path.join(tempfile.gettempdir(), f"web_v62_{int(time.time())}.mp3")
                audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file)

                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                result = synthesizer.speak_ssml_async(ssml).get()

                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    st.success(f"Audio Generated! ({voice_name})")
                    
                    # Read and Play Audio
                    with open(temp_file, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button("💾 Download MP3", audio_bytes, file_name="voiceover.mp3", mime="audio/mp3")
                else:
                    # Fallback for voices that don't support specific styles
                    st.warning("Specific style not supported, switching to Standard Mode...")
                    fallback_ssml = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{profile['lang']}'><voice name='{profile['id']}'><prosody pitch='{profile['pitch']}' rate='{profile['rate']}'>{text_input}</prosody></voice></speak>"
                    synthesizer.speak_ssml_async(fallback_ssml).get()
                    
                    with open(temp_file, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button("💾 Download MP3", audio_bytes, file_name="voiceover.mp3", mime="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")



