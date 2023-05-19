from ttypes import *
from i18n import *
from js_boilerplate import *
from collections import OrderedDict
from urllib.parse import parse_qs
import json, time, random, traceback, html, math
import http.server
hrc=http.server.HTTPStatus

REALLIFE="Misc/RealLife"
UNLIKED_EXAMPLE="Misc/UnlinkedExample"
MAX_RESULTS_PER_PAGE=50

blocks=[] # tgt, lang, bt, content
examples=[] # src, tgt, lang, content, ctime, mtime, asymmetric, backContent, playWith, hide, embargo
history=[]
pageTitles=[] # tgt, path, displayName, lang, isPrimary
pageDetail=[] # pageType, folder, hideHeader, ads, locked, fakeRedlink
# side: 0 - descriptor (trope, ymmv, trivia, useful notes)
#       1 - descriptee (work, creator, Real Life)
#       2 - other (not suitable as an example source or target)
users=[] # name, roles, description

def initDB():
    blocks.clear()
    examples.clear()
    history.clear()
    pageTitles.clear()
    pageDetail.clear()
    users.clear()

    #special pages
    createPageWithAlias(REALLIFE, PageType.WORK, 'Real life', 'en', pageExtraOpts={"folder": "RealLife", "hideHeader": True})
    createPageWithAlias(UNLIKED_EXAMPLE, PageType.WORK, 'Unlinked example', 'en', pageExtraOpts={"folder": "UnlinkedExample", "hideHeader": True})

namespaces={}

for mt in ['Main', 'YMMV', 'SugarWiki', 'Trivia']:
    namespaces[mt]={"lang": "en", "side":0}

for mt in ['Animation', 'BadCategory', 'Creator', 'Franchise', 'Series', 'FanFic', 'Film', 'VideoGame', 'Anime', 'LightNovel', 'Manga', 'Manhua', 'Manhwa', 'Music', 'ComicBook', 'WebAnimation',
    'Myth', 'WesternAnimation', 'Radio', 'TabletopGame', 'Ride', 'WebSite', 'Podcast', 'Roleplay', 'Literature', 'LetsPlay', 'WebVideo', 'Webcomic', 'Theatre', 'Toys', 'VisualNovel', 'Wrestling', 'Misc']:
    namespaces[mt]={"lang": "en", "side":1}

for mt in ['UsefulNotes']:
    namespaces[mt]={"lang": "en", "side":2}

for k,v in {
    'Es': 'Main',
    }.items():
    namespaces[k]={"lang":"es", "side":0, "aliasFor":v}

for k,v in {
    'EsAnimacionOccidental': 'WesternAnimation',
    'EsManga':'Manga',
    'EsAnime':'Anime',
    'EsLiteratura':'Literature',
    'EsVideojuego': 'VideoGame',
    }.items():
    namespaces[k]={"lang":"es", "side":1, "aliasFor":v}

roleActions={}
roleActions["editor"]=["edit"]
roleActions["moderator.en"]=["edit", "mod.en", "edit.locked.en", "create.descriptor"]
roleActions["moderator.es"]=["edit", "mod.es", "edit.locked.es", "create.descriptor"]
roleActions["admin"]=["edit", "mod", "create.descriptor", "create.admin", "pageprops", "edit.locked", "edit.addRedlink", "admin"]

def addTestUsers():
    users.append({"name": "alice", "roles": ["editor"], "description": "Normal user"})
    users.append({"name": "bob", "roles": ["editor"], "description": "Normal user"})
    users.append({"name": "karen", "roles": ["moderator.en"], "description": "Moderator (EN)"})
    users.append({"name": "juan", "roles": ["moderator.es"], "description": "Moderator (ES)"})
    users.append({"name": "lolmooga", "roles": [], "description": "User without edit rights"})
    users.append({"name": "wordya", "roles": ["admin"], "description": "Admin"})

def tryParseInt(text):
    try:
        return int(text)
    except:
        return None

def authorize(user, action, lang):
    if user is None:
        return False
    roles=users[user]["roles"]
    langAction=action+"."+lang
    for role in roles:
        actions=roleActions[role]
        if action in actions or langAction in actions:
            return True
    return False

def pageLocked(pi, user, lang):
    if not pageDetail[pi]["locked"]:
        return False
    return not authorize(user, "edit.locked", lang)

def pageIsFakeRedlink(pi, user, lang):
    if not pageDetail[pi]["fakeRedlink"]:
        return False
    return not authorize(user, "edit.addRedlink", lang)

def normalizeNs(ns):
    if not ns in namespaces:
        found = False
        lns = ns.lower()
        for ns0 in namespaces.keys():
            if ns0.lower() == lns:
                found = True
                ns = ns0
                break
        if not found:
            raise Exception("invalid namespace {}".format(ns))
    return ns

def normalizePath(path):
    pp=path.split('/')
    if 2<len(pp):
        raise Exception("too many path elements: {}".format(path))
    if 1==len(pp):
        ns = "Main"
        page = pp[0]
    else:
        ns = pp[0]
        page = pp[1]
    ns=normalizeNs(ns)
    return ns+"/"+page

def getPageIndex(path):
    for tt in pageTitles:
        if tt["path"]==path:
            return tt["tgt"]
    return -1

def getBlockIndex(tgt, lang, bt):
    bi=-1
    for i,block in enumerate(blocks):
        if block["tgt"]==tgt and block["bt"]==bt and block["lang"]==lang:
            bi=i
            break
    return bi

def getAliasForPath(path):
    for tt in pageTitles:
        if tt["path"]==path:
            return tt

def getPagePrimaryAlias(pi, lang):
    result = None
    for tt in pageTitles:
        if tt["tgt"]==pi and tt["lang"]==lang:
            if tt["isPrimary"] or result is None:
                result = tt
    return result

def getPagePrimaryPath(pi, lang):
    alias=getPagePrimaryAlias(pi,lang)
    return alias["path"] if alias is not None else None

def getPageDisplayName(pi, lang):
    alias=getPagePrimaryAlias(pi,lang)
    if alias is None:
        alias=getPagePrimaryAlias(pi,"en")
    return alias["displayName"]

def getNamespaceDisplayName(ns, lang):
    if ns in namespaces and "aliasFor" in namespaces[ns]:
        ns=namespaces[ns]["aliasFor"]
    if ns in i18n[lang]["namespaces"]:
        return i18n[lang]["namespaces"][ns]
    return ns

def hasExamples(pi):
    for ex in examples:
        if ex["src"]==pi:
            return True
        elif ex["tgt"]==pi:
            return True
    return False

def getPageHistory(pi):
    result=[]
    for hist in history:
        if hist["event"] in ["addExample", "editExample"]:
            if hist["wi"] == pi or hist["ti"] == pi:
                result.append(hist)
        if hist["event"] in ["moveExample", "moveAlias", "changeExHidden"]:
            if hist["src"] == pi or hist["tgt"] == pi:
                result.append(hist)
        elif hist["event"] in ["addBlock", "editBlock"]:
            if hist["tgt"] == pi:
                result.append(hist)
    return result

def getUserHistory(user):
    result=[]
    for hist in history:
        if hist["user"]==user:
            result.append(hist)
    return result

def formatTime(tm):
    return time.strftime("%Y-%m-%d %H:%M:%S %z",time.localtime(tm/1000000000))

def formatHistory(hist):
    result=formatTime(hist["time"])+": user "+users[hist["user"]]["name"]+" "
    if hist["event"] == "addExample":
        result += "added an example"
    elif hist["event"] == "editExample":
        result += "edited an example"
    elif hist["event"] == "moveExample":
        result += "moved an example"
    elif hist["event"] == "moveAlias":
        result += "moved alias"
    elif hist["event"] == "addBlock":
        result += "added a block"
    elif hist["event"] == "editBlock":
        result += "edited a block"
    elif hist["event"] == "changeExHidden":
        result += "hid an example" if hist["val"] else "unhid an example"
    else:
        raise Exception("unknown history event type: {}".format(hist["event"]))
    if hist["event"] in ["addExample", "editExample"]:
        pSrc=getPagePrimaryPath(hist["ti"], "en") or "wiki/"+str(hist["ti"])
        pTgt=getPagePrimaryPath(hist["wi"], "en") or "wiki/"+str(hist["wi"])
        result+=" of "+pSrc+" in "+pTgt
    if hist["event"] == "moveExample":
        result+=" from "+hist["srcPath"]+" to "+hist["tgtPath"]
    if hist["event"] == "moveAlias":
        result+=" "+hist["path"]+" from "+hist["srcPath"]+" to "+hist["tgtPath"]
    if "content" in hist:
        result+="<br>"+renderHTMLList(hist["content"], "en", None)
    return htc("li", result)

def getExamplesRaw(idx, lang, filt, srt, addHidden):
    exs=[]
    for i, ex in enumerate(examples):
        if ex["lang"]==lang and (not ex["hide"] or addHidden):
            if ex["src"]==idx:
                if filt is None or pageDetail[ex["src"]]["pageType"]==filt:
                    exs.append((ex["tgt"], ex["content"], i, ex["ctime"], ex["mtime"], ex["playWith"], ex["hide"]))
            elif ex["tgt"]==idx:
                if filt is None or pageDetail[ex["src"]]["pageType"]==filt:
                    exs.append((ex["src"], ex["content"] if not ex["asymmetric"] else ex["backContent"], i, ex["ctime"], ex["mtime"], ex["playWith"], ex["hide"]))
    if srt==SortType.AZ:
        exs=sorted(exs, key=lambda x:getPageDisplayName(x[0], lang))
    elif srt==SortType.CTIME_UP:
        exs=sorted(exs, key=lambda x:(x[3],x[2]))   #include example ID in key, as when importing pages all examples will likely have the same ctime/mtime
    elif srt==SortType.CTIME_DOWN:
        exs=sorted(exs, key=lambda x:(x[3],x[2]), reverse=True)
    elif srt==SortType.MTIME_UP:
        exs=sorted(exs, key=lambda x:(x[4],x[2]))
    elif srt==SortType.MTIME_DOWN:
        exs=sorted(exs, key=lambda x:(x[4],x[2]), reverse=True)
    return exs

def getExamples(wi, lang, filt, srt, addHidden):
    exs=getExamplesRaw(wi, lang, filt, srt, addHidden)
    exs2=groupExamples(exs)
    return exs2

def getLinkSide(link, normNs):
    ns=link.split("/")[0] if "/" in link else "Main"
    if normNs:
        ns=normalizeNs(ns)
    return namespaces[ns]["side"]

def resolveLink(side, pi, lang):
    if pi == -1:
        return (PageElementType.TEXT, '???')
    hideHeader=pageDetail[pi]["hideHeader"] if "hideHeader" in pageDetail[pi] else False
    if hideHeader:
        return []
    if side == 1:
        return [(PageElementType.RESOLVED_LINK, pi, lang, None)]
    else:
        return [(PageElementType.EMPHASIS, 2, [(PageElementType.RESOLVED_LINK, pi, lang, None)])]

def folderizeExamples(exs, nameResolver, lang):
    result={}
    for ex in exs:
        folder=''
        if "folder" in pageDetail[ex[0]]:
            folder=pageDetail[ex[0]]["folder"]
        else:
            name=nameResolver(ex[0])
            if '/' in name:
                folder=name.split('/')[0]
        if 0<len(folder):
            folder=getNamespaceDisplayName(folder, lang)
        if folder in result:
            result[folder].append(ex)
        else:
            result[folder]=[ex]
    folders=sorted(list(result.items()),key=lambda x:x[0])
    return folders

