import requests
import requests_cache
import json
import decimal



# setup api cache location (makes temp sql lite database for storage for api calls)

requests_cache.install_cache('image_cache', backend='sqlite')

def get_image(search):
    
    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q":search,"gl":"us","lr":"lang_en","num":"10","start":"0"}

    headers = {
        "X-RapidAPI-Key": "d37d52df47mshe15ee7955c96fb4p1dc3c7jsne2dc9ccc4a9b",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    img_url=""

    if 'items' in data.keys():
        img_url = data['items'][0]['originalImageUrl']

    return img_url

class json_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder(json_encoder,self.default(obj))