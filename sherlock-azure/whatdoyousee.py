import json
import requests

vision_api_key = 'a5a3c94b1dee4faa8047873e73e5e642'
vision_api_url = 'https://chinaeast2.api.cognitive.azure.cn/vision/v2.0/analyze'

def WhatDoYouSee(body):
    image = '~/sherlock-azure/faces/Detection_%s.png' %(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(image, 'wb') as f:
        f.write(camera.get_frame())
        f.close()
    headers = {
#         'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': vision_api_key,
    }
     
    params = {
        'visualFeatures': 'Description, Faces',
        'details': '',
        'language': 'en',
    }
    data = {'url': image}

    try:
        api_url = vision_api_url 
        response = requests.post(api_url, headers=headers, json=data, params=params)
        print ('Respose:')
        parsed = json.loads(response.text)
        if len(parsed) == 0:
            parsedText = 'I see nothing'
        else:
            tag_str = ''
            for num_tags in range(5):
                tag_str += parsed['description']['tags'][num_tags] + ', '
            parsedText = 'I see %s. Top 5 tags are: %s' % (parsed['description']['captions'][0]['text'], tag_str)
        print(parsedText)
        print(json.dumps(parsed, sort_keys=True, indent=2))
    except Exception as e:
        print('Error:')
        print(e)
        parsedText = e

    return parsedText