def getPageSide(pi):
    return pageTypeToSide[pageDetail[pi]["pageType"]]

def genExamplesAst(pi, lang, filt, srt, addHidden):
    side=getPageSide(pi)
    exs=getExamples(pi, lang, filt, srt, addHidden)
    exsf=folderizeExamples(exs, lambda x:getPagePrimaryPath(x,lang), lang)
    resolver=lambda pi:resolveLink(side, pi, lang)
    exast=[]
    if 0==len(exsf):
        exast+=[(PageElementType.TEXT,i18n[lang]["noExamples"])]
    elif 1==len(exsf):
        exast+=tieExamples(exsf[0][1], lang, resolver)
    else:
        exast+=[(PageElementType.FOLDERCONTROL,),(PageElementType.PARAGRAPH_BREAK,)]
        for folder in exsf:
            exast+=[(PageElementType.FOLDER,folder[0],tieExamples(folder[1], lang, resolver)),(PageElementType.PARAGRAPH_BREAK,)]
    return exast

def createPage(path, pageType, extraOpts={}):
    if -1<getPageIndex(path):
        raise Exception("page already exists: {}".format(path))
    pp = path.split('/')
    if not pp[0] in namespaces:
        raise Exception('cannot create page {} in namespace: {}'.format(path, pp[0]))
    pageDetail.append({"pageType": pageType, "ads": False, "locked": False, "fakeRedlink": False} | extraOpts)
    return len(pageDetail)-1

def createAlias(tgt, path, displayName, lang, primary):
    pi=getPageIndex(path)
    if pi>-1:
        raise Exception('path already exists: {}'.format(path))
    if not 0<=tgt<len(pageDetail):
        raise Exception('invalid alias target: {}'.format(tgt))
    pp = path.split('/')
    if not pp[0] in namespaces:
        raise Exception('cannot create page {} in namespace: {}'.format(path, pp[0]))
    alias={"tgt":tgt, "path":path, "displayName":displayName, "lang":lang, "isPrimary": primary}
    pageTitles.append(alias)

def createPageWithAlias(path, pageType, displayName, lang, pageExtraOpts={}):
    pi = createPage(path, pageType, extraOpts=pageExtraOpts)
    createAlias(pi, path, displayName, lang, True)
    return pi

def getNamespacesForSide(side, lang):
    return [k for k,v in namespaces.items() if v["side"]==side and v["lang"]==lang]

def parseWiki(text, i, terminator=None, initNewLine=True):
    newLine = initNewLine
    lastImageInd=-1
    result=[]
    currType=PageElementType.NONE
    currValue=""

    def scanWord(text,i):
        i0=i
        while i<len(text) and ('a'<=text[i]<='z' or 'A'<=text[i]<='Z' or '0'<=text[i]<='9'):
            i+=1
        return (i,text[i0:i])

    def isWikiWord(word):
        i=0
        if 2>=len(word):
            return False
        if not 'A'<=word[i]<='Z':
            return False
        upperCount=0
        while 'A'<=word[i]<='Z':
            i+=1
            upperCount+=1
            if i==len(word):
                return False
        if not ('a'<=word[i]<='z' or '0'<=word[i]<='9'):
            return False
        while 'a'<=word[i]<='z':
            i+=1
            if i==len(word):
                return upperCount>1
        if not ('A'<=word[i]<='Z' or '0'<=word[i]<='9' or upperCount>1):
            return False
        return True

    def joinWikiWord(text):
        result=""
        cap=True
        for i in range(len(text)):
            ch=text[i]
            if ch == ' ':
                cap=True
            elif cap:
                cap=False
                result+=ch.upper()
            else:
                result+=ch
        return result

    def appendText(s):
        nonlocal currType
        nonlocal currValue
        nonlocal newLine
        prevNewLine=newLine
        newLine = False
        if currType == PageElementType.NONE:
            currType = PageElementType.TEXT
            currValue = s
        elif currType == PageElementType.TEXT:
            if prevNewLine:
                currValue += " "
            currValue += s
        else:
            raise Exception("don't know how to handle text after {}".format(currType))

    def appendContent(cont):
        nonlocal newLine
        nonlocal result
        newLine = False
        result.append(cont)

    def flush():
        nonlocal currType
        nonlocal currValue
        if currType != PageElementType.NONE:
            appendContent((currType, currValue))
            currType=PageElementType.NONE
            currValue=""

    def addToList(target, level, cont):
        if level<=0:
            raise Exception('invalid list level')
        elif level==1:
            if cont[0]==PageElementType.LIST and len(target[1])>0 and target[1][-1][0]==PageElementType.LISTITEM:
                target[1][-1][1].extend(cont)
            elif cont[0]==PageElementType.QUOTE and len(target[1])>0 and target[1][-1][0]==PageElementType.LISTITEM:
                target[1][-1][1].append(cont)
            else:
                target[1].append(cont)
        else:
            if len(target[1])>0 and target[1][-1][0]==PageElementType.LIST:
                addToList(target[1][-1], level-1, cont)
            elif len(target[1])>0 and target[1][-1][0]==PageElementType.LISTITEM:
                addToList(target[1][-1], level, cont)
            else:
                target[1].append((PageElementType.LIST, []))
                addToList(target[1][-1], level-1, cont)

    def mergeOrAppendLink(word, sp):
        nonlocal result
        if 0<len(result) and result[-1][0] == PageElementType.TEXT and result[-1][1].endswith('/'):
            if result[-1][1] == '/' and 1<len(result) and result[-2][0] == PageElementType.LINK: # WikiWord/AnotherWikiWord
                result.pop()
                lnk = (PageElementType.LINK, result[-1][1]+'/'+word, sp)
                result[-1] = lnk
            else:
                lastText=result[-1][1]
                cut=len(lastText)-2
                while cut>0 and 'a'<=lastText[cut]<='z' or 'A'<=lastText[cut]<='Z':
                    cut-=1
                if -1<cut:
                    remain=lastText[:cut+1]
                    ns=lastText[cut+1:]
                    result[-1]=(PageElementType.TEXT, remain)
                    lnk=(PageElementType.LINK, ns+word, sp)
                    appendContent(lnk)
                else:
                    lnk=(PageElementType.LINK, lastText+word, sp)
                    result[-1]=lnk
            return
        lnk=(PageElementType.LINK, word, sp)
        appendContent(lnk)

    while i<len(text):
        if terminator is not None:
            term=False
            if text[i:i+len(terminator)] == terminator:
                term=True
            if term and terminator=="''":    #stupid quirky syntax ''aa'''bb'''''
                if text[i:i+3]=="'''":
                    term=False
            if term:
                i+=len(terminator)
                flush()
                return (result,i)
        ch = text[i]
        if 'a'<=ch<='z' or 'A'<=ch<='Z':
            (i,word)=scanWord(text,i)
            isWiki = isWikiWord(word)
            if not isWiki:
                appendText(word)
            else:
                flush()
                #sp = splitWikiWord(word)
                #mergeOrAppendLink(word, sp)
                mergeOrAppendLink(word, None)
        elif -1<'<>~+ "&?:;.,_/|()]$#0123456789='.find(ch):
            appendText(ch)
            i+=1
        elif ch == '-':
            if newLine:
                j=i
                level=0
                while j<len(text) and text[j]=='-':
                    j+=1
                    level+=1
                if j<len(text) and text[j]=='>':
                    j+=1
                    while j<len(text) and text[j]==' ':
                        j+=1
                    flush()
                    i=j
                    (part,i) = parseWiki(text, i, '\n')
                    level-=1
                    if 0==level:
                        appendContent((PageElementType.QUOTE, part))
                    elif 0<len(result) and result[-1][0] == PageElementType.LIST:
                        addToList(result[-1], level, (PageElementType.QUOTE, part))
                    else:
                        elem=(PageElementType.LIST, [])
                        appendContent(elem)
                        addToList(result[-1], level, (PageElementType.QUOTE, part))
                    newLine=True
                elif level>=4:
                    flush()
                    i+=level
                    appendContent((PageElementType.SECTION_SEPARATOR,))
                else:
                    appendText(ch)
                    i+=1
            else:
                appendText(ch)
                i+=1
        elif ch == '%':
            i+=1
            ch = text[i]
            if ch == '%':
                end = text.find('\n', i)
                if end==-1:
                    end = len(text)
                if newLine:
                    appendContent((PageElementType.FORCE_NEWLINE,))
                flush()
                appendContent((PageElementType.LINE_COMMENT, text[i+1:end]))
                i = end+1
                newLine = True
            elif 'a'<=ch<='a' or 'A'<=ch<='Z':
                flush()
                end = text.find('%', i)
                appendContent((PageElementType.BLOCK_COMMENT, text[i:end]))
                i = end+1
            else:
                appendText('%')
        elif 127<=ord(ch):
            appendText(ch)
            i+=1
        elif ch == '\n':
            if newLine:
                flush()
                appendContent((PageElementType.PARAGRAPH_BREAK,))
            newLine = True
            i+=1
        elif ch == '{':
            i+=1
            ch = text[i]
            if ch == '{':
                i+=1
                flush()
                (part,i) = parseWiki(text, i, '}}')
                if 0==len(part):
                    raise Exception("empty braced link")
                elif part[0][0] == PageElementType.LINK:
                    if 1<len(part) and part[1][0] == PageElementType.TEXT and part[1][1][0] == '/':
                        target=part[0][1] + part[1][1]
                        #appendContent((PageElementType.LINK, target, part[1][1][1:]))
                        appendContent((PageElementType.LINK, target, None))
                    else:
                        appendContent(part[0])
                elif part[0][0] != PageElementType.TEXT:
                    raise Exception("non-text element in braced link: '{}'".format(part[0]))
                else:
                    link=part[0][1]
                    #disp=link
                    disp=None
                    split=link.find('|')
                    if split>-1:
                        disp=link[:split]
                        link=link[:split]+link[split+1:]
                    mergeOrAppendLink(joinWikiWord(link), disp)
            else:
                raise Exception("unrecognized character after {{: '{}'".format(ch))
        elif ch == '[':
            i+=1
            ch = text[i]
            if ch == '[':
                i+=1
                flush()
                i0=i
                nextClose=text.find(']]',i)
                if nextClose==-1:
                    nextClose=len(text)
                nextSpace=text.find(' ',i)
                if nextSpace==-1:
                    nextSpace=len(text)
                command=text[i:min(nextClose,nextSpace)]
                (part,i) = parseWiki(text, i, ']]')
                if command.startswith('source:'):
                    pass
                elif command.startswith('http://') or command.startswith('https://'):
                    link=text[i0:nextSpace]
                    disp=text[nextSpace+1:i-2]
                    appendContent((PageElementType.WEBLINK, link, disp))
                elif command=='/folder':
                    return (None,None)  # e.g. unterminated ''
                else:
                    if 0==len(part):
                        raise Exception("empty command")
                    elif part[0][0] == PageElementType.TEXT:
                        command=part[0][1]
                        if command.startswith('quoteright:'):
                            cp=command.split(':')
                            lastImageInd=len(result)
                            url=':'.join(cp[2:])
                            if 0==len(url):
                                if 1<len(part) and part[1][0] == PageElementType.LINK:
                                    url=part[1][2]
                            appendContent((PageElementType.IMAGE, int(cp[1]), url))
                        elif command.startswith('caption-width-right:'):
                            cp=command.split(':')
                            cpWidth=int(cp[1])
                            cpText=':'.join(cp[2:])
                            cpPart=([(PageElementType.TEXT,cpText)] if 0<len(cpText) else []) + part[1:]
                            if lastImageInd>-1:
                                img=result[lastImageInd]
                                result[lastImageInd]=(PageElementType.CAPTIONED_IMAGE, img[1], img[2], cpWidth, cpPart)
                                lastImageInd=-1
                            else:
                                appendContent((PageElementType.INFOBOX, cpWidth, cpPart))
                        elif command.startswith('spoiler:'):
                            cp=command.split(':')
                            cpText=':'.join(cp[1:])
                            cpPart=([(PageElementType.TEXT,cpText)] if 0<len(cpText) else []) + part[1:]
                            appendContent((PageElementType.SPOILER, cpPart))
                        elif command == 'index':
                            if text[i] == '\n':
                                i+=1
                            (part,i) = parseWiki(text, i, '[[/index]]')
                            appendContent((PageElementType.INDEX, part))
                        elif command == 'foldercontrol':
                            appendContent((PageElementType.FOLDERCONTROL,))
                        elif command == 'note':
                            (part,i) = parseWiki(text, i, '[[/note]]')
                            appendContent((PageElementType.NOTE, '', part))
                        elif command.startswith('labelnote:'):
                            label=command[10:]
                            (part,i) = parseWiki(text, i, '[[/labelnote]]')
                            appendContent((PageElementType.NOTE, label, part))
                        elif command.startswith('strike:'):
                            part[0]=(part[0][0],part[0][1][7:])
                            appendContent((PageElementType.STRIKE, part))
                        elif command.startswith('AC:'):
                            part[0]=(part[0][0],part[0][1][3:])
                            appendContent((PageElementType.ASSCAPS, part))
                        elif command.startswith('folder:'):
                            label=command[7:]
                            if text[i]=='\n':
                                i+=1
                                newLine=True
                            else:
                                newLine=False
                            (part,i) = parseWiki(text, i, '[[/folder]]', initNewLine=newLine)
                            appendContent((PageElementType.FOLDER, label, part))
                        else:
                            raise Exception("unrecognized command: '{}'".format(command))
                    elif part[0][0] == PageElementType.LINK:
                        (_,afterLink) = parseWiki(text, i0, ' ')
                        linkText=text[afterLink:i-2]
                        if linkText=='':
                            linkText='[1]'
                        lnk=(PageElementType.LINK, joinWikiWord(part[0][1]), linkText)
                        appendContent(lnk)
                    else:
                        raise Exception("unknown element in command: '{}'".format(part[0]))
            elif ch == '=':
                flush()
                i+=1
                end = text.find('=]',i)
                if end == -1:
                    raise Exception("unmatched [=")
                appendContent((PageElementType.ESCAPE, text[i:end]))
                i = end+2
            else:
                appendText('[')
        elif ch == "'":
            width=0
            while i<len(text) and text[i] == "'" and width<5:
                i+=1
                width+=1
            if width == 4:
                i-=1
                width-=1
            if width == 1:
                appendText(ch)
            else:
                (part,newi) = parseWiki(text, i, width*"'")
                if part is None and width==2:
                    appendText("''")
                else:
                    flush()
                    if part is None and width==3 and terminator=="''":
                        i-=1
                        return (result,i)
                    appendContent((PageElementType.EMPHASIS, width, part))
                    i=newi
        elif ch == "!":
            if not newLine:
                i+=1
                appendText(ch)
            else:
                flush()
                width=0
                while i<len(text) and text[i] == "!":
                    i+=1
                    width+=1
                (part,i) = parseWiki(text, i, "\n")
                appendContent((PageElementType.HEADER, width, part))
                newLine = True
        elif ch == "*":
            if not newLine:
                i+=1
                appendText(ch)
            else:
                if terminator=="'''":   # ''aa'''bb\n*cc
                    return (None,None)
                flush()
                level=0
                while i<len(text) and text[i] == "*":
                    i+=1
                    level+=1
                while i<len(text) and text[i] == " ":
                    i+=1
                (part,i) = parseWiki(text, i, "\n")
                if 0<len(result) and result[-1][0] == PageElementType.LIST:
                    addToList(result[-1], level, (PageElementType.LISTITEM, part))
                else:
                    elem=(PageElementType.LIST, [])
                    appendContent(elem)
                    addToList(result[-1], level, (PageElementType.LISTITEM, part))
                newLine = True
        elif ch == "\\":
            if text[i:i+3]=="\\\\\n":
                i+=3
                appendText('\n')
            else:
                i+=1
                appendText(ch)
        else:
            raise Exception("unrecognized character: '{}' near {}".format(ch, text[i:i+10]))
    flush()
    if terminator=="''":    # unterminated
        return (None, None)
    return (result,i)

