import json
import datetime
from datetime import timedelta
from functools import wraps

from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from django.views.generic import View
from .models import raid_ing, party, partyboard, raid

block_dict = {
    '이벤트 상세정보': '5c89f9ac5f38dd4767218f9d',
    '레이드 정정': '5c767e21384c5541a0eea6f1',
    '레이드 시간 정정': '5c765278e821274ba789841c',
    '레이드 포켓몬 정정': '5c767cf3e821274ba789850e',
    '레이드 장소': '5c923394384c550f44a1a739',
    '레이드 포켓몬': '5ca20d715f38dd08cf0ee9e7',
    '레이드 현황': '5c6f5b355f38dd01ebc09af4',
    '명령어': '5c764774e821274ba7898374',
    '유저등록': '5c7766b805aaa75509eab579',
    '파티 생성': '5c7b7540384c550f44a13f86',
    '파티 참가': '5c7b7540384c550f44a13f86',
}


class SkillResponseView(View):
    def make_response(self, request):
        '''
        I = request(.req_rsp)
        O = skill response(dict)
        받은 .req_rsp를 바탕으로 skill response를 작성
        '''
        resp = skillResponse()
        return resp

    def decode_request(self, request):
        '''
        I = request(django httpRequest object, Binary Json request)
        O = skill response형식(dict)
        I를 .req_rsp(dict)으로 바꾼 후, .res_rsp를 make_response로 전달
        '''
        decoded_request = req_rsp(request)
        return self.make_response(decoded_request)

    def post(self, request):
        '''
        I = request(django httpRequest object, Binary Json request)
        O = response(django jsonResponse object)
        I를 decode_request()에 넣어 return한 값을 jsonresponse로 보낸다.
        '''
        # 받은 json request 풀어보기
        skill_response = self.decode_request(request)
        return JsonResponse(skill_response)

    def raid_board(self):
        raid_bd = raid_ing.objects.filter(
            s_time__gte=(datetime.datetime.now() + datetime.timedelta(minutes=-46))).order_by(
            's_time')
        party_obj = party.objects.filter(time__gte=(datetime.datetime.now() + datetime.timedelta(minutes=-5)))
        raid_board_response = skillResponse()
        raid_dict = {5: [], 4: [], 3: [], 2: [], 1: []}
        raid_objs = raid.objects.filter(ison=True)
        for raid_obj in raid_objs:
            raid_dict[raid_obj.Tier].append(raid_obj.poke.name)
        raid_text = ""
        for k, v in raid_dict.items():
            raid_text += f"{k}성\n{','.join(v)}\n"
        if raid_bd:
            text = ""
            card_list = list()
            for board in raid_bd:
                print(f'board:{board}')
                if board.poke:
                    raid_obj = str(board.poke.poke)
                elif board.tier in [1, 2]:
                    raid_obj = f'{board.tier}성'
                elif board.tier in [3, 4]:
                    raid_obj = f"{board.tier}성"
                elif board.tier == 5:
                    raid_obj = f"{board.tier}성"
                board_text = str(board.s_time.strftime('%H:%M')) + "~" + str(
                    (board.s_time + timedelta(minutes=45)).strftime('%H:%M')) + " " + str(
                    board.gym.nick) + " " + raid_obj + '\n'
                text += board_text
                if party_obj:
                    party_text = ''
                    for i, p in enumerate(party_obj):
                        print(f'p.raid{p.raid}, board{board}')
                        if p.raid == board:
                            party_text += f'{p.time.strftime("%H:%M"):>13} 팟{i + 1} '
                            users = partyboard.objects.filter(party=p)
                            mys_num = users.aggregate(Sum('mys'))['mys__sum'] if users else 0
                            val_num = users.aggregate(Sum('val'))['val__sum'] if users else 0
                            ins_num = users.aggregate(Sum('ins'))['ins__sum'] if users else 0
                            party_text += f'❄{mys_num}명' if mys_num > 0 else ''
                            party_text += f'🔥{val_num}명' if val_num > 0 else ''
                            party_text += f'⚡{ins_num}명' if ins_num > 0 else ''
                            party_text += '\n'
                    text += party_text
                card_list.append(singleResponse(board_text.rstrip(), thumbnail=board.gym.img_url,
                                                thumbnail_link=f'https://map.kakao.com/link/roadview/{board.gym.x_cdn},{board.gym.y_cdn}').block_button(
                    '레이드 정정',
                    {
                        'gym_id': board.id}).block_button_message(
                    '파티 생성', {'gym_name': board.id}, f'{board.gym.name} 팟 생성').share().form)
            # party_card_list = list()
            # 현재 진행중인 파티 query
            # party_ing = party.objects.filter(time__gte=datetime.datetime.now() + datetime.timedelta(minutes=-5))
            # if party_ing:
            # i는 파티순서, p는 파티 오브젝트
            # for i, p in enumerate(party_ing):
            #     party_board = get_party_board(i, p)
            # party_card_list.append(singleResponse(description=party_board).block_button_message('파티 참가',{},f'팟{i+1} 참가').share().form)
            # else:
            # party_card_list.append(singleResponse('파티가 없네요 만들어보시는건 어떨까요?').form)
            raid_board_response.input(singleResponse("레이드 현황", f"{text}").share().card())
            raid_board_response.carousel(card_list)
            raid_board_response.carousel([singleResponse("레이드 목록", f"{raid_text}").share().form], )
            raid_board_response.quickReply("새로고침", "레이드 현황", '레이드 현황')
            raid_board_response.quickReply("레이드 제보", "레이드 제보", "레이드 포켓몬")
            return raid_board_response.default
        else:
            form = {
                "simpleText": {
                    'text': "현재 알려진 레이드가 없습니다! 제보 하시겠어요?"
                }
            }
            return raid_board_response.input(form).quickReply("새로고침", "레이드 현황", '레이드 현황').quickReply("레이드 제보", "레이드 제보",
                                                                                                     "레이드 포켓몬").default


