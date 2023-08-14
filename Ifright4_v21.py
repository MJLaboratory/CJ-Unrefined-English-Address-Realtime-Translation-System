import re
import string
import requests
from urllib.parse import urlencode, unquote
from korean_romanizer.romanizer import Romanizer
from urllib.parse import urlencode, unquote
import os
# brilliant-scene-392701-53df09bf1204.json 이 토큰 파일 임
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'brilliant-scene-392701-53df09bf1204.json'
from google.cloud import translate_v2 as translate
translate_client = translate.Client()

#from kakaotrans import Translator
#translator = Translator()

import Ifwrong

def func1(txt): 

    # 콤마를 스페이스로 바꾸기
    txt = re.sub(",", " ", txt)

    # 한글 바로 앞에 있으면서, 바로 뒤의 한글이 '번길'이나 '길'이 아닌 경우 해당 숫자 제거
    txt = re.sub(r'\d+(?=[가-힣])(?!번길|길)', '', txt)

    # 특수 문자 바로 앞에 오는 숫자 제거
    txt = re.sub(r'\d+(?=[!@#$%^&*().?":{}|<>])', '', txt)

    # 괄호를 괄호 안에 있는 단어와 함께 제거
    txt = re.sub(r"\([^()]*\)", "", txt)

    # -를 제외한 특수문자 제거
    txt = re.sub(r"[^\w\s-]", "", txt)
    
    
    # 알파벳 바로 뒤에 숫자가 올 경우 알파벳과 숫자 사이에 띄어쓰기(space) 추가
    txt = re.sub(r"([A-Za-z])(\d)", r"\1 \2", txt)

    # 한글 바로 뒤에 알파벳이나 숫자가 붙어있으면 띄어쓰기(space) 추가
    txt = re.sub(r"([ㄱ-ㅎㅏ-ㅣ가-힣])([A-Za-z0-9])", r"\1 \2", txt)

    # -si', '-gu', '-daero', '-ro', '-gil', 'beon-gil' 바로 뒤에 숫자나 영문자가 올 경우 그 사이에 띄어쓰기 추가 
    txt = re.sub(r"(-si|-gu|-daero|-ro|-gil|beon-gil)(\w)", r"\1 \2", txt)
    
    # 숫자 바로 뒤에 B가 오면 띄어쓰기 하기
    txt = re.sub(r"(\d)(B)", r"\1 \2", txt)

    # 'B', 'G', '지하'를 모두 'underground'로 바꿈
    txt = re.sub(r"\b(B|G|지하)\b", "underground", txt)

    # 'underground' 여러번 나오면 첫번째 것만 남김
    txt = re.sub(r"\bunderground\b", lambda match: "underground" if match.start() == txt.index("underground") else "", txt)
    
    return txt






def extract(txt):
    
    mylist = txt.split(' ')

    match = ('-daero', 'daero', 'ro', '-ro', 'gil', '-gil',  '-gu', '-si', 'si','underground', 'beon-gil',  
             '로', '길', '구' , '번길')
    eles = []
    for ele in mylist:
        if ele.endswith(match):
            
            eles.append(ele)
 
        elif ele.replace('-', '').isdigit()== True:
            eles.append(ele)        
    txt2 = ' '.join(eles)
    return txt2


def romanize(text):
    r = Romanizer(text)
    romanized = r.romanize()
    return romanized



#중복 단어 제거
def remove_duplicates(string):
    words = string.split()
    unique_words = []
    for word in words:
        if word not in unique_words:
            unique_words.append(word)
    result = ' '.join(unique_words)
    return result


# Define a function to translate text1 using the translator
#def translate_text(text1):
#    translated = translator.translate(text1, src="en", tgt="kr")
#    # print("translated: ", translated)
#    return translated

