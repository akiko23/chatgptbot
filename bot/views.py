import hashlib
import hmac
import json
import time

import asyncio
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from config import db, secretKey, bot


# Create your views here.
@csrf_exempt
def index(req: WSGIRequest):
    if req.method.upper() == "POST":
        print(req.body)
        data = {item.split(":")[0].replace("\"", ""): item.split(":")[1].replace("\"", "") for item in
                str(req.body).replace("\\r\\n", "").replace("b'", "").replace("'", "").split(",")}

        order_reference = data.get("orderReference")
        if data.get("transactionStatus") == 'Approved':
            db.set_purchase(order_reference=order_reference)
            product_id, user_id, order_time, msg_id = order_reference.split("-")[1:]

            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(bot.delete_message(user_id, msg_id))
                loop.run_until_complete(bot.delete_message(user_id, msg_id + 1))
            except:
                pass
            loop.run_until_complete(bot.send_message(user_id, f"Спасибо за покупку!"))

        status = "accept" if data.get("transactionStatus") == 'Approved' else "denied"
        response_time = int(time.time())

        response = {
            "orderReference": order_reference,
            "status": status,
            "time": response_time,
            "signature": hmac.new(secretKey,
                                  ";".join([order_reference, status, str(response_time)]).encode("utf-8"),
                                  hashlib.md5).hexdigest()
        }

        return HttpResponse(json.dumps(response))
    return render(req, "index.html")


def csrf_failure(request, reason=""):
    print(request.body)