class req_rsp:
    def __init__(self, request):
        '''
        I = request(django httpRequest object, Binary Json request)
        '''
        # json_str / bson -> json
        self.json_str = request.body.decode('utf-8')
        # received_json_data / json -> python dict
        self.received_json_data = json.loads(self.json_str)
        print(self.received_json_data, flush=True)
        # params / 챗봇에서 보내주는 파라미터들
        self.params = self.received_json_data['action']['detailParams']
        # user_id / 챗봇을 발화한 유저 id
        self.user_id = self.received_json_data['userRequest']['user']['id']

    def client_data(self):
        return self.received_json_data['action']['clientExtra']

    def get_time(self):
        dt = json.loads(self.params['sys_plugin_datetime']['value'])['value']
        mod_date = list(map(int, dt[0:10].split('-')))
        mod_time = list(map(int, dt[11:19].split(':')))
        st = datetime.datetime(mod_date[0], mod_date[1], mod_date[2], mod_time[0], mod_time[1], 0, 0)
        return st

    def cal_time(self):
        # 13:33
        text_time = self.params['my_time']['value'] if self.params else self.client_data()['raid_time']
        hours, minutes = list(map(int, text_time.split(':')))
        return datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=hours, minute=minutes))


class skillResponse:
    def __init__(self, Homebutton=True):
        self.default = {
            "version": "2.0",
            "template": {
                'outputs': list(),
                'quickReplies': list(),
            },
            "context": {},
            "data": {},
        }
        if Homebutton:
            self.quickReply("홈", "명령어", "명령어")

    def input(self, data_list):
        self.default["template"]['outputs'].append(data_list)
        return self

    def carousel(self, card_list):
        self.default['template']['outputs'].append({
            "carousel": {
                'type': "basicCard",
                'items': card_list,
            }
        })
        return self

    def quickReply(self, label, message, block, extra=None):
        template = {
            "action": "block",
            "label": label,
            "messageText": message,
            "blockId": block_dict[block] if block_dict.get(block, 0) else block,
        }
        if extra:
            template['extra'] = extra
        self.default["template"]["quickReplies"].append(template)
        return self


