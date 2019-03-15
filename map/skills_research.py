import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import temp
from .skills import make_simple_text_response, req_rsp


@csrf_exempt
def post(request):
    req = req_rsp(request)
    if (req.user_id == 'b32a22d3306d1fd49149991ec0293f580186b459ec3bd6d29a0e36547409d8385c') or (req.user_id == '457ae6a6448028ad73d2cf1a35ab3eac4c18334edf16d13446a114bcf9476ea951'):
        temp.objects.update(id=1, date=datetime.datetime.now(), description=req.params['sys_text']['value'])
        return JsonResponse(make_simple_text_response("리서치 제보 감사합니다"))
    else:
        return JsonResponse(make_simple_text_response("현재 리서치 제보는 몇몇분 한정으로 기능하고 있습니다."))


@csrf_exempt
def board(request):
    research_bd = temp.objects.filter(date=(timezone.now().date())).first()
    rsch = getattr(research_bd, "description", "오늘은 리서치가 아직 제보되지 않았네요 ㅠㅁㅠ")
    return JsonResponse(make_simple_text_response(rsch))