import os
import re
import requests

SEHUATANG_HOST = 'www.sehuatang.net'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'


def daysign(cookies: dict) -> bool:
    with requests.get(url=f'https://{SEHUATANG_HOST}/plugin.php',
                      cookies=cookies,
                      params={'id': 'dd_sign', 'mod': 'sign', 'infloat': 'yes', 'handlekey': 'pc_click_ddsign',
                              'inajax': '1', 'ajaxtarget': 'fwin_content_pc_click_ddsign',
                              },
                      headers={
                          'user-agent': DEFAULT_USER_AGENT,
                          'x-requested-with': 'XMLHttpRequest',
                          'accept': '*/*',
                          'sec-ch-ua-mobile': '?0',
                          'sec-ch-ua-platform': 'macOS',
                          'sec-fetch-site': 'same-origin',
                          'sec-fetch-mode': 'cors',
                          'sec-fetch-dest': 'empty',
                          'referer': f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&view=daysign',
                          'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
                      }) as r:
        return r.text


def retrieve_cookies_from_env(env: str) -> dict:
    rawCookies = os.getenv(env, '')
    return dict(i.strip().split('=', maxsplit=1) for i in rawCookies.split(';') if '=' in i)


def retrieve_cookies_from_url(url: str) -> dict:
    with requests.get(url=url, allow_redirects=True) as r:
        return dict(i.strip().split('=', maxsplit=1) for i in r.text.split(';') if '=' in i)


def telegram_send_message(text: str, chat_id: str, token: str):
    with requests.get(url=f'https://api.telegram.org/bot{token}/sendMessage',
                      params={
                          'chat_id': chat_id,
                          'text': text,
                          'parse_mode': 'Markdown',
                      }) as r:
        return r.json()


def main():
    cookies = retrieve_cookies_from_env('COOKIES') or \
        retrieve_cookies_from_url(os.getenv('COOKIES_URL'))
    raw_html = daysign(cookies=cookies)

    try:
        if '签到成功' in raw_html:
            message_text = re.findall(
                r"'(签到成功.+?)'", raw_html, re.MULTILINE)[0]
        elif '已经签到' in raw_html:
            message_text = re.findall(
                r"'(已经签到.+?)'", raw_html, re.MULTILINE)[0]
        else:
            message_text = raw_html
    except IndexError:
        message_text = f'# 98tang Daysign Error\nregex result is empty\n----------\n{raw_html}'
    except Exception as e:
        message_text = f'# 98tang Daysign Error\n{e}\n----------\n{raw_html}'

    # log to output
    print(message_text)

    # telegram notify
    chat_id = os.getenv('CHAT_ID')
    bot_token = os.getenv('BOT_TOKEN')
    if chat_id and bot_token:
        telegram_send_message(message_text, chat_id, bot_token)


if __name__ == '__main__':
    main()