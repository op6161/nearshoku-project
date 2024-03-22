from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from . import models
import json
import requests


# settings, tools
def constant(func):
    '''
        A decorator function for _Const Class
    '''
    def func_set(self, value):
        '''
            you can't edit constant
        '''
        raise TypeError

    def func_get(self):
        '''
            you can use constant
        '''
        return func()
    return property(func_get, func_set)

class _Const(object):
    '''
        This Class is saving constants
    '''
    @constant
    def GOOGLE_API(): # is not err
        return 'GEOLOCATION_API_KEY'

    @constant
    def RECRUIT_API():
        return 'HOTPEPPER_API_KEY'

def check_unicode(text):
    '''
        Replace the str has unicode u3000 -> ' ' (space)

        Args:
            text(str): the string that has unicode u3000
        Returns:
            text(str): the string that changed from u3000 to space
    '''
    return text.replace('\u3000',' ')

def make_hash():
    '''
        Make hash key from current time

        Returns: hash key (int)
    '''
    import time
    key = time.time_ns()
    return hash(key)

def parsing_xml_to_json(xml_data):
    '''
        Parse the xml data into json format

        Args:
             xml_data(requests.get():xml format)
        Raises:
            -
        Returns:
            json_data(requests.get().txt:json format)
    '''
    import xmltodict
    xml_pars = xmltodict.parse(xml_data.text)
    json_dump = json.dumps(xml_pars)
    json_data = json.loads(json_dump)
    return json_data

def model_form_save(item_list, form_model):
    '''
        Save the items into the modelform(db)

        Args:
            item_list(list): list of dict items
            form_model(models.Model): model form in models.py
    '''
    object_bulk = [form_model(**item) for item in item_list]
    form_model.objects.bulk_create(object_bulk)

def combine_dictionary(dict1, dict2):
    '''
        Combine two dictionaries. but they should have different keys
        * if dicts have same keys, it can update dict1's value without combining

        Args:
            dict1(dict)
            dict2(dict)
        Returns dictionary: dict1 + dict2
    '''
    dict1.update(dict2)
    return dict1

CONST = _Const() # const class using set

# use API function
def get_api(api_type):
    '''
        Get protected key with python-dotenv

        Args:
            api_type(str): a .env key for using API
        Returns:
            api_key(str)
    '''
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.environ.get(api_type)
    return api_key


def get_latlng(api_key):
    '''
        Get user's current lat/lng from google-geolocation

        Args:
            api_key(str): googlemaps API key
        Returns:
            lat(float): user's current Latitude
            lng(float): user's current Longitude
    '''
    API_HOST = 'https://www.googleapis.com/geolocation/v1/'
    url = f'{API_HOST}geolocate?key={api_key}'

    response_geolocate = json.loads(requests.post(url).text)

    lat = response_geolocate['location']['lat']
    lng = response_geolocate['location']['lng']

    return lat, lng

# # # 구글맵과 연동 필요함
def get_location(lat, lng, api_key):
    '''
        Get user's location for lat/lng from google-geocode API

        Args:
            api_key(str): googlemaps API key
        Raises:
            -
        Returns:
            -
    '''
    API_HOST = 'https://maps.googleapis.com/maps/api/geocode/'
    url = f'{API_HOST}json?latlng={lat},{lng}&key={api_key}'
    response_geocode = json.loads(requests.post(url).text)
    return response_geocode


def get_current_latlng():
    '''

    '''
    api_key = get_api(CONST.GOOGLE_API)
    current_lat, current_lng = get_latlng(api_key)
    context = {'current_lat': current_lat, 'current_lng': current_lng}
    return context
# # 이 두 함수는 조건부로 합치면 좋을 것 같다, view.result 같이 수정 필요함 주의
def get_selected_latlng():
    '''

    '''
    api_key = get_api(CONST.GOOGLE_API)
    current_lat, current_lng = get_latlng(api_key)
    selected_lat, selected_lng = 1,1
    context = {
        'current_lat': current_lat, 'current_lng': current_lng,
        'selected_lat': selected_lat, 'selected_lng': selected_lng}
    return context


