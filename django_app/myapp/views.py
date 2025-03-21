import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from datetime import datetime
import nats
from asgiref.sync import sync_to_async
from .models import Orders, Payments, UsersBot

logger = logging.getLogger(__name__)

# Create your views here.

async def index(request):
    return redirect('/admin/')

@csrf_exempt
@require_http_methods(["POST"])
async def yookassa_webhook(request):
    try:
        data = json.loads(await sync_to_async(lambda: request.body)())
        if data.get('event') == 'payment.succeeded':
            json_data = json.dumps(data, ensure_ascii=False)
            nc = await nats.connect(os.getenv('NATS_URL'))
            js = nc.jetstream()
            headers = {
                'Timestamp': str(datetime.now().timestamp())
            }
            
            await js.publish(
                subject=os.getenv('SUBJECT_PAYMENT'), 
                stream=os.getenv('STREAM_NAME'),
                payload=json_data.encode(encoding='utf-8'),  
                headers=headers)
            
            await nc.close()
            logger.info("Webhook обработал событие payment.succeeded")
            
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}", exc_info=True)
    
    return JsonResponse({}, status=200)
