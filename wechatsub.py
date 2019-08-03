# -*- coding: utf-8 -*-
from selenium import webdriver
import webbrowser
import time
import json
import requests
import re
import random

# 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中

# 微信公众号账号
user = "2869928788@qq.com"
# 公众号密码
password = "anton826"
# 设置要爬取的公众号列表
gzlist = []
gzlist.append(input("设置要爬取的公中号:"))

def weChat_login():
    # 定义一个空的字典，存放cookies内容
    post = {}

    # 用webdriver启动谷歌浏览器
    print("启动浏览器，打开微信公众号登录界面")
    driver = webdriver.Chrome()
    # 打开微信公众号登录页面
    driver.get('https://mp.weixin.qq.com/')
    # 等待5秒钟
    time.sleep(1)
    print("正在输入微信公众号登录账号和密码......")
    # 清空账号框中的内容
    driver.find_element_by_xpath("./*//input[@name='account']").clear()
    # 自动填入登录用户名
    driver.find_element_by_xpath("./*//input[@name='account']").send_keys(user)
    # 清空密码框中的内容
    driver.find_element_by_xpath("./*//input[@name='password']").clear()
    # 自动填入登录密码
    driver.find_element_by_xpath("./*//input[@name='password']").send_keys(password)

    # 在自动输完密码之后需要手动点一下记住我
    print("请在登录界面点击:记住账号")
    time.sleep(2)
    # 自动点击登录按钮进行登录
    driver.find_element_by_xpath("./*//a[@class='btn_login']").click()
    # 拿手机扫二维码！
    print("请拿手机扫码二维码登录公众号")
    time.sleep(10)
    print("登录成功")
    # 重新载入公众号登录页，登录之后会显示公众号后台首页，从这个返回内容中获取cookies信息
    driver.get('https://mp.weixin.qq.com/')
    # 获取cookies
    cookie_items = driver.get_cookies()

    # 获取到的cookies是列表形式，将cookies转成json形式并存入本地名为cookie的文本中
    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post)
    with open('cookie.txt', 'w+', encoding='utf-8') as f:
        f.write(cookie_str)
    print("cookies信息已保存到本地")

# 爬取微信公众号文章，并存在本地文本中


