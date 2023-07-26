import cv2
import imutils
import math
import easyocr
import openai
from django.conf import settings
openai.api_key = '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'
def get_orientation(p1,p2,p3,p4):

    x1  = p1[0]
    y1  = p1[1]
    x2  = p2[0]
    y2  = p2[1]
    x4  = p4[0]
    y4  = p4[1]   
    d1 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
    d2 = (x4 - x1) * (x4 - x1) + (y4 - y1) * (y4 - y1)
    if d2 > d1:
        x2 = x4
        y2 = y4
    angle = 180 / math.pi * math.atan((y2 - y1)/(x2 - x1))
    return angle
def choose_correct_word_by_AI(word1, word2):
    # print(word1)
    # print(word2)
    word1 = word1.lower()
    word2 = word2.lower()
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": f"Please select  english word that spell is correct. The words are '{word1}' and '{word2}'.  If word is in 'ly' or 's' it is true."}
        ]
    )
    if word1 in response.choices[0].message['content'].lower():
        return word1
    else:
        return word2
def complete_correct_sentence(str):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": f"Please correct word's order for right string from this - '{str}'. some word's order is changed so you should make new sentence by changing word's order. new sentence must be reliable and logical.  Don't add new word anymore"}
        ]
    )
    return   response.choices[0].message['content']
def extract_string_from_image(image):
    reader = easyocr.Reader(['en'])

    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 200, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []
    words_rect = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4 :
            x, y, w, h = cv2.boundingRect(approx)
            if w > 50 and h > 50:
                rectangles.append(approx)
                roi = image[y:y+h, x:x+w]
                words_rect.append(roi)
    index = 0
    output = ''
    for rect in rectangles:
        angle = get_orientation(rect[0][0],rect[1][0],rect[2][0],rect[3][0])
        rotated = imutils.rotate_bound(words_rect[index], angle = -angle)
        rotated_2 = imutils.rotate_bound(words_rect[index], angle = 180-angle)
        index = index + 1        
        result = reader.readtext(rotated)
        result_2 = reader.readtext(rotated_2)
        if len(result) == 0 or len(result_2) == 0:
            continue
        str_imd = choose_correct_word_by_AI(result[0][1],result_2[0][1])
        # print(result[0][1] + ' : ' + result_2[0][1] + ' -> ' + str_imd)
        output = output + ' ' +  str_imd
    return complete_correct_sentence(output)
    
    # cv2.drawContours(image, rectangles, -1, (0,255,0), 3)
    # cv2.imshow('Result',image)
    # cv2.waitKey(0)    
def generate_AI_image(path):
    # media_file_url = settings.MEDIA_ROOT + '\\upload\\' + path
    # image = cv2.imread(media_file_url)
    try:
        # result = extract_string_from_image(image)
        # print(result)
        result = 'The engineering wizard is a systematic design efficiency.'
        response = openai.Image.create(
        prompt='fantastic and amazing image. topic is "'+ result +'"',
        n=1,
        size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except:
        return 'File Format Error'