##############################################################
##################google translate API##################
def translate_text_google(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    #if isinstance(text, bytes):
    #    text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target, source_language = 'en')

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    #print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result


def translate(txt):
    
   
    trs_txt = translate_text_google(target = 'ko', text = txt)['translatedText']
    trs_txt = re.sub(r'(\d+)호', r'\1', trs_txt)
    trs_txt = re.sub(r'(\d+)년', r'\1', trs_txt)
    trs_txt = re.sub(r'(\d+)층', r'\1', trs_txt)
    trs_txt = re.sub(r'(\d+)번지', r'\1', trs_txt)
    trs_txt = re.sub(r'지하철', '지하', trs_txt)
    return trs_txt
#########################################################



def get_address(addrs):
    # 도로명 주소 검색 API url
    url = "https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=10"
    # 신청 시 발급받은 승인키 
    confirmKey = "U01TX0FVVEgyMDIzMDcxNTE5NDMwNTExMzkzMDk="

    # 웹 요청시 같이 전달될 데이터 = 요청 메시지
    params = {
        'keyword' : unquote(addrs), 
        'confmKey' : unquote(confirmKey),
        'firstSort' : "road",
        'resultType' : 'json'
    }

    # url 링크
    queryURL = url + '&'+  urlencode(params)
    # api 받아오기
    response = requests.get(queryURL)
    

    if response.status_code == 200:
        jsonData = response.json()
        if jsonData['results']['common']['errorCode'] == 0:
            print('errorMessage: ', jsonData['results']['common']['errorMessage'])
        else:
            juso = jsonData['results']['juso']
            if juso :  #'juso' 리스트가 빈 리스트가 아니라면
                # - 처리 : 주소길이 > 1일 경우 buldMnnm 값과 rnMgtSn 값을 기준으로 같으면 첫번째 return, 다르면 rn 값 비교 후 답 없음 return 
                if len(juso)>1:
                    #같은 도로명에 건물번호가 183 과 183-1인 경우 183 리턴 
                    if ((juso[0]["buldMnnm"]==juso[1]["buldMnnm"])&(juso[0]['rnMgtSn']==juso[1]['rnMgtSn'])):
                        roadAddr = juso[0]['roadAddr']
                    # 첫번째 도로명이 두번째 도로명에 포함된 경우 첫번째 도로명 리턴
                    elif (juso[0]["rn"]!=juso[1]["rn"])&(bool(re.search(juso[0]["rn"], juso[1]["rn"]))):
                        roadAddr = juso[0]['roadAddr']
                    else:
                        roadAddr = '답 없음'
                else:
                    roadAddr = juso[0]['roadAddr'] # 목록에서 제일 위에 있는 검색 결과의 도로명 주소를 반환
            else: #'juso' 리스트가 빈 리스트라면
                roadAddr = '답 없음'  # '답 없음'을 반환
            print(roadAddr)
            # print(roadAddr)
            #print(response.text1)
    return roadAddr 


def find_address(text):
    #results = try_every_number(text)
    #results = text.split()
    #addr = str()
    res = re.sub(r'\d+', '', text)
    res2 = res.replace(' ', '').replace('지하', '')   #지하 1822같이 하나의 힌트만 있으면 '답 없음' 처리
    if bool(res2) == False:
        return '답 없음'
    addr = get_address(text)
    
    return addr


def try_every_number(string):
    words = string.split()
    numbers = []
    non_numbers= []
    results = []
    text= ''
    for word in words:
        if word.isdigit() or word.replace('-', '').isdigit():
            numbers.append(word)
        else:
            non_numbers.append(word)
        
        text = ' '.join(non_numbers)
    if numbers:
        for num in numbers:
            text2 = text + ' ' + num
            results.append(text2)
    else:
        results.append(text)
    return results

def find_words(text):
    text_list = text.split()
    lst = []
    for word in text_list:
        if word.endswith('-gu'):
            lst.append(word)
        elif word.endswith('-ro') or word.endswith('-daero'):
            lst.append(word)
        elif word.endswith('-gil') or word.endswith('beon-gil'):
            lst.append(word)
        elif word.endswith('-si'):
            lst.append(word)
        elif word.replace('-', '').isdigit():
            lst.append(word)
        elif word =='underground':
            lst.append(word)
    result = ' '.join(lst)
    return result

def find_address2(text):
    results = try_every_number(text)
    addr = str()
    for res in results:
        res  = translate(res)
        pattern = r'\d+'
        result = re.sub(pattern, '', res)
        res2 = result.replace(' ', '').replace('지하', '')   #지하 1822같이 하나의 힌트만 있으면 '답 없음' 처리
        if bool(res2) == False:
            return '답 없음'
        addr = get_address(res)
        if addr !='답 없음':
            return addr
        else:
            continue
    addr = '답 없음'
    return addr

# z콤마 추가하기
def add_comma(text):
    # -daero, -ro, -gil, -ga, -gu, -si 뒤에 콤마 추가 
    pattern = r'(-daero|-ro|-gil|-gu|-si)(?!\s*,)'
    text = re.sub(pattern, r'\1,', text)
    #숫자 앞에 콤마 추가 
    #pattern = r'(?<=\s)(\d+)'
    #text = re.sub(pattern, r', \1', text)
    # underground 앞에 콤마 추가 
    pattern = r'(?<!,)\b(underground)'
    text = re.sub(pattern, r', \1', text)
    # -gu 로 끝나는 단어 앞에 콤마 추가 
    pattern = r'(\b\w+)-gu\b'
    text = re.sub(pattern, r', \1-gu', text)
    # 숫자 뒤에 콤마 추가하기
    pattern = r'(?<=\s)(\d+)(?=\s)'
    text = re.sub(pattern, r'\1,', text)
    # -daero, -ro, -gil, -ga, -gu, -si 앞에 콤마가 있으면 콤마 삭제하기
    pattern = r',\s*(-daero|-ro|-gil|-gu|-si)'
    text = re.sub(pattern, r'\1', text)

    pattern = r'\b(underground)\b'
    text = re.sub(pattern, r'\1,', text)
    #숫자와 하이픈으로만 이루어진 단어 뒤에 콤마 없으면 추가
    pattern = r'(\b[0-9-]+\b)\s'
    text = re.sub(pattern, r'\1, ', text)

    #알파벳 없이 숫자와 하이픈으로만 이루어진 단어 앞에 콤마 없으면 추가
    #pattern = r'\s(\b[0-9-]+\b)'
    #text = re.sub(pattern, r',\1', text)
    text = re.sub(r'(?<!,)\b\d+-\d+\b',  r', \g<0>', text)
    pattern = r'(?<=\s)(\d+-ro\b)'
    text = re.sub(pattern, r'\1', text)

   
    
    return text


# '로'만 빼 놓기 
def extract_ro(txt):
    input_list = txt.split(',')
    #ro = ''
    for word in input_list:
        if '-ro' in word :
            #ro = word
            return word.replace('Republic of Korea', '')
    for word in input_list:
        if '-daero' in word:
            #ro = word
            return word.replace('Republic of Korea', '')
    for word in input_list:
        if 'ro' in word and 'underground' not in word:
            #ro = word
            return word.replace('Republic of Korea', '')
    for word in input_list:
        if '로' in word:
            #ro = word
            return word
    return ''
    #ro = ro.replace('Republic of Korea', '')
    #return ro
        
#df['로'] = df.apply(lambda x: extract_ro(x['comma_added']), axis=1)
def get_translated_address(text):
    text1 = func1(text)
    text2 = extract(text1)
    text3 = romanize(text2)
    text4 = remove_duplicates(text3)
    text5 = translate(text4)
    text7 = find_address(text5)
    if text7=='답 없음':
        pattern = r'\b\w+-(ro|daero)\b'
        new_text = re.sub(pattern, '', text4)
        new_text = new_text + extract_ro(add_comma(text1))
        text7 = find_address(translate(new_text))
        if text7 == '답 없음':
            text7 = find_address2(find_words(text4))
            if text7 == '답 없음':
                words = text4.split()
                words_without_gu = [word for word in words if not word.endswith("-gu")] 
                result_text = " ".join(words_without_gu)
                text7 = find_address(translate(result_text))
            #text1 = Ifwrong.get_translated_address(text)

    return text7
