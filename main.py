from util import *
from ttypes import *
from importer import *
from test import *
import http.server
import urllib
from http.cookies import SimpleCookie

def rewriteAllLinks():
    for ex in examples:
        content, resolvedLinks, unresolvedLinks = rewriteLinks(ex["content"], True)
        ex["content"]=content
        ex["resolvedLinks"]=resolvedLinks
        ex["unresolvedLinks"]=unresolvedLinks

def getUser(headers):
    user=None
    if "Cookie" in headers:
        cookie = SimpleCookie()
        cookie.load(headers["Cookie"])
        cookie={k: v.value for k, v in cookie.items()}
        if "userid" in cookie:
            for i in range(len(users)):
                if users[i]["name"]==cookie["userid"]:
                    user=i
                    break
    return user

class handler(http.server.BaseHTTPRequestHandler):
    def sendResponse(self, resp):
        self.send_response(resp["code"])
        if resp["type"]=='text':
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        elif resp["type"]=='json':
            self.send_header('Content-Type', 'application:json; charset=utf-8')
        if "headers" in resp:
            for k,v in resp["headers"].items():
                self.send_header(k, v)
        if "cookies" in resp:
            self.send_header("Set-Cookie", ";".join([urllib.parse.quote(k)+"="+urllib.parse.quote(v) for k,v in resp["cookies"].items()]))
        self.end_headers()
        self.wfile.write(bytes(resp["content"], 'utf-8'))

    def do_GET(self):
        user=getUser(self.headers)
        resp=handleGet(self.path, user)
        self.sendResponse(resp)

    def do_POST(self):
        user=getUser(self.headers)
        content_len = int(self.headers.get('Content-Length'))
        body=str(self.rfile.read(content_len), encoding="utf-8")
        ctype = self.headers.get("Content-Type")
        if ctype == "application/x-www-form-urlencoded":
            body = parse_qs(body)
        elif ctype == "application/json":
            body = json.loads(body)
        resp=handlePost(self.path, body, user)
        self.sendResponse(resp)

def run(server_class=http.server.HTTPServer, handler_class=handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


def initialImport():
    #open('example.html','w',encoding="utf-8").write(renderWikiPage(parse(open('example.txt',encoding="utf-8").read(),0)[0], 'en', 'Example'))
    #open('example.html','w',encoding="utf-8").write(renderHTML(tieExamples(groupExamples(importExamples(parse(open('example.txt').read(),0)[0])),lambda x:(PageElementType.LINK, x, x)), 'Example'))

    initDB()
    addTestUsers()

    importWork("VideoGame/Factorio", "en")
    importWork("YMMV/Factorio", "en", dest="VideoGame/Factorio", exPageType=PageType.YMMV)
    importWork("Trivia/Factorio", "en", dest="VideoGame/Factorio", exPageType=PageType.TRIVIA)
    importWork("VideoGame/Satisfactory", "en")
    importWork("Film/TotalRecall1990", "en")
    importTrope("RefiningResources", "en")
    importTrope("NoOSHACompliance", "en")

    importTrope("BFS", "en")
    importTrope("Es/EJG", "es", dest="Main/BFS", addPrimaryAlias=True)

    importTrope("PetTheDog", "en")
    importTrope("PetTheDog/WesternAnimation", "en", dest="Main/PetTheDog")
    importTrope("PetTheDog/AnimeAndManga", "en", dest="Main/PetTheDog")
    importTrope("PetTheDog/Literature", "en", dest="Main/PetTheDog")
    importTrope("PetTheDog/VideoGames", "en", dest="Main/PetTheDog")
    importTrope("Es/AcariciaAlPerro", "es", dest="Main/PetTheDog", addPrimaryAlias=True)
    print("imports complete")

    rewriteAllLinks()
    print("rewriting links complete")

test()
initialImport()
run()
