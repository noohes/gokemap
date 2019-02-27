import datetime
import json
import copy
from datetime import timedelta
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import raid_ing, raid


def make_simple_text_response(text):
    skill_response_default = {
            "version":"2.0",
            "template":{},
            "context":{},
            "data":{},
        }
    data = {
        "simpleText":{}
        }
    lis = list()
    data['simpleText']['text'] = text
    lis.append(data)
    skill_response_default['template']['outputs'] = lis
    return skill_response_default


# 레이드 시작 가능 시간을 구해주는 함수
# def get_datetime(time, date):
#     # 24시 에러 제거
#     if time[0] == 24:
#         time[0] = 0
#     # input을 datetime형식으로 변환
#     st = datetime.datetime(date[0], date[1], date[2], time[0], time[1], 0, 0)
#     # st_li는 am, pm, 어제, 오늘, 내일 모두 고려한 선택지
#     st_li = [st, st+timedelta(hours=12), st+timedelta(hours=-12), st+timedelta(days=1), st+timedelta(days=-1), st+timedelta(hours=36), st+timedelta(hours=-36)]
#     # st_li_gap은 현재 시간과 선택지 간의 차를 구함
#     st_li_gap = [abs(t-datetime.datetime.now()) for t in st_li]
#     # 가장 차가 적은 st_li_gap의 인덱스를 st_li로 넘겨서 return
#     return st_li[st_li_gap.index(min(st_li_gap))]


# raid_post의 jsonresponse를 만들어주는 함수
def get_resp(params, raid_ing_object, stt):
    if 'raid_level' in params:
        raid_ing_object.update(poke=None, tier=params['raid_level']['value'], s_time=stt)
        return make_simple_text_response('raid level receive ok')
    if 'raid_poke_name' in params:
        poke = raid.objects.filter(poke__name=params['raid_poke_name']['value'])
        raid_ing_object.update(poke=poke[0].id, tier=poke[0].Tier, s_time=stt)
        return make_simple_text_response('raid poke receive ok')


@csrf_exempt
def post(request):
    json_str = request.body.decode('utf-8')
    received_json_data = json.loads(json_str)
    params = received_json_data['action']['detailParams']
    date = list(map(int, params['date_time']['value']['value'][0:9].split('-')))
    time = list(map(int, params['date_time']['value']['value'][11:18].split(':')))
    stt = datetime.datetime(date[0], date[1], date[2], time[0], time[1], 0, 0)
    raid_ing_object = raid_ing.objects.filter(gym__name=params['gym_name']['value'])
    return JsonResponse(get_resp(params, raid_ing_object, stt))


def get_raid_board(raid_bd):
    text = ""
    for raid in raid_bd:
        raid_obj = ""
        if raid.poke:
            raid_obj += str(raid.poke)
        else:
            raid_obj += str(raid.tier) + "성"
        text += str(raid.s_time.strftime('%H:%M')) + "~" + str((raid.s_time + timedelta(minutes=45)).strftime('%H:%M')) + " " + str(raid.gym.nick) + " " + raid_obj + "\n"
    if text == "":
        text += "현재 알려진 레이드가 없습니다! 제보하시겠어요?"
    return text


@csrf_exempt
def board(request):
    raid_bd = raid_ing.objects.filter(s_time__gte=(timezone.now() + timezone.timedelta(minutes=-46))).order_by('s_time')
    return JsonResponse(make_simple_text_response(get_raid_board(raid_bd)))


def mod(request):
    #json data decode
    json_str = request.body.decode('utf-8')
    # 디코드한 json data 풀어보기
    received_json_data = json.loads(json_str)
    # json 파일에서 입력값을 전달해주는 param 접근
    params = received_json_data['action']['detailParams']
    raid_ing_object = raid_ing.objects.filter(gym__name=params['gym_name']['value'])
    if 'date_time' in params:
        mod_date = list(map(int, params['date_time']['value']['value'][0:9].split('-')))
        mod_time = list(map(int, params['date_time']['value']['value'][11:18].split(':')))
        st = datetime.datetime(mod_date[0], mod_date[1], mod_date[2], mod_time[0], mod_time[1], 0, 0)
        raid_ing_object.update(s_time=st)
    if 'raid_poke_name' in params:
        poke = raid.objects.filter(poke__name=params['raid_poke_name']['value'])
        raid_ing_object.update(poke=poke[0].id, tier=poke[0].Tier)
    return JsonResponse(make_simple_text_response("레이드가 정정되었습니다."))