def splitWikiWord(word):
    result=""
    for i in range(len(word)):
        if 0<i<len(word)-1 and 'A'<=word[i]<='Z' and 'a'<=word[i+1]<='z':
            result+=' '+word[i]
        elif 0<i and 'a'<=word[i-1]<='z' and 'A'<=word[i]<='Z':
            result+=' '+word[i]
        elif 0<i and (not '0'<=word[i-1]<='9') and '0'<=word[i]<='9':
            result+=' '+word[i]
        else:
            result+=word[i]
    return result

def escapeAttr(t):
    return t.replace('"', '&quot;')

def escapeText(t):
    return t.replace('<', '&lt;').replace('>', '&gt;')

def htc(t,c):
    return '<'+t+'>'+c+'</'+t+'>'

def hta(t,a):
    return '<'+t+"".join([' '+x+'="'+escapeAttr(y)+'"' for x,y in a.items()])+('>')

def htac(t,a,c):
    return '<'+t+"".join([' '+x+'="'+escapeAttr(y)+'"' for x,y in a.items()])+('>'+c+'</'+t+'>')

def ha(a,c):
    return htac("a", {"href": a}, c)

def renderHTMLList(elems, lang, currentPage):
    return ''.join([renderHTMLElem(x, lang, currentPage) for x in elems])

