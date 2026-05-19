from django.shortcuts import render

# Create your views here.

import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types

# Initialize the GenAI client (automatically loads GEMINI_API_KEY from environment)
client = genai.Client()

def chat_home(request):
    """Renders the main chat interface."""
    # Clear history on a fresh page reload if you want a clean slate
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    return render(request, 'chat.html')

@csrf_exempt
def send_message(request):
    """API endpoint to process user messages and return AI responses."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # 1. Retrieve history from Django Session
            history_data = request.session.get('chat_history', [])
            
            # 2. Reconstruct the historical contents for the SDK
            contents = []
            for msg in history_data:
                contents.append(
                    types.Content(
                        role=msg['role'],
                        parts=[types.Part.from_text(text=msg['text'])]
                    )
                )
            
            # 3. Initialize the chat session with existing history
            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=contents
            )
            
            # 4. Send the new message and capture response
            response = chat.send_message(user_message)
            bot_reply = response.text

            # 5. Update session history to retain context for the next turn
            history_data.append({'role': 'user', 'text': user_message})
            history_data.append({'role': 'model', 'text': bot_reply})
            request.session['chat_history'] = history_data
            request.session.modified = True 

            return JsonResponse({'reply': bot_reply})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)