import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
import json

def get_ollama_response(message):
    try:
        response = requests.post('http://localhost:11434/api/generate',
            json={
                'model': 'llama3',
                'prompt': f"You are FormEase assistant. Response to: {message}",
                'stream': False
            })
        if response.status_code == 200:
            return response.json()['response']
        return "I apologize, but I'm having trouble processing your request at the moment."
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request at the moment. Error: {str(e)}"

def get_chatbot_response(message):
    return get_ollama_response(message)

@login_required
def chat_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            response = get_chatbot_response(user_message)
            
            # Save the chat message and response
            chat = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=response
            )
            
            return JsonResponse({
                'response': response,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