def renderHTMLElem(elem, lang, currentPage):
    if not type(elem)==tuple:
        raise Exception('element is not a tuple: {}'.format(elem))
    ty=elem[0]
    if ty==PageElementType.TEXT:
        return escapeText(elem[1])
    elif ty==PageElementType.ESCAPE:
        return escapeText(elem[1])
    elif ty==PageElementType.RESOLVED_LINK:
        alias = getPagePrimaryAlias(elem[1], elem[2])
        disp=elem[3] if elem[3] is not None else alias["displayName"]
        if currentPage==elem[1]:
            return renderHTMLElem((PageElementType.TEXT, disp), lang, currentPage)
        link=(PageElementType.LINK, alias["path"], disp)
        return renderHTMLElem(link, lang, currentPage)
    elif ty==PageElementType.LINK:
        path=("Main/" if '/' not in elem[1] else "")+elem[1]
        title=path
        alias=getAliasForPath(path)
        if elem[2] is None:
            disp=escapeText(splitWikiWord(elem[1].split('/')[-1]))
        else:
            disp=escapeText(elem[2])
        prop={"href": "/"+path}
        if alias is None or pageDetail[alias["tgt"]]["fakeRedlink"]:
            prop["class"]="red"
            title+=" ("+i18n[lang]["invalidPage"]+")"
        elif alias["lang"] != lang:
            disp+='\U0001F30D'
            title+=" ("+i18n[lang]["crossLangLink"]+")"
        prop["title"]=title
        return htac('a', prop, disp)
    elif ty==PageElementType.WEBLINK:
        return htac('a', {"href": elem[1]}, escapeText(elem[2])+hta('img',{'src':"https://static.tvtropes.org/pmwiki/pub/external_link.gif",
            'style':"border:none;", "width":"12", "height":"12"}))
    elif ty==PageElementType.LIST:
        return htc('ul', renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.LISTITEM:
        return htc('li', renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.IMAGE:
        # If we don't assign a height to the image, in Firefox with F12 open, clicking a note to expand it
        # causes the scroll to jump by a few lines. This is not a problem on real tvtropes because it knows
        # the height of the image even though it's not indicated by the page source.
        return htac('div', {"class": "quoteright", "style": "width:{}px;".format(elem[1])},
            hta('img', {"src": elem[2], "height": "500"}))
    elif ty==PageElementType.CAPTIONED_IMAGE:
        return htac('div', {"class": "quoteright", "style": "width:{}px;".format(elem[1])},
            hta('img', {"src": elem[2], "height": "500"}) + renderHTMLList(elem[4], lang, currentPage))
    elif ty==PageElementType.EMPHASIS and elem[1]==2:
        return htc('em', renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.EMPHASIS and elem[1]==3:
        return htc('strong', renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.EMPHASIS and elem[1]==5:
        return htc('em', htc('strong', renderHTMLList(elem[2], lang, currentPage)))
    elif ty==PageElementType.HEADER:
        return htc('h'+str(elem[1]), renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.BLOCK_COMMENT:
        return ''
    elif ty==PageElementType.LINE_COMMENT:
        return ''
    elif ty==PageElementType.QUOTE:
        return htac('div', {'class': 'quote'}, renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.SPOILER:
        return htac('span', {"class": "spoiler"}, renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.NOTE:
        return htac('span', {"class": "notelabel", 
            }, i18n[lang]["noteLabel"] if 0==len(elem[1]) else escapeText(elem[1])) +\
            htac('span', {"class": "note", "style":"display:none"}, renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.SECTION_SEPARATOR:
        return '<hr>'
    elif ty==PageElementType.INDEX:
        return renderHTMLList(elem[1], lang, currentPage)
    elif ty==PageElementType.FOLDERCONTROL:
        return htac('div', {"class": "foldercontrol-closed", "id": "folderCtrlGlobal"}, i18n[lang]["folderCtrlGlobal"])
    elif ty==PageElementType.FOLDER:
        return htac('div', {"class": "foldercontrol-closed"}, escapeText(elem[1])) +\
            htac('div', {"class": "folder-closed"}, renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.STRIKE:
        return htc('strike', renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.ASSCAPS:
        return htac('span', {"class": "asscaps"}, renderHTMLList(elem[1], lang, currentPage))
    elif ty==PageElementType.PARAGRAPH_BREAK:
        return '<br>'
    elif ty==PageElementType.EXAMPLE:
        return htac('div', {"class": "example", "data-idx": str(elem[1])}, renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.FORCE_NEWLINE:
        return ''
    elif ty==PageElementType.NEW_EXAMPLE_PLACEHOLDER:
        return htac('div', {"id":"nxp", "data-side":str(elem[1]), "data-pi":str(elem[2]), "data-title":elem[3]}, '')
    elif ty==PageElementType.PAGE_BLOCK:
        v=str(elem[1].value)
        return htac('div', {"class": "block", "id": "block"+v, "data-bt":v}, renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.CONTAINER:
        return htac('div', elem[1], renderHTMLList(elem[2], lang, currentPage))
    elif ty==PageElementType.FORMATTER:
        return htac('span', elem[1], renderHTMLList(elem[2], lang, currentPage))
    else:
        raise Exception("Don't know how to render: {}".format(elem))

def renderWikiList(ast, level=0, newLine=True):
    result=''
    for x in ast:
        t = renderWikiElem(x, level, newLine)
        result+=t
        if len(result)>0:
            newLine=result[-1]=='\n'
    return result

def renderWikiElem(elem, level=0, newLine=True):
    if not type(elem)==tuple:
        raise Exception('element is not a tuple: {}'.format(elem))
    ty=elem[0]
    if ty==PageElementType.TEXT:
        return elem[1]
    if ty==PageElementType.ESCAPE:
        return '[='+elem[1]+'=]'
    elif ty==PageElementType.RESOLVED_LINK:
        path = getPagePrimaryPath(elem[1], elem[2])
        return renderWikiElem((PageElementType.LINK, path, elem[3]), level, newLine)
    elif ty==PageElementType.LINK:
        if elem[2] is None:
            return '{{'+elem[1]+'}}'
        else:
            return '[[{{'+elem[1]+'}} '+elem[2]+']]'
    elif ty==PageElementType.WEBLINK:
        return '[['+elem[1]+' '+elem[2]+']]'
    elif ty==PageElementType.LIST:
        cont=renderWikiList(elem[1], level+1, newLine)
        return cont
    elif ty==PageElementType.LISTITEM:
        return ('' if newLine else '\n')+level*'*'+' '+renderWikiList(elem[1], level, False)
    elif ty==PageElementType.IMAGE:
        return '[[quoteright:{}:{}]]'.format(elem[1],elem[2])
    elif ty==PageElementType.CAPTIONED_IMAGE:
        return '[[quoteright:{}:{}]][[caption-width-right:{}:{}]]'.format(elem[1],elem[2],elem[3],renderWikiList(elem[4], level))
    elif ty==PageElementType.EMPHASIS:
        mark=elem[1]*"'"
        return mark+renderWikiList(elem[2], level)+mark
    elif ty==PageElementType.HEADER:
        return elem[1]*'!'+renderWikiList(elem[2], level)
    elif ty==PageElementType.LINE_COMMENT:
        return '%%'+elem[1]+'\n'
    elif ty==PageElementType.SPOILER:
        return '[[spoiler:'+renderWikiList(elem[1], level)+']]'
    elif ty==PageElementType.NOTE:
        if elem[1]=='':
            return '[[note]]'+renderWikiList(elem[2], level)+'[[/note]]'
        else:
            return '[[labelnote:'+elem[1]+']]'+renderWikiList(elem[2], level)+'[[/labelnote]]'
    elif ty==PageElementType.QUOTE:
        return ('' if newLine else '\n')+(1+level)*'-'+'>'+renderWikiList(elem[1], level, False).replace('\n','\\\\\n')
    elif ty==PageElementType.SECTION_SEPARATOR:
        return ('' if newLine else '\n')+'----\n'
    elif ty==PageElementType.INDEX:
        return '[[index]]\n'+renderWikiList(elem[1], level)+'\n[[/index]]\n'
    elif ty==PageElementType.FOLDERCONTROL:
        return '[[foldercontrol]]'
    elif ty==PageElementType.FOLDER:
        return '[[folder:'+elem[1]+']]\n'+renderWikiList(elem[2], level)+'\n[[/folder]]\n'
    elif ty==PageElementType.STRIKE:
        return '[[strike:'+renderWikiList(elem[1], level)+']]'
    elif ty==PageElementType.ASSCAPS:
        return '[[AC:'+renderWikiList(elem[1], level)+']]'
    elif ty==PageElementType.PARAGRAPH_BREAK:
        return ('' if newLine else '\n')+'\n'
    elif ty==PageElementType.FORCE_NEWLINE:
        return ('' if newLine else '\n')
    elif ty==PageElementType.EXAMPLE:
        return renderWikiList(elem[2])
    else:
        raise Exception("Don't know how to render: {}".format(elem))

def renderWiki(ast):
    return renderWikiList(ast)

def groupExamples(exs):
    exs2=OrderedDict()
    for ex in exs:
        cont=(ex[2],ex[1],ex[5], ex[6])
        if ex[0] in exs2:
            exs2[ex[0]].append(cont)
        else:
            exs2[ex[0]] = [cont]
    return list(exs2.items())

def renderPlayingWith(play, lang):
    if play == PlayingWithType.STRAIGHT:
        return []
    return [(PageElementType.EMPHASIS, 2, [(PageElementType.TEXT,guii18n[lang]["playingWithType"][play.value]+": ")])]

def tieExample(ast, lang, play, hide):
    ex=renderPlayingWith(play, lang) + ast
    if hide:
        ex=[(PageElementType.FORMATTER, {"class": "hidden"}, ex)]
    return ex

def tieExamples(exs, lang, linkResolver):
    exList=[]
    for ex in exs:
        cont=linkResolver(ex[0])
        if 1==len(ex[1]):
            if 0<len(cont):
                cont.append((PageElementType.TEXT,': '))
            cont.extend(tieExample(ex[1][0][1], lang, ex[1][0][2], ex[1][0][3])) # content
            cont=[(PageElementType.EXAMPLE, ex[1][0][0], cont)] # id
            exList.append((PageElementType.LISTITEM,cont))
        else:
            if 0<len(cont):
                cont.append((PageElementType.TEXT,':'))
                cont+=[(PageElementType.LIST, [(PageElementType.LISTITEM,[(PageElementType.EXAMPLE,x[0],tieExample(x[1], lang, x[2], x[3]))]) for x in ex[1]])]
                exList.append((PageElementType.LISTITEM,cont))
            else:
                cont+=[(PageElementType.LISTITEM,[(PageElementType.EXAMPLE,x[0],tieExample(x[1], lang, x[2], x[3]))]) for x in ex[1]]
                exList+=cont
    exFull=(PageElementType.LIST, exList)
    return [exFull]

def getUniqueLangLink(pi, lang):
    result=None
    for alias in pageTitles:
        if result is None and alias["tgt"]==pi:
            result=alias["path"]
        if alias["tgt"]==pi and alias["lang"]==lang and alias["isPrimary"]:
            result=alias["path"]
            break
    return result

def renderWikiPage(pi, ast, lang, title, langLinks=[], user=None):
    topBar=''
    if pageDetail[pi]["ads"]:
        topBar+=htac("div", {"class": "ad"},
            htac("div", {"style":"font-size:8pt;letter-spacing:3pt;float:left;"}, i18n[lang]["ad"])+
            htac("div", {"style": "margin-top:10px;margin-bottom:10px;"}, random.choice(i18n[lang]["fakeAds"])))
    topBar+=i18n[lang]["notLoggedIn"] if user is None else htc("b",users[user]["name"])
    topBar+=" - "
    topBar+=ha("/switchUser",i18n[lang]["switchUser"])
    topBar+=" - "
    topBar+=ha("/pageHistory?id="+str(pi),i18n[lang]["pageHistory"])
    if authorize(user, "pageprops", lang):
        topBar+=" - "
        topBar+=ha("/pageSettings?page="+str(pi),i18n[lang]["pageSettings"])
    if authorize(user, "admin", lang):
        topBar+=" - "
        topBar+=ha("/bulkEdit?page="+str(pi),i18n[lang]["bulkEdit"])
        topBar+=" - "
        topBar+=ha("/adminTools?page="+str(pi),i18n[lang]["adminTools"])
    topBar+="<br>"
    if 0<len(langLinks):
        topBar+=i18n[lang]["lang"]+": "
        first=True
        for ll in langLinks:
            if not first:
                topBar += " | "
            topBar+=htac('a', {"href":"/"+ll[1]}, ll[0]) if ll[0]!=lang else htc("strong", ll[0])
            first=False
        topBar+='<br>'
    if authorize(user, "edit", lang):
        topBar+=hta('input', {'type':'button', 'onclick':'edit()', 'value':i18n[lang]["editMode"]})
    t=renderHTMLList(ast, lang, pi)
    b=htac('body',{'onload':'init()'},topBar+t)
    head=htc('title', title) + boilerplate + htac("script", {"type":"text/javascript"}, "\n"+
        "i18n="+json.dumps(guii18n[lang])+";\nlang='"+lang+"';\nmod="+json.dumps(authorize(user, "mod", lang))
        )
    return '<!DOCTYPE html>\n'+htc('html', htc('head',head)+b)

def genWikiPage(pi, lang, aka=None, user=None):
    alias=getPagePrimaryAlias(pi, lang)
    if alias is None:
        body=i18n[lang]["untranslated1"]
        body+=htac("a", {"href":"/createAlias?lang="+lang+"&path=wiki/"+str(pi)+"&primary=1"}, i18n[lang]["untranslated2"])
        body+="<br>"
        body+=i18n[lang]["untranslated3"]
        body+=htc("ul","".join([htc("li",x["lang"]+": "+htac("a",{"href":"/"+x["path"]},x["displayName"])) for x in pageTitles if x["tgt"]==pi and x["isPrimary"]]))
        return htmlPage(str(pi), '', body)
    path=alias["path"]
    ns=path.split("/")[0]
    dn=alias["displayName"]
    side=getPageSide(pi)
    titleDisp=[(PageElementType.TEXT, dn)]
    htmlTitleDisp=dn
    if ns != "Main":
        nsDisp = getNamespaceDisplayName(ns, lang)
        htmlTitleDisp='{} ({})'.format(dn, nsDisp)
        titleDisp = [(PageElementType.TEXT, nsDisp+' / ')] + titleDisp
        if aka is not None:
            titleDisp += [(PageElementType.CONTAINER, {}, [(PageElementType.TEXT, i18n[lang]["aka"]+aka)])]
    ast=[(PageElementType.HEADER, 1, titleDisp)]
    quote=[]
    img=[]
    desc=[]
    stinger=[]
    for block in blocks:
        if block["tgt"] == pi and block["lang"] == lang:
            if block["bt"] == BlockType.DESCRIPTION:
                desc=block["content"]
            elif block["bt"] == BlockType.IMAGE:
                img=block["content"]
            elif block["bt"] == BlockType.QUOTE:
                quote=block["content"]
            elif block["bt"] == BlockType.STINGER:
                stinger=block["content"]
    ast+=[(PageElementType.PAGE_BLOCK, BlockType.QUOTE, quote)]
    ast+=[(PageElementType.PAGE_BLOCK, BlockType.IMAGE, img)]
    ast+=[(PageElementType.PAGE_BLOCK, BlockType.DESCRIPTION, desc)]
    if side<2:
        ast+=[
            (PageElementType.SECTION_SEPARATOR,),
            ((PageElementType.HEADER, 2, [(PageElementType.TEXT, i18n[lang]["descriptorExamples"])]) if side==0 else
                (PageElementType.HEADER, 2, [(PageElementType.EMPHASIS, 2, [(PageElementType.TEXT, dn)]), (PageElementType.TEXT, i18n[lang]["descripteeExamples"])])),
            (PageElementType.NEW_EXAMPLE_PLACEHOLDER, side, pi, path),
        ]
        exast=genExamplesAst(pi, lang, PageType.TROPE if side==1 else None, SortType.AZ, False)
        ast+=[(PageElementType.CONTAINER, {"id":"examples"}, exast)]
    if 0<len(stinger):
        ast+=[(PageElementType.SECTION_SEPARATOR,)]
    ast+=[(PageElementType.PAGE_BLOCK, BlockType.STINGER, stinger)]
    langs=sorted({x["lang"] for x in blocks if x["tgt"]==pi}.union({x["lang"] for x in examples if x["src"]==pi or x["tgt"]==pi}).union(
        {x["lang"] for x in pageTitles if x["tgt"]==pi})
    )
    langLinks=[(x,getUniqueLangLink(pi,x)) for x in langs]
    return renderWikiPage(pi, ast, lang, htmlTitleDisp, langLinks, user)

def rewriteLinks(ast, allowRed):
    if type(ast)==list:
        cont=[]
        rl=set()
        nrl=set()
        for elem in ast:
            c,r,n = rewriteLinks(elem, allowRed)
            cont.append(c)
            rl=rl.union(r)
            nrl=nrl.union(n)
        return (cont,rl,nrl)
    elif type(ast)==tuple:
        if ast[0] in [PageElementType.TEXT, PageElementType.ESCAPE, PageElementType.WEBLINK, PageElementType.LINE_COMMENT, PageElementType.PARAGRAPH_BREAK,
            PageElementType.FORCE_NEWLINE]:
            return (ast, set(), set())
        elif ast[0]==PageElementType.LINK:
            link = ast[1]
            if not '/' in link:
                link="Main/"+link
            alias = getAliasForPath(link)
            if alias is not None:
                pi=alias["tgt"]
                if pageDetail[pi]["fakeRedlink"] and not allowRed:
                    return (ast, set(), {link})
                else:
                    return ((PageElementType.RESOLVED_LINK, pi, alias["lang"], ast[2]), {pi}, set())
            else:
                return (ast, set(), {link})
        elif ast[0] in [PageElementType.LIST, PageElementType.LISTITEM, PageElementType.SPOILER, PageElementType.QUOTE, PageElementType.STRIKE]:
            c,r,n = rewriteLinks(ast[1], allowRed)
            return ((ast[0], c), r, n)
        elif ast[0] in [PageElementType.EMPHASIS, PageElementType.NOTE]:
            c,r,n = rewriteLinks(ast[2], allowRed)
            return ((ast[0], ast[1], c), r, n)
        else:
            raise Exception("don't know how to replace links in {}".format(ast[0]))
    else:
        raise Exception("don't know how to replace links in {}".format(ast))

def makeExample(src, tgt, lang, asym, side, content, play, hide, lock, embargo, resolvedLinks, unresolvedLinks):
    now=time.time_ns()
    ex={"src": src, "tgt": tgt, "lang": lang, "content": content, "asymmetric": asym, "ctime":now, "mtime":now, "playWith": play,
        "hide": hide is True, "lock": lock is True, "embargo": embargo is True, "resolvedLinks": resolvedLinks, "unresolvedLinks": unresolvedLinks}
    if asym:
        ex["backContent"]=content
    return ex

def updateExample(ei, src, tgt, asym, side, content, play, hide, lock, embargo, extraFields):
    now=time.time_ns()
    ex=examples[ei]
    ex["src"]=src
    ex["tgt"]=tgt
    ex["mtime"]=now
    ex["asymmetric"]=asym
    ex["playWith"]=play
    if hide is not None:
        ex["hide"]=hide
    if lock is not None:
        ex["lock"]=lock
    if embargo is not None:
        ex["embargo"]=embargo
    if asym:
        if side==0:
            ex["content"]=content
        else:
            ex["backContent"]=content
    else:
        ex["content"]=content
        if "backContent" in ex:
            del ex["backContent"]
    ex|=extraFields

def hiddenExampleExists(src, tgt, play):
    for ex in examples:
        if ex["hide"] and ex["src"]==src and ex["tgt"]==tgt and ex["playWith"]==play:
            return True
    return False

def embargoedExampleExists(src, tgt):
    for ex in examples:
        if ex["embargo"] and ex["src"]==src and ex["tgt"]==tgt:
            return True
    return False

def hasImage(ast):
    if type(ast)==list:
        for elem in ast:
            if hasImage(elem):
                return True
    elif type(ast)==tuple:
        ty=ast[0]
        if ty==PageElementType.IMAGE or ty==PageElementType.CAPTIONED_IMAGE:
            return True
    else:
        raise Exception("Not a list or tuple: {}".format(ast))
    return False

def hresp(code, content):
    if dict==type(content):
        return {"type": "json", "code": code, "content": json.dumps(content)}
    return {"type": "text", "code": code, "content": content}

def badreq(err):
    return hresp(hrc.BAD_REQUEST, {"error":err})

def badauth(lang):
    return hresp(hrc.FORBIDDEN, i18n[lang]["notAuthorized"])

def redirect(loc):
    return {"type": "text", "code": hrc.FOUND, "content": "", "headers": {"Location":loc}}

def splitUrl(path):
    paramp=path.split('?')
    path=paramp[0]
    if len(paramp)>1:
        params={x:y[-1] for x,y in parse_qs(paramp[1]).items()}
    else:
        params={}
    return (path,params)

def genListPage(side, lang):
    text='<html><body><ul>'
    for alias in pageTitles:
        if alias["lang"]==lang and getPageSide(alias["tgt"]) == side:
            text+='<li><a href="/wiki/'+str(alias["tgt"])+'?lang='+lang+'">'+html.escape(alias["displayName"])+'</a></li>'
    text+='</ul></body></html>'
    return {"code": hrc.OK, "type": "text", "content":text}

def radioGroup(name, mapping, selectedItem):
    return ''.join([hta("input", {"type":"radio", "name":name, "id":name+"_"+x, "value":x, "required": "true"} | ({"checked": "true"} if x==selectedItem else {}))+
        htac("label", {"for":name+"_"+x}, y) for x,y in mapping.items()])

def checkbox(name, label, checked):
    return (hta("input", {"type": "checkbox", "name": name, "id": name} | ({} if not checked else {"checked": "true"}))+
        htac("label", {"for": name}, label))

def htmlPage(title, head, body):
    return '<!DOCTYPE html>\n'+htc('html', htc('head',htc('title', title)+head)+htc('body',body))

def genCreatePageForm(path, lang):
    body=(htc('h1',i18n[lang]["createPage"])+
        htac("form", {"method": "post", "action": "/createPage"},
            radioGroup("pageType", i18n[lang]["pageType"], None)+
            hta("br",{})+
            htac("label", {"for": "path"}, i18n[lang]["newPagePath"])+
            hta("input", {"id": "path", "name": "path", "value": path, "size": "50", "required": "true"})+
            hta("br",{})+
            htac("label", {"for": "displayName"}, i18n[lang]["newPageDisplayName"])+
            hta("input", {"id": "displayName", "name": "displayName", "value": splitWikiWord(path.split('/')[-1]), "size": "50", "required": "true"})+
            hta("br",{})+
            hta("input", {"type": "submit"})
        ))
    return htmlPage(i18n[lang]["createPage"], '', body)

def genCreateAliasForm(path, lang, isPrimary):
    head=htc('title', i18n[lang]["createAlias"])
    body=(htc('h1',i18n[lang]["createAlias"])+
        htac("form", {"method": "post", "action": "/createAlias"},
            hta("input", {"id": "primary", "name": "primary", "type": "checkbox"}|({"checked": "true"} if isPrimary else {}))+
            htac("label", {"for": "primary"}, i18n[lang]["aliasPrimary"])+
            hta("br",{})+
            htac("label", {"for": "target"}, i18n[lang]["aliasTarget"])+
            hta("input", {"id": "target", "name": "target", "value": path, "size": "50", "required": "true"})+
            hta("br",{})+
            htac("label", {"for": "path"}, i18n[lang]["aliasPath"])+
            hta("input", {"id": "path", "name": "path", "size": "50", "required": "true"})+
            hta("br",{})+
            htac("label", {"for": "displayName"}, i18n[lang]["newPageDisplayName"])+
            hta("input", {"id": "displayName", "name": "displayName", "size": "50", "required": "true"})+
            hta("br",{})+
            hta("input", {"id": "lang", "name": "lang", "type": "hidden", "value": lang})+
            hta("input", {"type": "submit"})
        ))
    return '<!DOCTYPE html>\n'+htc('html', htc('head',head)+htc('body',body))

def genSwitchUserPage(currUser):
    body="This is a demo app, you can freely switch to any user at will.<br>"+"<br>".join(
        [(ha("/switchUser?user="+x["name"],x["name"]) if i!=currUser else htc("b",x["name"]))+
            " ("+ha("/userHistory?id="+str(i),"history")+") - "+x["description"] for i,x in enumerate(users)])
    return htmlPage('Switch User', '', body)

def genPageSettingsPage(pi, lang):
    body="Page settings for "+getPageDisplayName(pi, "en")+"<br>"
    pd=pageDetail[pi]
    body+=htac("form", {"method": "post", "action": "pageSettings"},
        hta("input", {"type": "hidden", "name": "page", "value": str(pi)})+
        checkbox("ads", "Ads", pd["ads"])+"<br>"+
        checkbox("locked", "Locked", pd["locked"])+"<br>"+
        checkbox("fakeRedlink", "Fake redlink", pd["fakeRedlink"])+"<br>"+
        radioGroup("pageType", i18n[lang]["pageType"], str(pd["pageType"].value))+"<br>"+
        hta("input", {"type": "submit"})
    )
    return htmlPage('Page settings', '', body)

def genAdminTools(pi):
    body="Merge page into"+"<br>"
    pd=pageDetail[pi]
    body+=htac("form", {"method": "post", "action": "mergePage"},
        hta("input", {"type": "hidden", "name": "page", "value": str(pi)})+
        hta("input", {"name": "target"})+
        hta("input", {"type": "submit"})
    )
    return htmlPage('Admin tools', '', body)

def genBulkEditForm(pi):
    body=""
    body+=htac("form", {"method": "post", "action": "bulkEdit"},
        htac("label", {"for": "exTarget"}, "Examples with links to ")+
        hta("input", {"name": "exTarget", "id": "exTarget"} | ({"value": getPagePrimaryPath(pi, "en")} if pi is not None else {}))+
        hta("input", {"type": "submit", "value": "Search"})
    )
    return htmlPage('Bulk edit', '', body)

def parseBulkEditParams(data, lang):
    exs=[]
    selexs=set()
    hide=None
    for k in data.keys():
        if k.startswith("excont"):
            isBack=False
            ka=k
            if k.endswith(".back"):
                isBack=True
                ka=k[:-5]
            ei=tryParseInt(ka[6:])
            if ei is None or not 0<=ei<len(examples):
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format("excont"))
            if type(data[k]) != list:
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format("excont"+str(ei)))
            if len(data[k]) != 1:
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format("excont"+str(ei)))
            cont=data[k][0]
            if type(cont) != str:
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format("excont"+str(ei)))
            cont=cont.replace("\r","")
            ast=parseWiki(cont,0)[0]
            ast, rl, ul = rewriteLinks(ast, True)
            exs.append({"id": ei, "isBack": isBack, "content": ast, "rawContent": cont, "resolvedLinks": rl, "unresolvedLinks": ul, "sel": False})
        if k.startswith("exsel"):
            ei=tryParseInt(k[5:])
            if ei is None or not 0<=ei<len(examples):
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format("exsel"))
            sel=getBooleanFormParam(data, k)
            if sel is None:
                return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidParam"].format(k))
            if sel:
                selexs.add(ei)
    moveEnabled=getBooleanFormParam(data,"move")
    hideAll=getBooleanFormParam(data,"hideAll")
    unhideAll=getBooleanFormParam(data,"unhideAll")
    if hideAll and unhideAll:
        return None,hresp(hrc.BAD_REQUEST, i18n[lang]["hideVsUnhide"].format(k))
    if hideAll:
        hide=True
    if unhideAll:
        hide=False
    move=getStrFormParam(data, "moveAll") if moveEnabled else None
    if move is not None:
        pi=getPageIndex(move)
        if pi==-1:
            return None,hresp(hrc.BAD_REQUEST, i18n[lang]["invalidPage"])
        if getPageSide(pi)>=2:
            return None,hresp(hrc.BAD_REQUEST, i18n[lang]["noExamplesAllowed"])
    for ex in exs:
        if ex["id"] in selexs:
            ex["sel"]=True
    return {"exs":exs, "move":move, "hide":hide},None

def genBulkEditResults(pi, offset, exTarget):
    eis0=[]
    for i,ex in enumerate(examples):
        if ex["src"]==pi or ex["tgt"]==pi or pi in ex["resolvedLinks"]:
            eis0.append(i)
    eis=eis0[offset:offset+MAX_RESULTS_PER_PAGE]
    exedits=""
    body=""
    if len(eis0)>MAX_RESULTS_PER_PAGE:
        body += "go to page (changes will be lost):"
        for i in range(math.ceil(len(eis0)/MAX_RESULTS_PER_PAGE)):
            fromTo=str(i*MAX_RESULTS_PER_PAGE)+"-"+str(min((i+1)*MAX_RESULTS_PER_PAGE,len(eis0))-1)
            if i*MAX_RESULTS_PER_PAGE == offset:
                body += " "+fromTo
            else:
                body += " "+htac("form", {"method": "post", "action": "bulkEdit", "style": "display: inline;"},
                    htac("input", {"type": "hidden", "name": "offset", "value": str(i*MAX_RESULTS_PER_PAGE)}, "")+
                    htac("input", {"type": "hidden", "name": "exTarget", "value": exTarget}, "")+
                    htac("input", {"type": "submit", "value": fromTo}, "")
                )
        body+="<br><br>"
    for ei in eis:
        ex=examples[ei]
        exedits+=htac("input", {"type":"checkbox", "checked": "true", "name": "exsel"+str(ei)},"")
        exedits+="example of "+getPagePrimaryPath(ex["src"],"en")+" in "+getPagePrimaryPath(ex["tgt"],"en")+"<br>"+htac(
            "textarea", {"id": "exedit"+str(ei), "name": "excont"+str(ei), "style": "width: 80%; height: 300px;"},
            renderWikiList(ex["content"]))+"<br>"
        if ex["asymmetric"]:
            exedits+="example of "+getPagePrimaryPath(ex["src"],"en")+" in "+getPagePrimaryPath(ex["tgt"],"en")+" (reverse side)<br>"+htac(
                "textarea", {"id": "exedit"+str(ei)+".back", "name": "excont"+str(ei)+".back", "style": "width: 80%; height: 300px;"},
                renderWikiList(ex["backContent"]))+"<br>"
    exedits+=htac("input", {"type": "checkbox", "id": "hideAll", "name": "hideAll"}, "")
    exedits+=htac("label", {"for": "hideAll"}, "Hide selected examples")+"<br>"
    exedits+=htac("input", {"type": "checkbox", "id": "unhideAll", "name": "unhideAll"}, "")
    exedits+=htac("label", {"for": "unhideAll"}, "Unhide selected examples")+"<br>"
    exedits+=htac("input", {"type": "checkbox", "id": "moveAll", "name": "move"}, "")
    exedits+=htac("label", {"for": "moveAll"}, "Move selected examples to ")
    exedits+=htac("input", {"id": "moveAll", "name": "moveAll"}, "")+"<br>"
    body+=htac("form", {"method": "post", "action": "bulkEditPreview"}, exedits+hta("input", {"type": "submit", "value": "preview"}))
    return htmlPage('Bulk edit', '', body)

def genBulkEditPreview(bep, lang):
    exedits=""
    for ex in bep["exs"]:
        ei=ex["id"]
        oex=examples[ei]
        suffix=".back" if ex["isBack"] else ""
        exedits+=htc("li", "example of "+getPagePrimaryPath(oex["src"],"en")+" in "+getPagePrimaryPath(oex["tgt"],"en")+(" (reverse side)" if ex["isBack"] else "")+
            (" (Will be hidden)" if bep["hide"] and ex["sel"] and not oex["hide"] else "")+
            (" (Will be unhidden)" if bep["hide"] is False and ex["sel"] and oex["hide"] else "")+
            ((" (Will be moved to "+bep["move"]+")") if bep["move"] is not None else "")+
            "<br>"+htac("input", {"type": "hidden", "name": "excont"+str(ei)+suffix, "value": ex["rawContent"]}, "")+
            (htac("input", {"type": "hidden", "name": "exsel"+str(ei), "value": "on"}, "") if ex["sel"] and not ex["isBack"] else "")+
            renderHTMLList(ex["content"], lang, None)+"<br>")
    if bep["move"] is not None:
        exedits+=htac("input", {"type": "hidden", "name": "move", "value": "on"}, "")
        exedits+=htac("input", {"type": "hidden", "name": "moveAll", "value": bep["move"]}, "")
    if bep["hide"]:
        exedits+=htac("input", {"type": "hidden", "name": "hideAll", "value": "on"}, "")
    if bep["hide"] is False:
        exedits+=htac("input", {"type": "hidden", "name": "unhideAll", "value": "on"}, "")
    body=htac("form", {"method": "post", "action": "bulkEditSave"}, htc("ul",exedits)+hta("input", {"type": "submit", "value": "save"}))
    return htmlPage('Bulk edit', css_boilerplate, body)

def handleGet(path, user):
    lang = None
    path,params=splitUrl(path)
    if "lang" in params:
        lang=params["lang"]
    pp=path.split('/')
    if len(pp)>2 and pp[1] in namespaces:
        path='/'.join(pp[1:3])
        alias=getAliasForPath(path)
        if alias is None:
            return redirect("/createPage?path="+path)
        if lang is None:
            lang = alias["lang"]
        if not alias["isPrimary"]:
            primAlias = getPagePrimaryAlias(alias["tgt"], lang)
            return redirect("/"+primAlias["path"]+"?from="+alias["path"])
        newpath='/wiki/'+str(alias["tgt"])
        print('rewrite {} to {}'.format(path, newpath))
        path=newpath
        pp=path.split('/')
    if lang is None:
        lang = "en"
    if path=='/':
        return hresp(hrc.OK, '<html><body><a href="/tropes">Tropes</a><br><a href="/works">Works</a></body></html>')
    elif path=='/nuke': # for use by automated tests only
        initDB()
        addTestUsers()
        return hresp(hrc.OK, "KABOOOOOOOM... whooooooooosssssssh...")
    elif path=='/tropes':
        return genListPage(0, lang)
    elif path=='/works':
        return genListPage(1, lang)
    elif path.startswith('/api/v1/'):
        if len(pp)>=4:
            apiName=pp[3]
            if apiName=='example' and len(pp)>=5:
                if not "side" in params:
                    return badreq("missing side parameter")
                side=tryParseInt(params["side"])
                if side is None or not 0<=side<=1:
                    return badreq("invalid side")
                ei=int(pp[4])
                if ei<0 or ei>=len(examples):
                    return badreq("example not found")
                ex=examples[ei]
                tAlias=getPagePrimaryAlias(ex["src"], lang)
                wAlias=getPagePrimaryAlias(ex["tgt"], lang)
                exj={"id":ei, "linkSource":tAlias["path"], "linkTarget":wAlias["path"], "content":renderWiki(ex["content" if side==0 or not ex["asymmetric"] else "backContent"]),
                    "asym":ex["asymmetric"], "play":ex["playWith"].value, "hide":ex["hide"], "lock":ex["lock"]}
                if authorize(user, "mod", lang):
                    exj["embargo"]=ex["embargo"]
                return hresp(hrc.OK, exj)
            elif pp[3]=='typeahead':
                if not "query" in params:
                    return badreq("missing query parameter")
                if not "side" in params:
                    return badreq("missing side parameter")
                query=params["query"].lower()
                found=[]
                side=tryParseInt(params["side"])
                if side is None or not 0<=side<=1:
                    return badreq("invalid side")
                for alias in pageTitles:
                    if alias["lang"]==lang and query in alias["path"].lower() or query in alias["displayName"].lower():
                        if getPageSide(alias["tgt"])==side:
                            found.append({"id": alias["tgt"], "name": alias["path"], "displayName": alias["displayName"]})
                    if len(found)>=10:
                        break
                return hresp(hrc.OK,{"results": found})
            elif pp[3]=='page':
                if len(pp)>=7 and pp[5]=='block':
                    pi=tryParseInt(pp[4])
                    if pi is None or not 0<=pi<len(pageDetail):
                        return badreq("invalid page index")
                    bt=tryParseInt(pp[6])
                    if bt is None or not 1<=bt<=4:
                        return badreq("invalid block type")
                    bt=BlockType(bt)
                    bi=getBlockIndex(pi, lang, bt)
                    block = [] if bi==-1 else blocks[bi]["content"]
                    return hresp(hrc.OK, {"content":renderWiki(block)})
                elif len(pp)>=6 and pp[5]=='exampleHtml':
                    pi=tryParseInt(pp[4])
                    if pi is None or not 0<=pi<len(pageDetail):
                        return badreq("invalid page index")
                    f=PageType.TROPE
                    if "filter" in params:
                        filt=params["filter"]
                        if filt=="tropes":
                            pass
                        elif filt=="all":
                            f=None
                        elif filt=="ymmv":
                            f=PageType.YMMV
                        elif filt=="trivia":
                            f=PageType.TRIVIA
                        else:
                            return badreq("invalid filter type")
                    s=SortType.AZ
                    if "sort" in params:
                        srt=params["sort"]
                        if srt=="az":
                            pass
                        elif srt=="ctimeUp":
                            s=SortType.CTIME_UP
                        elif srt=="ctimeDn":
                            s=SortType.CTIME_DOWN
                        elif srt=="mtimeUp":
                            s=SortType.MTIME_UP
                        elif srt=="mtimeDn":
                            s=SortType.MTIME_DOWN
                        else:
                            return badreq("invalid sort type")
                    addHidden=False
                    if "addHidden" in params:
                        if params["addHidden"]=="false":
                            pass
                        elif params["addHidden"]=="true":
                            addHidden=True
                        else:
                            badreq(i18n[lang]["invalidParam"].format("addHidden"))
                    ast=genExamplesAst(pi, lang, f, s, addHidden)
                    return hresp(hrc.OK, renderHTMLList(ast, lang, pi))
        return badreq("get: unknown API")
    elif path=="/createPage":
        return hresp(hrc.OK, genCreatePageForm(params["path"] if "path" in params else "", lang))
    elif path=="/createAlias":
        return hresp(hrc.OK, genCreateAliasForm(params["path"] if "path" in params else "", lang, True if "primary" in params else False))
    elif path=="/switchUser":
        if "user" in params:
            user=params["user"]
            if not user in [x["name"] for x in users]:
                return hresp(hrc.BAD_REQUEST, "unknown user")
            resp=redirect("/switchUser")
            resp["cookies"]={"userid":params["user"]}
            return resp
        return hresp(hrc.OK, genSwitchUserPage(user))
    elif pp[1]=="pageSettings":
        if not authorize(user, "pageprops", lang):
            return badauth(lang)
        if not "page" in params:
            return hresp(hrc.BAD_REQUEST, i18n[lang]["missingParam"].format("page"))
        pi=tryParseInt(params["page"])
        if pi is None or not 0<=pi<len(pageDetail):
            return hresp(hrc.BAD_REQUEST, "invalid page index")
        return hresp(hrc.OK, genPageSettingsPage(pi, lang))
    elif path.startswith('/wiki/'):
        wi=int(pp[2])
        if wi<0 or wi>=len(pageDetail):
            return hresp(hrc.NOT_FOUND, "Unknown page")
        aka = None
        if "from" in params:
            alias=getAliasForPath(params["from"])
            if alias is not None:
                aka = alias["displayName"]
        text=genWikiPage(wi, lang, aka, user)
        return hresp(hrc.OK, text)
    elif path=="/pageHistory":
        if not "id" in params:
            return hresp(hrc.BAD_REQUEST, i18n[lang]["missingParam"].format("id"))
        pi=tryParseInt(params["id"])
        if pi is None or not 0<=pi<len(pageDetail):
            return hresp(hrc.BAD_REQUEST, "invalid page index")
        hist=getPageHistory(pi)
        text=htc("ul","".join([formatHistory(x) for x in hist])) if 0<len(hist) else "Empty history"
        return hresp(hrc.OK, text)
    elif path=="/userHistory":
        if not "id" in params:
            return hresp(hrc.BAD_REQUEST, i18n[lang]["missingParam"].format("id"))
        pi=tryParseInt(params["id"])
        if pi is None or not 0<=pi<len(users):
            return hresp(hrc.BAD_REQUEST, "invalid user")
        hist=getUserHistory(pi)
        text=htc("ul","".join([formatHistory(x) for x in hist])) if 0<len(hist) else "Empty history"
        return hresp(hrc.OK, text)
    elif path=="/adminTools":
        if not "page" in params:
            return hresp(hrc.BAD_REQUEST, i18n[lang]["missingParam"].format("page"))
        pi=tryParseInt(params["page"])
        if pi is None or not 0<=pi<len(pageDetail):
            return hresp(hrc.BAD_REQUEST, "invalid page index")
        return hresp(hrc.OK, genAdminTools(pi))
    elif path=="/bulkEdit":
        pi=None
        if "page" in params:
            pi=tryParseInt(params["page"])
            if pi is None or not 0<=pi<len(pageDetail):
                return hresp(hrc.BAD_REQUEST, "invalid page index")
        return hresp(hrc.OK, genBulkEditForm(pi))
    elif path=="/favicon.ico":
        return hresp(hrc.OK, "File not found")  # deliberately using OK instead of NOT_FOUND to avoid extra log on firefox console
    else:
        return hresp(hrc.BAD_REQUEST, "wtf")

def getBooleanFormParam(data, name):
    result=False
    if name in data:
        if 1 != len(data[name]):
            return None
        if data[name][0] == "on":
            result=True
    return result

def getIntFormParam(data, name):
    if not name in data:
        return None
    if 1 != len(data[name]):
        return None
    return tryParseInt(data[name][0])

def getStrFormParam(data, name):
    if not name in data:
        return None
    if 1 != len(data[name]):
        return None
    return data[name][0]

def handlePost(path, data, user):
    lang=None
    path,params=splitUrl(path)
    pp=path.split('/')
    if "lang" in params:
        lang=params["lang"]
    if lang is None:
        lang="en"
    try:
        if path.startswith('/api/v1/'):
            if len(pp)>=4:
                apiName=pp[3]
                if apiName=='example':
                    if not authorize(user, "edit", lang):
                        return badauth(lang)
                    if not "linkSource" in data:
                        return badreq(i18n[lang]["missingParam"].format("linkSource"))
                    elif not "linkTarget" in data:
                        return badreq(i18n[lang]["missingParam"].format("linkTarget"))
                    elif not "pageSide" in data:
                        return badreq(i18n[lang]["missingParam"].format("pageSide"))
                    elif not "content" in data:
                        return badreq(i18n[lang]["missingParam"].format("content"))
                    elif not "play" in data:
                        return badreq(i18n[lang]["missingParam"].format("play"))
                    elif 0==len(data["linkSource"]):
                        return badreq(i18n[lang]["emptyParam"].format("linkSource"))
                    elif 0==len(data["linkTarget"]):
                        return badreq(i18n[lang]["emptyParam"].format("linkTarget"))
                    elif 0==len(data["content"]):
                        return badreq(i18n[lang]["emptyParam"].format("content"))
                    elif 0==len(data["play"]):
                        return badreq(i18n[lang]["emptyParam"].format("play"))
                    pageSide=tryParseInt(data["pageSide"])
                    if pageSide is None:
                        return badreq(i18n[lang]["invalidParam"].format("pageSide"))
                    try:
                        Side(pageSide)
                    except:
                        return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("pageSide")))
                    play=tryParseInt(data["play"])
                    if pageSide is None:
                        return badreq(i18n[lang]["invalidParam"].format("pageSide"))
                    try:
                        play=PlayingWithType(play)
                    except:
                        return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("play")))
                    ti=getPageIndex(data["linkSource"])
                    wi=getPageIndex(data["linkTarget"])
                    asym=False
                    if "asym" in data:
                        if not type(data["asym"])==bool:
                            return badreq(i18n[lang]["invalidParam"].format("asym"))
                        asym=data["asym"]
                    hide=None
                    if "hide" in data:
                        if not type(data["hide"])==bool:
                            return badreq(i18n[lang]["invalidParam"].format("hide"))
                        hide=data["hide"]
                    modAuth=authorize(user, "mod", lang)
                    lock=None
                    if "lock" in data:
                        if not type(data["lock"])==bool:
                            return badreq(i18n[lang]["invalidParam"].format("lock"))
                        if not modAuth:
                            return hresp(hrc.FORBIDDEN, {"error":i18n[lang]["notAuthorized"]})
                        lock=data["lock"]
                    embargo=None
                    if "embargo" in data:
                        if not type(data["embargo"])==bool:
                            return badreq(i18n[lang]["invalidParam"].format("embargo"))
                        if not modAuth:
                            return hresp(hrc.FORBIDDEN, {"error":i18n[lang]["notAuthorized"]})
                        embargo=data["embargo"]
                    if ti==-1:
                        return hresp(hrc.BAD_REQUEST, {"error":i18n[lang]["invalidPagePleaseCreate"], "badLinks": [data["linkSource"]]})
                    if wi==-1:
                        return hresp(hrc.BAD_REQUEST, {"error":i18n[lang]["invalidPagePleaseCreate"], "badLinks": [data["linkTarget"]]})
                    if pageIsFakeRedlink(ti, user, lang):
                        return badreq(i18n[lang]["invalidExSrc"].format(data["linkSource"]))
                    if pageIsFakeRedlink(wi, user, lang):
                        return badreq(i18n[lang]["invalidExSrc"].format(data["linkTarget"]))
                    if getPageSide(ti) != 0:
                        return badreq(i18n[lang]["invalidExSrc"].format(data["linkSource"]))
                    if getPageSide(wi) != 1:
                        return badreq(i18n[lang]["invalidExTgt"].format(data["linkTarget"]))
                    ei=None
                    if len(pp)>=5:
                        ei=int(pp[4])
                    cont=data["content"]
                    if ei is not None and (ei<0 or ei>=len(examples)):
                        return badreq(i18n[lang]["invalidParam"].format("exampleId"))
                    if pageLocked(ti, user, lang):
                        return badreq(i18n[lang]["pageLocked"].format(data["linkSource"]))
                    if pageLocked(wi, user, lang):
                        return badreq(i18n[lang]["pageLocked"].format(data["linkTarget"]))
                    if ei is not None:
                        oti=examples[ei]["src"]
                        owi=examples[ei]["tgt"]
                        if pageLocked(oti, user, lang):
                            return badreq(i18n[lang]["pageLocked"].format(getPagePrimaryPath(oti, lang)))
                        if pageLocked(owi, user, lang):
                            return badreq(i18n[lang]["pageLocked"].format(getPagePrimaryPath(owi, lang)))
                    ast=parseWiki(cont,0)[0]
                    hasimg=hasImage(ast)
                    if hasimg:
                        return badreq(i18n[lang]["blockNotAllowedImage"])
                    ast, rl, ul = rewriteLinks(ast, authorize(user, "edit.addRedlink", lang))
                    if "save" in data and data["save"]:
                        if 0<len(ul):
                            return hresp(hrc.BAD_REQUEST, {"error":i18n[lang]["invalidPagePleaseCreate"].format(", ".join(ul)), "badLinks": list(ul)})
                        if ei is None:  #new example
                            ex=makeExample(ti, wi, lang, asym, pageSide, ast, play, hide, lock, embargo, rl, ul)
                            if ex in examples:
                                return badreq(i18n[lang]["dupeEx"])
                            if not modAuth and hiddenExampleExists(ti, wi, play):
                                return hresp(hrc.FORBIDDEN, {"error": i18n[lang]["hasHiddenExample"]})
                            if not modAuth and embargoedExampleExists(ti, wi,):
                                return hresp(hrc.FORBIDDEN, {"error": i18n[lang]["hasEmbargoedExample"]})
                            history.append({"event": "addExample", "id":ei, "wi":wi, "ti":ti, "content":ast, "user": user, "time": time.time_ns()})
                            examples.append(ex)
                            ei=len(examples)-1
                        else:   #exsting example
                            oex=examples[ei]
                            if oex["lock"] and not modAuth:
                                return hresp(hrc.FORBIDDEN, {"error": i18n[lang]["exLocked"]})
                            history.append({"event": "editExample", "id":ei, "wi":wi, "ti":ti, "content":ast, "user": user, "time": time.time_ns()})
                            oti=oex["src"]
                            owi=oex["tgt"]
                            oplay=oex["playWith"]
                            if oti != ti or owi != wi or oplay != play: # move counts as delete+add
                                if not modAuth and hiddenExampleExists(ti, wi, play):
                                    return hresp(hrc.FORBIDDEN, {"error": i18n[lang]["hasHiddenExample"]})
                            if oti != ti or owi != wi:
                                if not modAuth and embargoedExampleExists(ti, wi) or embargoedExampleExists(oti, owi):
                                    return hresp(hrc.FORBIDDEN, {"error": i18n[lang]["hasEmbargoedExample"]})
                            updateExample(ei, ti, wi, asym, pageSide, ast, play, hide, lock, embargo, {"resolvedLinks": rl, "unresolvedLinks": ul})
                    linkPreview=[(PageElementType.RESOLVED_LINK, ti, lang, None) if pageSide==1 else
                        (PageElementType.EMPHASIS,2,[(PageElementType.RESOLVED_LINK, wi, lang, None)]),(PageElementType.TEXT,": ")]
                    currentPage=ti if pageSide==0 else wi
                    return hresp(hrc.OK, {"id":ei,"content":renderHTMLList(linkPreview+tieExample(ast, lang, play, hide), lang, currentPage)})
                elif apiName=='page' and len(pp)>=7:
                    if not authorize(user, "edit", lang):
                        return badauth(lang)
                    pi=tryParseInt(pp[4])
                    if pi is None or not 0<=pi<len(pageDetail):
                        return badreq(i18n[lang]["invalidParam"].format("pageIndex"))
                    if pageLocked(pi, user, lang):
                        return badreq(i18n[lang]["pageLocked"].format(getPagePrimaryPath(pi, lang)))
                    bt=tryParseInt(pp[6])
                    if bt is None or not 1<=bt<=4:
                        return badreq(i18n[lang]["invalidParam"].format("blockType"))
                    bt=BlockType(bt)
                    if not "content" in data:
                        return badreq(i18n[lang]["missingParam"].format("content"))
                    cont=data["content"]
                    ast=parseWiki(cont,0)[0]
                    hasimg=hasImage(ast)
                    if hasimg:
                        if not bt==BlockType.IMAGE:
                            return badreq(i18n[lang]["blockNotAllowedImage"])
                    else:
                        if bt==BlockType.IMAGE:
                            return badreq(i18n[lang]["blockMissingImage"])
                    ast, rl, ul = rewriteLinks(ast, authorize(user, "edit.addRedlink", lang))
                    if "save" in data and data["save"]:
                        if 0<len(ul):
                            return hresp(hrc.BAD_REQUEST, {"error":i18n[lang]["invalidPagePleaseCreate"].format(", ".join(ul)), "badLinks": list(ul)})
                        bi=getBlockIndex(pi, lang, bt)
                        if bi==-1:
                            history.append({"event": "addBlock", "id":len(blocks), "tgt":pi, "bt":bt, "content":ast, "user": user, "time": time.time_ns()})
                            blocks.append({"tgt": pi, "lang": lang, "bt": bt, "content": ast})
                        else:
                            history.append({"event": "editBlock", "id":bi, "lang": lang, "content":ast, "user": user, "time": time.time_ns()})
                            blocks[bi]["content"]=ast
                    return hresp(hrc.OK, {"content":renderHTMLList(ast, lang, pi)})
            return badreq("unknown API")
        elif path=="/createPage":
            if not authorize(user, "edit", lang):
                return badauth(lang)
            if not "path" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("path")))
            if 1 != len(data["path"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            if not "pageType" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("pageType")))
            if 1 != len(data["pageType"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("pageType")))
            if not "displayName" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("displayName")))
            if 1 != len(data["displayName"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("displayName")))
            path=data["path"][0]
            if 0==len(path):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("path")))
            displayName=data["displayName"][0]
            if 0==len(displayName):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("displayName")))
            pageType=tryParseInt(data["pageType"][0])
            if pageType is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("pageType")))
            try:
                pageType=PageType(pageType)
            except:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("pageType")))
            pi=getPageIndex(path)
            if pi != -1:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["pageAlreadyExists"].format(path)))
            pp=path.split('/')
            if len(pp) != 2:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["pathNeedsOneSlash"]))
            if len(pp[0])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            if len(pp[1])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            side=pageTypeToSide[pageType]
            if side == 0 and not authorize(user, "create.descriptor", lang):
                return badauth(lang)
            if side == 2 and not authorize(user, "create.admin", lang):
                return badauth(lang)
            nsForSide=getNamespacesForSide(side, lang)
            if not pp[0] in nsForSide:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["wrongNsForSide"]+", ".join(nsForSide)))
            pi=createPage(path, pageType)
            pageTitles.append({"tgt": pi, "path": path, "displayName": displayName, "lang": lang, "isPrimary": True})
            return redirect(path)
        elif path=="/createAlias":
            if not authorize(user, "edit", lang):
                return badauth(lang)
            if not "lang" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["en"].format("lang")))
            if 1 != len(data["lang"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["en"].format("lang")))
            lang=data["lang"][0]
            if not lang in i18n:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["en"].format("lang")))

            if not "target" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("target")))
            if 1 != len(data["target"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("target")))
            target=data["target"][0]
            if 0==len(target):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("target")))
            pp=target.split('/')
            if len(pp) != 2:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["pathNeedsOneSlash"]+": "+escapeText(target)))
            if len(pp[0])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("target")))
            if len(pp[1])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("target")))
            if pp[0]=="wiki":
                tgt=tryParseInt(pp[1])
                if tgt is None or not 0<=tgt<len(pageDetail):
                    return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidPage"]+": "+escapeText(target)))
            else:
                tgt=getPageIndex(target)
            if tgt == -1:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidPage"]+": "+escapeText(target)))

            if not "path" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("path")))
            if 1 != len(data["path"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            path=data["path"][0]
            if 0==len(path):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("path")))
            pp=path.split('/')
            if len(pp) != 2:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["pathNeedsOneSlash"]))
            if len(pp[0])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            if len(pp[1])==0:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("path")))
            pi=getPageIndex(path)
            if pi != -1:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["pageAlreadyExists"].format(path)))
            side=pageDetail[pi]["side"]
            nsForSide=getNamespacesForSide(side, lang)
            if not pp[0] in nsForSide:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["wrongNsForSide"]+", ".join(nsForSide)))
            if side == 0 and not authorize(user, "create.descriptor", lang):
                return badauth(lang)
            if side == 2 and not authorize(user, "create.admin", lang):
                return badauth(lang)

            if not "displayName" in data:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["missingParam"].format("displayName")))
            if 1 != len(data["displayName"]):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("displayName")))
            displayName=data["displayName"][0]
            if 0==len(displayName):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["emptyParam"].format("displayName")))

            isPrimary=False
            if "primary" in data:
                primary=data["primary"]
                if 1 != len(primary):
                    return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("primary")))
                primary=primary[0]
                if primary=="on":
                    isPrimary=True

            pageTitles.append({"tgt": tgt, "path": path, "displayName": displayName, "lang": lang, "isPrimary": isPrimary})
            return redirect("/"+path)
        elif pp[1]=="pageSettings":
            if not authorize(user, "pageprops", lang):
                return badauth(lang)
            pi=getIntFormParam(data, "page")
            if pi is None or not 0<=pi<len(pageDetail):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("page")))
            ads=getBooleanFormParam(data, "ads")
            if ads is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("ads")))
            locked=getBooleanFormParam(data, "locked")
            if locked is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("locked")))
            fakeRedlink=getBooleanFormParam(data, "fakeRedlink")
            if fakeRedlink is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("fakeRedlink")))
            pageType=getIntFormParam(data, "pageType")
            if pageType is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("pageType")))
            try:
                pageType=PageType(pageType)
            except:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("pageType")))
            oldSide=getPageSide(pi)
            newSide=pageTypeToSide[pageType]
            if oldSide != newSide:
                if hasExamples(pi):
                    return hresp(hrc.BAD_REQUEST, i18n[lang]["cannotChangePageSide"])
            pageDetail[pi]["ads"]=ads
            pageDetail[pi]["locked"]=locked
            pageDetail[pi]["fakeRedlink"]=fakeRedlink
            pageDetail[pi]["pageType"]=PageType(pageType)
            return redirect("/pageSettings?page="+str(pi))
        elif pp[1]=="mergePage":
            if not authorize(user, "admin", lang):
                return badauth(lang)
            pi=getIntFormParam(data, "page")
            if pi is None or not 0<=pi<len(pageDetail):
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("page")))
            tgtPath=getStrFormParam(data,"target")
            srcPath=getPagePrimaryPath(pi,lang)
            if tgtPath is None:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("target")))
            tgt=getPageIndex(tgtPath)
            if tgt==-1:
                return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("target")))
            if pi == tgt:
                return hresp(hrc.BAD_REQUEST, i18n[lang]["sameSrcTgtPage"])

            oldSide=getPageSide(pi)
            newSide=getPageSide(tgt)
            if oldSide != newSide:
                return hresp(hrc.BAD_REQUEST, i18n[lang]["cannotMergeDifferentSides"])
            for ei,ex in enumerate(examples):
                if ex["src"] == pi:
                    history.append({"event": "moveExample", "id":ei, "src":ex["src"], "tgt":tgt, "srcPath":srcPath, "tgtPath":tgtPath,
                        "content":ex["content"], "user": user, "time": time.time_ns()})
                    ex["src"] = tgt
                if ex["tgt"] == pi:
                    history.append({"event": "moveExample", "id":ei, "src":ex["tgt"], "tgt":tgt, "srcPath":srcPath, "tgtPath":tgtPath,
                        "content":ex["content"], "user": user, "time": time.time_ns()})
                    ex["tgt"] = tgt
            for ei,alias in enumerate(pageTitles):
                if alias["tgt"] == pi:
                    oldTgt=alias["tgt"]
                    alias["tgt"] = tgt
                    alias["isPrimary"] = False
                    history.append({"event": "moveAlias", "id":ei, "src":oldTgt, "tgt":tgt, "path":alias["path"],
                        "srcPath":srcPath, "tgtPath":tgtPath, "user": user, "time": time.time_ns()})
            return redirect("/"+tgtPath)
        elif pp[1]=="bulkEdit":
            if not authorize(user, "admin", lang):
                return badauth(lang)
            exTarget=getStrFormParam(data, "exTarget")
            if exTarget is not None:
                pi=getPageIndex(exTarget)
                if pi==-1:
                    return hresp(hrc.BAD_REQUEST, (i18n[lang]["invalidParam"].format("exTarget")))
                offset=getIntFormParam(data, "offset") or 0
                return hresp(hrc.OK, genBulkEditResults(pi, offset, exTarget))
            return hresp(hrc.BAD_REQUEST, "nyi")
        elif pp[1]=="bulkEditPreview":
            if not authorize(user, "admin", lang):
                return badauth(lang)
            bep,err=parseBulkEditParams(data, lang)
            if err is not None:
                return err
            return hresp(hrc.OK, genBulkEditPreview(bep, lang))
        elif pp[1]=="bulkEditSave":
            if not authorize(user, "admin", lang):
                return badauth(lang)
            bep,err=parseBulkEditParams(data, lang)
            if err is not None:
                return err
            for ex in bep["exs"]:
                ei=ex["id"]
                eex=examples[ei]
                contName="backContent" if ex["isBack"] else "content"
                if eex[contName] != ex["content"]:
                    eex[contName] = ex["content"]
                    eex["resolvedLinks"] = ex["resolvedLinks"]
                    eex["unresolvedLinks"] = ex["unresolvedLinks"]
                    history.append({"event": "editExample", "id":ei, "wi":eex["src"], "ti":eex["tgt"], "content":ex["content"], "user": user, "time": time.time_ns()})
            if bep["move"] is not None:
                pi=getPageIndex(bep["move"])
                tgtPath=getPagePrimaryPath(pi,lang)
                moveField="src" if getPageSide(pi)==0 else "tgt"
                for ex in bep["exs"]:
                    ei=ex["id"]
                    if ex["sel"]:
                        eex=examples[ei]
                        if eex[moveField] != pi:
                            oldPage=eex[moveField]
                            srcPath=getPagePrimaryPath(oldPage,lang)
                            eex[moveField]=pi
                            history.append({"event": "moveExample", "id":ei, "src":oldPage, "tgt":pi, "srcPath":srcPath, "tgtPath":tgtPath, "content":eex["content"], 
                                "user": user, "time": time.time_ns()})
            if bep["hide"] is not None:
                for ex in bep["exs"]:
                    ei=ex["id"]
                    if ex["sel"]:
                        eex=examples[ei]
                        if eex["hide"] != bep["hide"]:
                            eex["hide"]=bep["hide"]
                            history.append({"event": "changeExHidden", "src":eex["src"], "tgt":eex["tgt"], "id":ei, "val": bep["hide"], "content":eex["content"], 
                                "user": user, "time": time.time_ns()})
            return redirect("/bulkEdit")
        else:
            return hresp(hrc.BAD_REQUEST, "wtf")
    except Exception as e:
        print(traceback.format_exc())
        return hresp(hrc.INTERNAL_SERVER_ERROR, str(e))