class singleResponse:
    def __init__(self, title="", description="", thumbnail="", thumbnail_link=""):
        self.form = dict()
        self.onoff = 0
        if title:
            self.form["title"] = title
        if description:
            self.form["description"] = description
        if thumbnail:
            self.form['thumbnail'] = {'imageUrl': thumbnail, }
            if thumbnail_link:
                self.form['thumbnail']['link'] = {
                    'web': thumbnail_link
                }

    def make_button(original_function):
        @wraps(original_function)
        def wrapper_function(self, *args, **kwargs):  # 1
            if self.onoff != 1:
                self.form['buttons'] = list()
                self.onoff = 1
            return original_function(self, *args, **kwargs)  # 2

        return wrapper_function

    @make_button
    def share(self):
        self.form['buttons'].append({'action': 'share', 'label': '공유하기'})
        return self

    @make_button
    def block_button(self, block, extra="", messagetext="", label=""):
        template = {
            'action': 'block',
            'label': label if label else block,
            'messageText': messagetext if messagetext else block,
            'blockId': block_dict[block] if block_dict.get(block, 0) else block,
        }
        if extra:
            template['extra'] = extra
        self.form['buttons'].append(template)
        return self

    @make_button
    def block_button_message(self, block, extra="", messagetext="", label=""):
        template = {
            'action': 'message',
            'label': label if label else block,
            'messageText': messagetext if messagetext else block,
        }
        if extra:
            template['extra'] = extra
        self.form['buttons'].append(template)
        return self

    @make_button
    def web_button(self, label="", url=""):
        template = {
            'action': 'webLink',
            'label': label,
            'webLinkUrl': url,
        }
        self.form['buttons'].append(template)
        return self

    def card(self):
        return {'basicCard': self.form}


# 간단한 텍스트 아웃풋을 만드려면 simple_text를 이용하자
def simple_text(text, Homebutton=True):
    '''
    간단한 텍스트 아웃풋을 생성하는 함수
    '''
    resp = skillResponse(Homebutton)
    form = {
        "simpleText": {
            'text': text
        }
    }
    return resp.input(form).default


def simple_image(imgUrl, altText):
    return {
        "simpleImage": {
            "imageUrl": imgUrl,
            "altText": altText
        }
    }


def get_party_board(i, p):
    text = ''
    # 파티에 속해있는 유저들
    users = partyboard.objects.filter(party=p)
    if p.raid.poke:
        text += "[팟" + str(i + 1) + "] " + p.time.strftime('%H:%M') + " " + str(p.raid.gym.nick) + " " + str(
            p.raid.poke.poke) + "\n"
        text += "🥇 " + str(int(p.raid.poke.poke.cp_cal(15, 15, 15, 20))) + " /😱 " + str(
            int(p.raid.poke.poke.cp_cal(10, 10, 10, 20))) + "\n"
        text += "🥇 " + str(int(p.raid.poke.poke.cp_cal(15, 15, 15, 25))) + " /😱 " + str(
            int(p.raid.poke.poke.cp_cal(10, 10, 10, 25))) + "(날씨부스트)\n\n"
    else:
        text += "[팟" + str(i + 1) + "] " + p.time.strftime('%H:%M') + " " + str(p.raid.gym.nick) + " " + str(
            p.raid.tier) + "성\n"
    val_num = users.aggregate(Sum('val'))['val__sum'] if users else 0
    ins_num = users.aggregate(Sum('ins'))['ins__sum'] if users else 0
    mys_num = users.aggregate(Sum('mys'))['mys__sum'] if users else 0
    val_text = "🔥(총 " + str(val_num) + "명)\n" if val_num > 0 else ""
    ins_text = "⚡(총 " + str(ins_num) + "명)\n" if ins_num > 0 else ""
    mys_text = "❄(총 " + str(mys_num) + "명)\n" if mys_num > 0 else ""
    val_ord = 0
    ins_ord = 0
    mys_ord = 0
    for u in users:
        u_tag = u.tag[0:15] if u.tag else " "
        if u.val > 0:
            val_ord += 1
            isarrived = "✔" if u.arrived == 1 else str(val_ord)
            val_text += isarrived + ". " + str(u.user.nick)
            if u.val > 1:
                val_text += " +" + str(u.val - 1)
            val_text += " " + u_tag + '\n'
        if u.ins > 0:
            ins_ord += 1
            isarrived = "✔" if u.arrived == 1 else str(ins_ord)
            ins_text += isarrived + ". " + str(u.user.nick)
            if u.ins > 1:
                ins_text += " +" + str(u.ins - 1)
            ins_text += " " + u_tag + '\n'
        if u.mys > 0:
            mys_ord += 1
            isarrived = "✔" if u.arrived == 1 else str(mys_ord)
            mys_text += isarrived + ". " + str(u.user.nick)
            if u.mys > 1:
                mys_text += " +" + str(u.mys - 1)
            mys_text += " " + u_tag + '\n'
    text += val_text + mys_text + ins_text + "\n" + str(p.description) + "\n\n"
    return text