def get_content(query):
    # query为要爬取的公众号名称
    # 公众号主页
    url = 'https://mp.weixin.qq.com'
    # 设置headers
    header = {
        "HOST": "mp.weixin.qq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }

    # 读取上一步获取到的cookies
    with open('cookie.txt', 'r', encoding='utf-8') as f:
        cookie = f.read()
    cookies = json.loads(cookie)

    # 登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1849751598，从这里获取token信息
    response = requests.get(url=url, cookies=cookies)
    token = re.findall(r'token=(\d+)', str(response.url))[0]

    # 搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    # 搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
    query_id = {
        'action': 'search_biz',
        'token' : token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5'
        }
    # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = requests.get(search_url, cookies=cookies, headers=header, params=query_id)
    # 取搜索结果中的第一个公众号
    lists = search_response.json().get('list')[0]
    # 获取这个公众号的fakeid，后面爬取公众号文章需要此字段
    fakeid = lists.get('fakeid')
    runtime = time.strftime('%Y-%m-%d', time.localtime())
    thead = "<th>微信公众号：&emsp;&emsp;&emsp;&emsp;微信号：%s&emsp;&emsp&emsp;&emsp;更新日期：%s</th>" % (gzlist[0], runtime)
    # 微信公众号文章接口地址
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    # 搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
    query_id_data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '0',# 不同页，此参数变化，变化规则为每页加5
        'count': '5',
        'query': '',
        'fakeid': fakeid,
        'type': '9'
        }
    # 打开搜索的微信公众号文章列表页
    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
    # 获取文章总数
    max_num = appmsg_response.json().get('app_msg_cnt')
    # 每页至少有5条，获取文章总的页数，爬取时需要分页爬
    num = int(int(max_num) / 5)
    # 起始页begin参数，往后每页加5
    begin = 0
    # 文章起始编号
    article_num = 1
    tbody = []
    while num + 1 > 0 :
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '{}'.format(str(begin)),
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
            }
        print('正在翻页：--------------',begin)

        # 获取每一页文章的标题和链接地址，并写入本地文本中
        query_fakeid_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
        fakeid_list = query_fakeid_response.json().get('app_msg_list')
        for item in fakeid_list:
            # 文章链接
            content_link=item.get('link')
            # 文章标题
            content_title=item.get('title')
            # 写入文章标题和文章链接
            tbody.append("<tr><td>" + str(article_num) + "&emsp;&emsp;<a href = '"+ content_link + "'>"+ content_title + "</a></td></tr>")
            article_num += 1
        num -= 1
        begin = int(begin)
        begin+=5
        time.sleep(2)
    print(thead)
    print("".join(tbody))
    # 命名生成的html
    GEN_HTML = "test.html"
    # 打开文件，准备写入
    f = open(GEN_HTML, 'w', encoding="utf-8")
    template = """
    <!doctype html>
    <html>
    <head>
    <meta charset='UTF-8'><meta name='viewport' content='width=device-width initial-scale=1'>
    <title></title><link href='https://fonts.loli.net/css?family=Open+Sans:400italic,700italic,700,400&subset=latin,latin-ext' rel='stylesheet' type='text/css' /><style type='text/css'>html {overflow-x: initial !important;}:root { --bg-color:#ffffff; --text-color:#333333; --select-text-bg-color:#B5D6FC; --select-text-font-color:auto; --monospace:"Lucida Console",Consolas,"Courier",monospace; }
    html { font-size: 14px; background-color: var(--bg-color); color: var(--text-color); font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
    body { margin: 0px; padding: 0px; height: auto; bottom: 0px; top: 0px; left: 0px; right: 0px; font-size: 1rem; line-height: 1.42857; overflow-x: hidden; background: inherit; tab-size: 4; }
    iframe { margin: auto; }
    a.url { word-break: break-all; }
    a:active, a:hover { outline: 0px; }
    .in-text-selection, ::selection { text-shadow: none; background: var(--select-text-bg-color); color: var(--select-text-font-color); }
    #write { margin: 0px auto; height: auto; width: inherit; word-break: normal; word-wrap: break-word; position: relative; white-space: normal; overflow-x: visible; padding-top: 40px; }
    #write.first-line-indent p { text-indent: 2em; }
    #write.first-line-indent li p, #write.first-line-indent p * { text-indent: 0px; }
    #write.first-line-indent li { margin-left: 2em; }
    .for-image #write { padding-left: 8px; padding-right: 8px; }
    body.typora-export { padding-left: 30px; padding-right: 30px; }
    .typora-export .footnote-line, .typora-export li, .typora-export p { white-space: pre-wrap; }
    @media screen and (max-width: 500px) {
      body.typora-export { padding-left: 0px; padding-right: 0px; }
      #write { padding-left: 20px; padding-right: 20px; }
      .CodeMirror-sizer { margin-left: 0px !important; }
      .CodeMirror-gutters { display: none !important; }
    }
    #write li > figure:first-child { margin-top: -20px; }
    #write ol, #write ul { position: relative; }
    img { max-width: 100%; vertical-align: middle; }
    button, input, select, textarea { color: inherit; font-style: inherit; font-variant: inherit; font-weight: inherit; font-stretch: inherit; font-size: inherit; line-height: inherit; font-family: inherit; }
    input[type="checkbox"], input[type="radio"] { line-height: normal; padding: 0px; }
    *, ::after, ::before { box-sizing: border-box; }
    #write h1, #write h2, #write h3, #write h4, #write h5, #write h6, #write p, #write pre { width: inherit; }
    #write h1, #write h2, #write h3, #write h4, #write h5, #write h6, #write p { position: relative; }
    h1, h2, h3, h4, h5, h6 { break-after: avoid-page; break-inside: avoid; orphans: 2; }
    p { orphans: 4; }
    h1 { font-size: 2rem; }
    h2 { font-size: 1.8rem; }
    h3 { font-size: 1.6rem; }
    h4 { font-size: 1.4rem; }
    h5 { font-size: 1.2rem; }
    h6 { font-size: 1rem; }
    .md-math-block, .md-rawblock, h1, h2, h3, h4, h5, h6, p { margin-top: 1rem; margin-bottom: 1rem; }
    .hidden { display: none; }
    .md-blockmeta { color: rgb(204, 204, 204); font-weight: 700; font-style: italic; }
    a { cursor: pointer; }
    sup.md-footnote { padding: 2px 4px; background-color: rgba(238, 238, 238, 0.7); color: rgb(85, 85, 85); border-radius: 4px; cursor: pointer; }
    sup.md-footnote a, sup.md-footnote a:hover { color: inherit; text-transform: inherit; text-decoration: inherit; }
    #write input[type="checkbox"] { cursor: pointer; width: inherit; height: inherit; }
    figure { overflow-x: auto; margin: 1.2em 0px; max-width: calc(100% + 16px); padding: 0px; }
    figure > table { margin: 0px !important; }
    tr { break-inside: avoid; break-after: auto; }
    thead { display: table-header-group; }
    table { border-collapse: collapse; border-spacing: 0px; width: 100%; overflow: auto; break-inside: auto; text-align: left; }
    table.md-table td { min-width: 32px; }
    .CodeMirror-gutters { border-right: 0px; background-color: inherit; }
    .CodeMirror-linenumber { user-select: none; }
    .CodeMirror { text-align: left; }
    .CodeMirror-placeholder { opacity: 0.3; }
    .CodeMirror pre { padding: 0px 4px; }
    .CodeMirror-lines { padding: 0px; }
    div.hr:focus { cursor: none; }
    #write pre { white-space: pre-wrap; }
    #write.fences-no-line-wrapping pre { white-space: pre; }
    #write pre.ty-contain-cm { white-space: normal; }
    .CodeMirror-gutters { margin-right: 4px; }
    .md-fences { font-size: 0.9rem; display: block; break-inside: avoid; text-align: left; overflow: visible; white-space: pre; background: inherit; position: relative !important; }
    .md-diagram-panel { width: 100%; margin-top: 10px; text-align: center; padding-top: 0px; padding-bottom: 8px; overflow-x: auto; }
    #write .md-fences.mock-cm { white-space: pre-wrap; }
    .md-fences.md-fences-with-lineno { padding-left: 0px; }
    #write.fences-no-line-wrapping .md-fences.mock-cm { white-space: pre; overflow-x: auto; }
    .md-fences.mock-cm.md-fences-with-lineno { padding-left: 8px; }
    .CodeMirror-line, twitterwidget { break-inside: avoid; }
    .footnotes { opacity: 0.8; font-size: 0.9rem; margin-top: 1em; margin-bottom: 1em; }
    .footnotes + .footnotes { margin-top: 0px; }
    .md-reset { margin: 0px; padding: 0px; border: 0px; outline: 0px; vertical-align: top; background: 0px 0px; text-decoration: none; text-shadow: none; float: none; position: static; width: auto; height: auto; white-space: nowrap; cursor: inherit; -webkit-tap-highlight-color: transparent; line-height: normal; font-weight: 400; text-align: left; box-sizing: content-box; direction: ltr; }
    li div { padding-top: 0px; }
    blockquote { margin: 1rem 0px; }
    li .mathjax-block, li p { margin: 0.5rem 0px; }
    li { margin: 0px; position: relative; }
    blockquote > :last-child { margin-bottom: 0px; }
    blockquote > :first-child, li > :first-child { margin-top: 0px; }
    .footnotes-area { color: rgb(136, 136, 136); margin-top: 0.714rem; padding-bottom: 0.143rem; white-space: normal; }
    #write .footnote-line { white-space: pre-wrap; }
    @media print {
      body, html { border: 1px solid transparent; height: 99%; break-after: avoid; break-before: avoid; }
      #write { margin-top: 0px; padding-top: 0px; border-color: transparent !important; }
      .typora-export * { -webkit-print-color-adjust: exact; }
      html.blink-to-pdf { font-size: 13px; }
      .typora-export #write { padding-left: 32px; padding-right: 32px; padding-bottom: 0px; break-after: avoid; }
      .typora-export #write::after { height: 0px; }
      @page { margin: 20mm 0px; }
    }
    .footnote-line { margin-top: 0.714em; font-size: 0.7em; }
    a img, img a { cursor: pointer; }
    pre.md-meta-block { font-size: 0.8rem; min-height: 0.8rem; white-space: pre-wrap; background: rgb(204, 204, 204); display: block; overflow-x: hidden; }
    p > .md-image:only-child:not(.md-img-error) img, p > img:only-child { display: block; margin: auto; }
    p > .md-image:only-child { display: inline-block; width: 100%; }
    #write .MathJax_Display { margin: 0.8em 0px 0px; }
    .md-math-block { width: 100%; }
    .md-math-block:not(:empty)::after { display: none; }
    [contenteditable="true"]:active, [contenteditable="true"]:focus { outline: 0px; box-shadow: none; }
    .md-task-list-item { position: relative; list-style-type: none; }
    .task-list-item.md-task-list-item { padding-left: 0px; }
    .md-task-list-item > input { position: absolute; top: 0px; left: 0px; margin-left: -1.2em; margin-top: calc(1em - 10px); border: none; }
    .math { font-size: 1rem; }
    .md-toc { min-height: 3.58rem; position: relative; font-size: 0.9rem; border-radius: 10px; }
    .md-toc-content { position: relative; margin-left: 0px; }
    .md-toc-content::after, .md-toc::after { display: none; }
    .md-toc-item { display: block; color: rgb(65, 131, 196); }
    .md-toc-item a { text-decoration: none; }
    .md-toc-inner:hover { text-decoration: underline; }
    .md-toc-inner { display: inline-block; cursor: pointer; }
    .md-toc-h1 .md-toc-inner { margin-left: 0px; font-weight: 700; }
    .md-toc-h2 .md-toc-inner { margin-left: 2em; }
    .md-toc-h3 .md-toc-inner { margin-left: 4em; }
    .md-toc-h4 .md-toc-inner { margin-left: 6em; }
    .md-toc-h5 .md-toc-inner { margin-left: 8em; }
    .md-toc-h6 .md-toc-inner { margin-left: 10em; }
    @media screen and (max-width: 48em) {
      .md-toc-h3 .md-toc-inner { margin-left: 3.5em; }
      .md-toc-h4 .md-toc-inner { margin-left: 5em; }
      .md-toc-h5 .md-toc-inner { margin-left: 6.5em; }
      .md-toc-h6 .md-toc-inner { margin-left: 8em; }
    }
    a.md-toc-inner { font-size: inherit; font-style: inherit; font-weight: inherit; line-height: inherit; }
    .footnote-line a:not(.reversefootnote) { color: inherit; }
    .md-attr { display: none; }
    .md-fn-count::after { content: "."; }
    code, pre, samp, tt { font-family: var(--monospace); }
    kbd { margin: 0px 0.1em; padding: 0.1em 0.6em; font-size: 0.8em; color: rgb(36, 39, 41); background: rgb(255, 255, 255); border: 1px solid rgb(173, 179, 185); border-radius: 3px; box-shadow: rgba(12, 13, 14, 0.2) 0px 1px 0px, rgb(255, 255, 255) 0px 0px 0px 2px inset; white-space: nowrap; vertical-align: middle; }
    .md-comment { color: rgb(162, 127, 3); opacity: 0.8; font-family: var(--monospace); }
    code { text-align: left; vertical-align: initial; }
    a.md-print-anchor { white-space: pre !important; border-width: initial !important; border-style: none !important; border-color: initial !important; display: inline-block !important; position: absolute !important; width: 1px !important; right: 0px !important; outline: 0px !important; background: 0px 0px !important; text-decoration: initial !important; text-shadow: initial !important; }
    .md-inline-math .MathJax_SVG .noError { display: none !important; }
    .html-for-mac .inline-math-svg .MathJax_SVG { vertical-align: 0.2px; }
    .md-math-block .MathJax_SVG_Display { text-align: center; margin: 0px; position: relative; text-indent: 0px; max-width: none; max-height: none; min-height: 0px; min-width: 100%; width: auto; overflow-y: hidden; display: block !important; }
    .MathJax_SVG_Display, .md-inline-math .MathJax_SVG_Display { width: auto; margin: inherit; display: inline-block !important; }
    .MathJax_SVG .MJX-monospace { font-family: var(--monospace); }
    .MathJax_SVG .MJX-sans-serif { font-family: sans-serif; }
    .MathJax_SVG { display: inline; font-style: normal; font-weight: 400; line-height: normal; zoom: 90%; text-indent: 0px; text-align: left; text-transform: none; letter-spacing: normal; word-spacing: normal; word-wrap: normal; white-space: nowrap; float: none; direction: ltr; max-width: none; max-height: none; min-width: 0px; min-height: 0px; border: 0px; padding: 0px; margin: 0px; }
    .MathJax_SVG * { transition: none; }
    .MathJax_SVG_Display svg { vertical-align: middle !important; margin-bottom: 0px !important; }
    .os-windows.monocolor-emoji .md-emoji { font-family: "Segoe UI Symbol", sans-serif; }
    .md-diagram-panel > svg { max-width: 100%; }
    [lang="mermaid"] svg, [lang="flow"] svg { max-width: 100%; }
    [lang="mermaid"] .node text { font-size: 1rem; }
    table tr th { border-bottom: 0px; }
    video { max-width: 100%; display: block; margin: 0px auto; }
    iframe { max-width: 100%; width: 100%; border: none; }
    .highlight td, .highlight tr { border: 0px; }
    :root { --side-bar-bg-color: #fafafa; --control-text-color: #777; }
    html { font-size: 16px; }
    body { font-family: "Open Sans", "Clear Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; color: rgb(51, 51, 51); line-height: 1.6; }
    #write { max-width: 860px; margin: 0px auto; padding: 30px 30px 100px; }
    #write > ul:first-child, #write > ol:first-child { margin-top: 30px; }
    a { color: rgb(65, 131, 196); }
    h1, h2, h3, h4, h5, h6 { position: relative; margin-top: 1rem; margin-bottom: 1rem; font-weight: bold; line-height: 1.4; cursor: text; }
    h1:hover a.anchor, h2:hover a.anchor, h3:hover a.anchor, h4:hover a.anchor, h5:hover a.anchor, h6:hover a.anchor { text-decoration: none; }
    h1 tt, h1 code { font-size: inherit; }
    h2 tt, h2 code { font-size: inherit; }
    h3 tt, h3 code { font-size: inherit; }
    h4 tt, h4 code { font-size: inherit; }
    h5 tt, h5 code { font-size: inherit; }
    h6 tt, h6 code { font-size: inherit; }
    h1 { padding-bottom: 0.3em; font-size: 2.25em; line-height: 1.2; border-bottom: 1px solid rgb(238, 238, 238); }
    h2 { padding-bottom: 0.3em; font-size: 1.75em; line-height: 1.225; border-bottom: 1px solid rgb(238, 238, 238); }
    h3 { font-size: 1.5em; line-height: 1.43; }
    h4 { font-size: 1.25em; }
    h5 { font-size: 1em; }
    h6 { font-size: 1em; color: rgb(119, 119, 119); }
    p, blockquote, ul, ol, dl, table { margin: 0.8em 0px; }
    li > ol, li > ul { margin: 0px; }
    hr { height: 2px; padding: 0px; margin: 16px 0px; background-color: rgb(231, 231, 231); border: 0px none; overflow: hidden; box-sizing: content-box; }
    li p.first { display: inline-block; }
    ul, ol { padding-left: 30px; }
    ul:first-child, ol:first-child { margin-top: 0px; }
    ul:last-child, ol:last-child { margin-bottom: 0px; }
    blockquote { border-left: 4px solid rgb(223, 226, 229); padding: 0px 15px; color: rgb(119, 119, 119); }
    blockquote blockquote { padding-right: 0px; }
    table { padding: 0px; word-break: initial; }
    table tr { border-top: 1px solid rgb(223, 226, 229); margin: 0px; padding: 0px; }
    table tr:nth-child(2n), thead { background-color: rgb(248, 248, 248); }
    table tr th { font-weight: bold; border-width: 1px 1px 0px; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: rgb(223, 226, 229); border-right-color: rgb(223, 226, 229); border-left-color: rgb(223, 226, 229); border-image: initial; border-bottom-style: initial; border-bottom-color: initial; text-align: left; margin: 0px; padding: 6px 13px; }
    table tr td { border: 1px solid rgb(223, 226, 229); text-align: left; margin: 0px; padding: 6px 13px; }
    table tr th:first-child, table tr td:first-child { margin-top: 0px; }
    table tr th:last-child, table tr td:last-child { margin-bottom: 0px; }
    .CodeMirror-lines { padding-left: 4px; }
    .code-tooltip { box-shadow: rgba(0, 28, 36, 0.3) 0px 1px 1px 0px; border-top: 1px solid rgb(238, 242, 242); }
    .md-fences, code, tt { border: 1px solid rgb(231, 234, 237); background-color: rgb(248, 248, 248); border-radius: 3px; padding: 2px 4px 0px; font-size: 0.9em; }
    code { background-color: rgb(243, 244, 244); padding: 0px 2px; }
    .md-fences { margin-bottom: 15px; margin-top: 15px; padding-top: 8px; padding-bottom: 6px; }
    .md-task-list-item > input { margin-left: -1.3em; }
    @media print {
      html { font-size: 13px; }
      table, pre { break-inside: avoid; }
      pre { word-wrap: break-word; }
    }
    .md-fences { background-color: rgb(248, 248, 248); }
    #write pre.md-meta-block { padding: 1rem; font-size: 85%; line-height: 1.45; background-color: rgb(247, 247, 247); border: 0px; border-radius: 3px; color: rgb(119, 119, 119); margin-top: 0px !important; }
    .mathjax-block > .code-tooltip { bottom: 0.375rem; }
    .md-mathjax-midline { background: rgb(250, 250, 250); }
    #write > h3.md-focus::before { left: -1.5625rem; top: 0.375rem; }
    #write > h4.md-focus::before { left: -1.5625rem; top: 0.285714rem; }
    #write > h5.md-focus::before { left: -1.5625rem; top: 0.285714rem; }
    #write > h6.md-focus::before { left: -1.5625rem; top: 0.285714rem; }
    .md-image > .md-meta { border-radius: 3px; padding: 2px 0px 0px 4px; font-size: 0.9em; color: inherit; }
    .md-tag { color: rgb(167, 167, 167); opacity: 1; }
    .md-toc { margin-top: 20px; padding-bottom: 20px; }
    .sidebar-tabs { border-bottom: none; }
    #typora-quick-open { border: 1px solid rgb(221, 221, 221); background-color: rgb(248, 248, 248); }
    #typora-quick-open-item { background-color: rgb(250, 250, 250); border-color: rgb(254, 254, 254) rgb(229, 229, 229) rgb(229, 229, 229) rgb(238, 238, 238); border-style: solid; border-width: 1px; }
    .on-focus-mode blockquote { border-left-color: rgba(85, 85, 85, 0.12); }
    header, .context-menu, .megamenu-content, footer { font-family: "Segoe UI", Arial, sans-serif; }
    .file-node-content:hover .file-node-icon, .file-node-content:hover .file-node-open-state { visibility: visible; }
    .mac-seamless-mode #typora-sidebar { background-color: var(--side-bar-bg-color); }
    .md-lang { color: rgb(180, 101, 77); }
    .html-for-mac .context-menu { --item-hover-bg-color: #E6F0FE; }
    #md-notification .btn { border: 0px; }
    .dropdown-menu .divider { border-color: rgb(229, 229, 229); }
     .typora-export li, .typora-export p, .typora-export,  .footnote-line {white-space: normal;} 
    </style>
    </head>
    <body class='typora-export os-windows' >
    <div  id='write'  class = 'is-node'>
    <figure>
    <table>
    <thead><tr>""" + thead + "</tr></thead><tbody>" + "".join(tbody) + "</tbody></html>"
    # 写入文件
    f.write(template)
    # 关闭文件
    f.close()
    webbrowser.open(GEN_HTML, new=1)

if __name__ == '__main__':
    try:
        # 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
        weChat_login()
        # 登录之后，通过微信公众号后台提供的微信公众号文章接口爬取文章
        for query in gzlist:
            # 爬取微信公众号文章，并存在本地文本中
            print("开始爬取公众号："+query)
            get_content(query)
            print("爬取完成")
    except Exception as e:
        print(str(e))
