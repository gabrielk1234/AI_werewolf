import os
import fitz  # PyMuPDF

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from app_werewolfkill.game_logic.config import url,api_key,analysis_prompt
from django.http import JsonResponse

# Create your views here.
def home(request):
    return render(request, 'app_werewolfkill/home.html')

@csrf_exempt
def api_read_pdf(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        pdf_path = '/'.join(url.split('/')[-3:])
        
        content = extract_text_from_pdf(pdf_path)
        report = analysis_gameplay(content)
        response = {'report':report}
        return JsonResponse(response)
        
def analysis_gameplay(gameplay:str):
    client = OpenAI(
            base_url=url,
            api_key=api_key
        )
    
    response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": f"以下是對局資料，請幫我分析：\n{gameplay}"},
            ]
        )
    return response.choices[0].message.content
            
def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text