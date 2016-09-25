# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests,json
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.exceptions import OfficialAPIError
from wechat_sdk.messages import TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, \
    EventMessage
from weixin.settings import BASE_DIR #,WECHAT_TOKEN,WEIXIN_APPID,WEIXIN_APPSECRET
from django.shortcuts import render_to_response
from django.template import Template, Context

WECHAT_TOKEN='welion'
WEIXIN_APPID = 'wx2dab89f15b53d205'
WEIXIN_APPSECRET = 'ae9c16f80dd384f2f9dabf2a1f901294'

wechat_instance = WechatBasic(
    token=WECHAT_TOKEN,
    appid=WEIXIN_APPID,
    appsecret=WEIXIN_APPSECRET
)


JUHE_ROBOT='http://op.juhe.cn/robot/index'
JUHE_KEY='2bd51d619a0b0b44868dc71a8036da39'

@csrf_exempt
def wechat(request):
    if request.method == 'GET':
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        if not wechat_instance.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')

        return HttpResponse(
            request.GET.get('echostr', ''), content_type="text/plain")

    # 解析本次请求的 XML 数据
    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')

    # 获取解析好的微信请求信息
    message = wechat_instance.get_message()

    if isinstance(message, TextMessage):
        # 当前会话内容
        img_dir = []
        static_dir = os.path.join(BASE_DIR,'../static')
        for item in os.listdir(static_dir):
            if os.path.isdir(os.path.join(static_dir,item)):
                img_dir.append(item)

        content = message.content.strip()
        if content == '博客' or content == 'blog' or content == '最新':
            reply_text = (
                '有狗毛的博客可以看啊！'
            )
            response = wechat_instance.response_text(content=reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '功能':
            reply_text = (
                '回复“最新”或“博客”或“blog”，获取最新博客内容\n' +
                '回复任意关键字，获取感兴趣内容，如“django”\n' +
                '更多功能，敬请期待'
            )
            response = wechat_instance.response_text(content=reply_text)
            return HttpResponse(response, content_type="application/xml")
#        if content == 'pic':
#            content = wechat_instance.response_text(content="http://zhongwanhua.cn/pic")
#            return HttpResponse(content, content_type="application/xml")
#        if content == 'lilisha':
#            content = wechat_instance.response_text(content="http://zhongwanhua.cn/tumblr/lilisha")
#            return HttpResponse(content, content_type="application/xml")
#        if content == 'subin':
#            content = wechat_instance.response_text(content="http://zhongwanhua.cn/tumblr/subin")
#            return HttpResponse(content, content_type="application/xml")
#        if content == 'ailili':
#            content = wechat_instance.response_text(content="http://zhongwanhua.cn/tumblr/ailili")
#            return HttpResponse(content, content_type="application/xml")
#        if content == 'hbo':
#            content = wechat_instance.response_text(content="http://zhongwanhua.cn/tumblr/hbo")
#            return HttpResponse(content, content_type="application/xml")
        if content in img_dir:
            path_content = "http://zhongwanhua.cn/tumblr/" + str(content)
            content = wechat_instance.response_text(content=path_content)
            return HttpResponse(content, content_type="application/xml")
        if content:
            keyword = content
            params = {
                "key":"2bd51d619a0b0b44868dc71a8036da39",
                "info":keyword,
                "dtype":"json",
                "loc":"上海浦东",
                "lon":"121550000",
                "lat":"31220000",
                "userid":"1"}
            try:
                resp = requests.get(JUHE_ROBOT,params=params).content
                result = json.loads(resp)['result']
                keyword = result['text']
                print result
            except :
                print "Get juhe error"
                

            content = wechat_instance.response_text(content=keyword)
            return HttpResponse(content, content_type="application/xml")


    elif isinstance(message, VoiceMessage):
        reply_text = '语音信息我听不懂/:P-(/:P-(/:P-('
    elif isinstance(message, ImageMessage):
        reply_text = '图片信息我也看不懂/:P-(/:P-(/:P-('
    elif isinstance(message, VideoMessage):
        reply_text = '视频我不会看/:P-('
    elif isinstance(message, LinkMessage):
        reply_text = '链接信息'
    elif isinstance(message, LocationMessage):
        reply_text = '地理位置信息'
    elif isinstance(message, EventMessage):
        if message.type == 'subscribe':
            reply_text = '感谢您的到来!回复“功能”返回使用指南'
        elif message.type == 'unsubscribe':
            reply_text = '取消关注事件'
        elif message.type == 'scan':
            reply_text = '已关注用户扫描二维码！'
        elif message.type == 'location':
            reply_text = '上报地理位置'
        elif message.type == 'click':
            reply_text = '自定义菜单点击'
        elif message.type == 'view':
            reply_text = '自定义菜单跳转链接'
        elif message.type == 'templatesendjobfinish':
            reply_text = '模板消息'
    else:
        reply_text = '功能还没有实现'

    response = wechat_instance.response_text(content=reply_text)
    return HttpResponse(response, content_type="application/xml")

def pic(request):
    
    pic_name = os.listdir(BASE_DIR + '/../static/subin/')
    pic_url=[]
    for i in pic_name:
        pic_url.append("/static/subin/" + i)
    #print pic_url    
    temp = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Girls</title>
</head>
<body>
<ul>
    {% for u in url %}
        <p></p>
        <img src="{{ u }}">{{u}}</img>
        <p></p>
    {% endfor %}
</ul>
</body>
</html>
"""
    t = Template(temp)
    html = t.render(Context({"url":pic_url}))
    return HttpResponse(html)

def index(request):
    temp = """<script type="text/javascript" src="http://ip.chinaz.com/getip.aspx"></script>"""
    return HttpResponse(temp)

def tumblr(request,name):
    
    pic_name = os.listdir(BASE_DIR + '/../static/' + name +'/')
    pic_url=[]
    for i in pic_name:
        pic_url.append("/static/" + name  + "/" + i)
    temp = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Girls</title>
</head>
<body>
<ul>
    {% for u in url %}
        <p></p>
        <img src="{{ u }}">{{u}}</img>
        <p></p>
    {% endfor %}
</ul>
</body>
</html>
"""
    t =Template(temp)
    html = t.render(Context({"url":pic_url}))
    return HttpResponse(html)
