import requests
import datetime
import dateparser
import time
import simplejson as json
from splash.har.utils import get_response_body_bytes

try:
    from cookielib import Cookie, CookieJar  # Python 2
except ImportError:
    from http.cookiejar import Cookie, CookieJar  # Python 3

lua_script = """
treat = require("treat")
base64 = require("base64")
function main(splash, args)
  splash:set_viewport_full()
  splash.images_enabled = false
  splash.plugins_enabled = false
  splash.response_body_enabled = false
  if args.cookies ~= nil then
    print('Cookies.....')
    print(args.cookies)
    splash:init_cookies(args.cookies)
  end

  splash:go{
    args.url,
    headers=args.headers,
    http_method=args.http_method
    }
  assert(splash:wait(10))

  local entries = splash:history()
  print('--Entries--')
  print(entries)
  print(#entries)
  if entries ~= nil then
    local last_response = entries[#entries].response
    return {
        url = splash:url(),
        headers = last_response.headers,
        http_status = last_response.status,
        cookies = splash:get_cookies(),
    }

  end
end
"""

headers = requests.utils.default_headers()

headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Connection': 'keep-alive'
})
data_for_spash = {
    'url': 'http://www.parliament.gov.sg/docs/default-source/default-document-library/co-operative-societies-(amendment)-bill-50-2017.pdf?sfvrsn=0',
    'wait': 5, 'headers': dict(headers), 'http_method': 'GET', 'response_body': 1, 'html': 1, 'lua_source': lua_script}

header_for_splash = {'Content-Type': 'application/json'}
resp = requests.post('http://192.168.99.100:8050/execute',
                     json=data_for_spash, headers=header_for_splash)

resp_data = resp.json()
#print resp_data
print '-'*20
url = resp_data['url']
print url
print '-'*20
headers = resp_data['headers']
print headers
print '-'*20
http_status = resp_data['http_status']
print http_status
print '-'*20
cookies = resp_data['cookies']
print cookies
print '-'*20
exit()

# cookies = requests.utils.cookiejar_from_dict(resp_data['cookies'])
br = requests.Session()
cj = CookieJar()
for cookie in cookies:
    del cookie[u'httpOnly']
    if u'expires' in cookie:
        exp = dateparser.parse(cookie[u'expires'])
        print dir(exp)
        print type(exp)
        print time.mktime(exp.utctimetuple())
        cookie[u'expires'] = int(time.mktime(exp.utctimetuple()))
    # timestamp = (exp - datetime(1970, 1, 1)).total_seconds()
    # print timestamp
    # cj = requests.utils.add_dict_to_cookiejar(cj,cookie)
    c = requests.cookies.create_cookie(**cookie)
    cj.set_cookie(c)


br.cookies = cj
url = "https://www.parliament.gov.sg/docs/default-source/default-document-library/co-operative-societies-(amendment)-bill-50-2017.pdf"
r = br.get(url, stream=True, headers=headers)
chunk_size = 1024
with open('metadata_1.pdf', 'wb') as fd:
    for chunk in r.iter_content(chunk_size):
        fd.write(chunk)


