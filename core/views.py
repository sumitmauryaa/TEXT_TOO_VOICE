from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from googletrans import Translator
from gtts import gTTS
from uuid import uuid4
import io
import os

translator = Translator()

# Optional MongoDB support - can be enabled if MongoDB is available
USE_MONGODB = False
history_collection = None

try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['polyglot_voice']
    history_collection = db['translation_history']
    USE_MONGODB = True
except Exception as e:
    print(f"MongoDB not available: {e}")
    USE_MONGODB = False


def home(request):
    return render(request, 'index.html')


def translate_text(request):
    if request.method == "POST":
        try:
            original_text = request.POST.get("text", "")
            target_lang = request.POST.get("lang", "en")

            if not original_text.strip():
                return JsonResponse({"error": "Please provide text to translate"}, status=400)

            translated = translator.translate(original_text, dest=target_lang)
            translated_text = translated.text

            if USE_MONGODB and history_collection:
                try:
                    history_collection.insert_one({
                        "original": original_text,
                        "translated": translated_text,
                        "target_lang": target_lang
                    })
                except Exception as e:
                    print(f"Error saving to MongoDB: {e}")

            return JsonResponse({"translated_text": translated_text})
        except Exception as e:
            return JsonResponse({"error": f"Translation failed: {str(e)}"}, status=500)


def text_to_speech(request):
    text = request.GET.get("text", "")
    lang = request.GET.get("lang", "en")

    if not text.strip():
        return JsonResponse({"error": "Please provide text for speech synthesis"}, status=400)

    try:
        # Generate speech in memory (no saving)
        audio_bytes = io.BytesIO()
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)  # Go back to start of stream

        # Return the audio directly as HTTP response
        response = HttpResponse(audio_bytes, content_type="audio/mpeg")
        response["Content-Disposition"] = f'inline; filename="{uuid4()}.mp3"'
        return response

    except Exception as e:
        return JsonResponse({"error": f"Speech synthesis failed: {str(e)}"}, status=500)
