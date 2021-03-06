import json, random
from django.db.models import Sum
from .models import restaurant, ratedRestaurant
from .skills import req_rsp, skillResponse, singleResponse, simple_text, SkillResponseView


class randomRestaurant(SkillResponseView):
    def make_response(self, request):
        restaurant_obj = restaurant.objects.filter(occasion__contains="식사")
        recommendedRestaurant = random.choice(restaurant_obj)
        name = recommendedRestaurant.name
        good = ratedRestaurant.objects.filter(restaurant=recommendedRestaurant, rating=1).aggregate(Sum('rating'))['rating__sum']
        bad = ratedRestaurant.objects.filter(restaurant=recommendedRestaurant, rating=-1).aggregate(Sum('rating'))['rating__sum']
        description = f"{recommendedRestaurant.occasion.strip()} / 👍: {good if good else 0} / 👎: {abs(bad) if bad else 0}\n{recommendedRestaurant.place.strip()}\n{recommendedRestaurant.childCategory.strip() if recommendedRestaurant.childCategory else recommendedRestaurant.parentCategory.strip()}"
        url = recommendedRestaurant.url
        restaurantCard = singleResponse(name, description).web_button("상세보기", url).card()
        positive = {"name":name, "result":1}
        negative = {"name":name, "result":-1}
        response = skillResponse(Homebutton=False).input(restaurantCard).quickReply("다시 뽑기", "다시 뽑기", "5e46597292690d00016cb7ef").quickReply("👍","좋아요","5e51de30ffa7480001302067",positive).quickReply("👎","별로에요","5e51de30ffa7480001302067",negative)
        return response.default


class restaurantRating(SkillResponseView):
    def make_response(self, request):
        user = request.user_id
        extra = request.client_data()
        if extra:
            Restaurant = restaurant.objects.filter(name=extra['name']).first()
            result = extra["result"]
            ratedRestaurant.objects.create(restaurant=Restaurant, user_id=user, rating=result)
            if result == 1:
                return simple_text(f"맛있는 식사 되셨나요? {extra['name']}을(를) 평가해주셔서 감사해요!", False)
            elif result == -1:
                return simple_text(f"식사가 별로였다니!😢 참고해서 더 좋은 맛집을 추천해드릴게요!", False)
        else:
            return simple_text(f"시스템 오류입니다. joel.e에게 알려주세요!", False)