def load_shop_info(lat,lng,range,model_hash):
    '''
        Load shop info from hotpepper API

        Args:
            lat(float): latitude
            lng(float): longitude
            range(int): range option
            model_hash(int): a hash key made by make_hash()
        Raises:
            KeyError: 검색 결과가 없는 경우
        Returns:
            shop_info(list): list of dicts shop information
    '''
    api_key = get_api(CONST.RECRUIT_API)
    API_HOST = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    headers = {
        'Content-Type': 'application/json',
        'charset': 'UTF-8',
        'Accept': '*/*'
    }
    param = {
        'key': f'{api_key}',
        'lat': lat,
        'lng': lng,
        'range': range,
        #'order':order, # order 거리순/권장순 변수 나중에 하자
        # 'format':'json'
    }

    query = '?'
    keys = param.keys()
    vals = param.values()

    for key, val in zip(keys, vals):
        query += f'{key}={val}&'

    url = API_HOST + query

    try:
        hot_pepper_response = requests.get(url, headers=headers)
    except Exception:
        raise Exception

    shop_info_json = parsing_xml_to_json(hot_pepper_response)
    try:
        shop_info_json = shop_info_json['results']['shop'] #****
    except KeyError:
        # API의 한계로 일본 외의 나라에서는 사용할 수 없다
        # 일본 내에서도 주변에 등록된 식당이 없다면 사용할 수 없을 것 같다
        # >> keyError:'shop' 발생함
        # 검색 결과가 없습니다 출력하면 좋을 듯 하다
        raise KeyError
    shop_info = []

    for shop in shop_info_json:
        temp = {
            'shop_id': shop['id'],
            'shop_name': check_unicode(shop['name']),
            'shop_kana': check_unicode(shop['name_kana']),
            'shop_access': check_unicode(shop['access']),
            'shop_thumbnail': shop['logo_image'],
            'shop_model_hash':model_hash
        }
        shop_info.append(temp)
    return shop_info

# views
# # # 페이징 구현 이후 views.result 합치기
def shop_show(request, cont1, model_hash):
    shop_list = models.ShopInfoModel.objects.filter(shop_model_hash=model_hash)
    # # # # paging code
    # PAGING_POST_NUMBER = 4
    # print(shop_list)
    # page = request.GET.get('page')
    # paginator = Paginator(shop_list, PAGING_POST_NUMBER)
    # try:
    #     page_object = paginator.page(page)
    # except:
    #     page=1
    #     page_object = paginator.page(page)
    # cont2 = {'shop_list': shop_list,
    #      'page_object': page_object,
    #      'paginator': paginator}
    cont2 = {'shop_list':shop_list} # temp value for no paging
    contexts = combine_dictionary(cont1,cont2)

    return render(request, 'result.html', contexts )

def direction_error(request):
    return HttpResponse('direction error')

def index(request):
    current_latlng = get_current_latlng()
    return render(request, 'result_index.html', current_latlng)

def result(request):
    if request.method not in ['POST','GET']:
        return direction_error(request)

    current_latlng = get_current_latlng()
    current_lat = current_latlng['current_lat']
    current_lng = current_latlng['current_lng']
    #### test code ####
    current_lat = 34.67  #temp value for testing
    current_lng = 135.52  #temp value for testing
    range = 1  # test valeu
    contexts = {'current_lat': current_lat,
                'current_lng': current_lng,
                'range': range}

    if request.method == ['GET']:
        print('get으로 들어올 일이 있나용?')
        shop_show(request, contexts)
    ####################
    try :
        if request.POST['selectCurrentLocationRange']:
            range = request.POST['selectCurrentLocationRange']
            #### test code ####
            current_lat = 34.67 #temp value for testing
            current_lng = 135.52 #temp value for testing
            range = 1 #temp value for testing
            contexts = {'current_lat':current_lat,
                        'current_lng':current_lng,
                        'range':range}
            model_hash = make_hash()
            shop_info = load_shop_info(current_lat,current_lng,range,model_hash)
            model_form_save(shop_info, models.ShopInfoModel)
            shop_show(request, contexts, model_hash)

            #### test code ####
            # contexts = {'current_lat':current_lat,
            #             'current_lng':current_lng,
            #             'range':range}
            return render(request, 'result.html', contexts)
    except:
         pass

    try:
        if request.POST['selectSelectedLocationRange']:
            range = request.POST['selectSelectedLocationRange']
            selected_lat = 34.67 #temp value for testing
            selected_lng = 135.52 #temlp value for testing
            contexts = {'current_lat': current_lat,
                        'current_lng': current_lng,
                        'range': range,
                        'selected_lat':selected_lat,
                        'selected_lng': selected_lng,}
            #### test code ####




            #### test code ####
            return render(request, 'result.html', contexts)

    except:
        return direction_error(request)