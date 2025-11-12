from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from googletrans import Translator
from gtts import gTTS
from uuid import uuid4
import os

translator = Translator()

# Optional MongoDB support - can be enabled if MongoDB is available
USE_MONGODB = False
history_collection = None

try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    # Test connection
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
            
            # Save to MongoDB if available
            if USE_MONGODB and history_collection:
                try:
                    history_collection.insert_one({
                        "original": original_text,
                        "translated": translated_text,
                        "target_lang": target_lang
                    })
                except Exception as e:
                    print(f"Error saving to MongoDB: {e}")
                    # Continue without saving to DB
            
            return JsonResponse({"translated_text": translated_text})
        except Exception as e:
            return JsonResponse({"error": f"Translation failed: {str(e)}"}, status=500)
def text_to_speech(request):
    text = request.GET.get("text", "")
    lang = request.GET.get("lang", "en")
    
    if not text.strip():
        return JsonResponse({"error": "Please provide text for speech synthesis"}, status=400)
    
    try:
        # Make sure media folder exists
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
        os.makedirs(media_dir, exist_ok=True)

        # Generate unique filename
        filename = os.path.join(media_dir, f"{uuid4()}.mp3")

        # Save TTS audio
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)

        # Open and return the file
        audio_file = open(filename, 'rb')
        response = FileResponse(audio_file, content_type='audio/mpeg')
        
        # Note: In production, implement proper cleanup (celery task, scheduled job, etc.)
        return response
    except Exception as e:
        return JsonResponse({"error": f"Speech synthesis failed: {str(e)}"}, status=500)
