from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import event
from .skills import req_rsp, make_simple_text_response, make_basic_card, make_carousel


@csrf_exempt
def board(request):
    # 시작했고 아직 안 끝난 이벤트
    event_now = event.objects.filter(end_time__gte=timezone.now(), start_time__lte=timezone.now()).order_by('start_time')
    # 아직 시작 안 한 이벤트
    event_upcoming = event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')
    card_list = list()
    for e in event_now:
        time_delta = e.end_time - timezone.now()
        e_time = str(e.end_time.strftime('%m/%d %H:%M')) + " 종료" + "(종료까지 " + str(time_delta).replace("days", "일").replace(":","시간",1).replace(":","분").replace(".","초")[:-6] + ")"
        card_list.append(make_basic_card(e.title, e_time, e.id, e.img_url))
    for e in event_upcoming:
        time_delta = e.start_time - timezone.now()
        e_time = str(e.start_time.strftime('%m/%d %H:%M')) + " 시작" + "(시작까지 " + str(time_delta).replace("days", "일").replace(":","시간",1).replace(":","분").replace(".","초")[:-6] + ")"
        card_list.append(make_basic_card(e.title, e_time, e.id, e.img_url))
    return JsonResponse(make_carousel(card_list))


@csrf_exempt
def detail(request):
    req = req_rsp(request)
    event_obj = event.objects.filter(id=req.client_data).first()
    # 이미 시작한 이벤트
    if event_obj.start_time < timezone.now():
        time_delta = event_obj.end_time - timezone.now()
        e_time = str(event_obj.end_time.strftime('%m/%d %H:%M')) + " 종료" + "(종료까지 " + str(time_delta).replace("days", "일").replace(":","시간 ",1).replace(":","분 ").replace(".","초 ")[:-6] + ")"
        text = event_obj.title + "\n" + e_time + "\n\n" + event_obj.description
        return JsonResponse(make_simple_text_response(text))
    else:
        time_delta = event_obj.start_time - timezone.now()
        e_time = str(event_obj.start_time.strftime('%m/%d %H:%M')) + " 시작" + "(시작까지 " + str(time_delta).replace("days", "일").replace(":","시간 ",1).replace(":","분 ").replace(".","초 ")[:-6] + ")"
        text = event_obj.title + "\n" + e_time + "\n\n" + event_obj.description
        return JsonResponse(make_simple_text_response(text))