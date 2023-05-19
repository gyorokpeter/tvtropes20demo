from util import *
from ttypes import *
import requests
import os
import html
import urllib.parse
try:
    import settings # if missing, copy settings.example.py to settings.py and fill in accordingly
except:
    print("failed to load settings, importer won't work")

def downloadPage(path):
    url="https://tvtropes.org/pmwiki/pmwiki.php/"+path+"?action=source"
    resp=requests.get(url, cookies={"mylogin":urllib.parse.quote(settings.loginToken)})
    return resp.content

def getPageCached(path):
    normPath="cache/"+path.replace("/",".")
    if os.path.exists(normPath):
        return open(normPath,encoding="1250").read()
    page = downloadPage(path)
    open(normPath,"wb").write(page)
    return open(normPath).read()

def findFirstLink(ast, matchSide, normNs=True):
    for it in ast:
        if it[0] == PageElementType.LINK:
            if matchSide is None or getLinkSide(it[1], normNs) == 1-matchSide:
                return it
        elif it[0] in [PageElementType.TEXT, PageElementType.WEBLINK, PageElementType.ESCAPE, PageElementType.LINE_COMMENT]:
            pass
        elif it[0] in [PageElementType.LIST, PageElementType.LISTITEM, PageElementType.SPOILER, PageElementType.QUOTE, PageElementType.STRIKE]:
            link = findFirstLink(it[1], matchSide)
            if link is not None:
                return link
        elif it[0] in [PageElementType.EMPHASIS, PageElementType.NOTE]:
            link = findFirstLink(it[2], matchSide, normNs)
            if link is not None:
                return link
        else:
            raise Exception("don't know how to find links in {}".format(it[0]))

def importExamplesFromList(theList, side, normNs=True, unlinkedTarget=None):
    result=[]
    for it in theList:
        if it[0] == PageElementType.LISTITEM:
            li = it[1]
            theLink = None
            if 1<len(li) and li[1][0] == PageElementType.TEXT and li[1][1].startswith(':'):
                if li[0][0] == PageElementType.EMPHASIS and li[0][2][0][0] == PageElementType.LINK:
                    theLink = li[0][2][0]
                elif li[0][0] == PageElementType.LINK:
                    theLink = li[0]
            if theLink is not None and side is not None and getLinkSide(theLink[1], normNs) != 1-side:
                theLink = None
            if theLink is not None:
                obj=theLink[1]
                desc=li[1:]
                desc[0]=(desc[0][0], desc[0][1][2:])
                if 0==len(desc[0][1]):
                    desc=desc[1:]
                result.append((obj,desc))
            else:
                theLink = findFirstLink(li, side, normNs)
                if theLink is None:
                    #raise Exception('Not properly formatted (no link): {}'.format(li))
                    obj=unlinkedTarget or UNLIKED_EXAMPLE
                else:
                    obj=theLink[1]
                result.append((obj,li))
        else:
            raise Exception('Not properly formatted (expect LISTITEM): {}'.format(it))
    return result

def importExamples(ast, side, normNs=True):
    theList = []
    foldersUsed = False
    for elem in ast:
        if elem[0]==PageElementType.LIST:
            if len(elem[1])>0:
                hasListitems = False
                for li in elem[1]:
                    if li[0]==PageElementType.LISTITEM:
                        hasListitems = True
                        break
                if hasListitems:    #skip quote-only lists
                    theList += elem[1]
        elif elem[0]==PageElementType.FOLDER:
            foldersUsed = True
    if 0==len(theList) and not foldersUsed:
        return []
    if foldersUsed:
        result=[]
        for elem in ast:
            if elem[0]==PageElementType.FOLDER:
                cont=elem[2]
                for elem2 in cont:
                    unlinkedTarget=REALLIFE if elem[1]=='Real Life' else None
                    if elem2[0] == PageElementType.LIST:
                        result+=importExamplesFromList(elem2[1], side, normNs, unlinkedTarget=unlinkedTarget)
        return result
    else:
        return importExamplesFromList(theList, side, normNs)

def importPageBlocks(ast, hasExamples):
    desc=[]
    image=[]
    quote=[]
    stinger=[]
    hasSeparator = False
    readingDesc = True
    readingQuote = False
    readingExamples = False
    readingStinger = False
    for elem in ast:
        if elem[0] == PageElementType.SECTION_SEPARATOR:
            hasSeparator = True
            if readingDesc:
                readingDesc = False
                readingExamples = True
            elif readingExamples:
                readingExamples = False
                readingStinger = True
            elif readingStinger:
                readingStinger = False
        elif elem[0] == PageElementType.QUOTE and readingDesc:
            readingQuote = True
            quote.append(elem)
        elif elem[0] == PageElementType.PARAGRAPH_BREAK and readingQuote:
            readingQuote = False
        elif elem[0] == PageElementType.IMAGE or elem[0] == PageElementType.CAPTIONED_IMAGE:
            image=[elem]
        elif readingQuote:
            quote.append(elem)
        elif readingDesc:
            desc.append(elem)
        elif readingStinger:
            stinger.append(elem)
    if hasExamples and not hasSeparator:
        return {"desc": [], "image": [], "quote": [], "stinger": []}
    return {"desc": desc, "image": image, "quote": quote, "stinger": stinger}

def addImportedExamplesForPage(pi, lang, ptex, pageType):
    side=getPageSide(pi)
    for ex in ptex:
        path = normalizePath(ex[0])
        ei=getPageIndex(path)
        if ei == -1:
            ei = createPageWithAlias(path, pageType, splitWikiWord(path.split('/')[1]),lang)
        src = pi if side==0 else ei
        tgt = ei if side==0 else pi
        exr=makeExample(src, tgt, lang, False, 0, ex[1], PlayingWithType.STRAIGHT, None, None, None, set(), set())
        if not exr in examples:
            examples.append(exr)

def preprocessPage(page):
    startTag='<span style="font-family:Courier, \'Courier New\', monospace">'
    if not page.startswith(startTag):
        raise Exception("incorrect beginning")
    endTag="</span>"
    if not page.endswith(endTag):
        raise Exception("incorrect ending")
    return html.unescape(page[len(startTag):-len(endTag)].replace("<br>","\n"))

def importPage(path, lang, dest, pageType, exPageType, addPrimaryAlias = False, customContent=None):
    if dest is None:
        dest=path
    if not "/" in path:
        path="Main/"+path
    dest=normalizePath(dest)
    page=customContent or preprocessPage(getPageCached(path))
    prepPath="cache/"+path.replace("/",".")+".txt"
    if not os.path.exists("cache"):
        os.mkdir("cache")
    open(prepPath,"w",encoding="utf-8").write(page)

    ast=parseWiki(page,0)[0]

    wi=getPageIndex(dest)
    if wi == -1:
        wi=createPageWithAlias(dest, pageType, splitWikiWord(path.split("/")[1]), lang)

    if addPrimaryAlias:
        createAlias(wi, path, splitWikiWord(path.split("/")[1]), lang, True)

    ptex=importExamples(ast, pageTypeToSide[pageType], True)
    pb=importPageBlocks(ast, 0<len(ptex))
    if 0<len(pb["desc"]) and -1==getBlockIndex(wi, lang, BlockType.DESCRIPTION):
        blocks.append({"tgt":wi, "lang":lang, "bt":BlockType.DESCRIPTION, "content":pb["desc"]})
    if 0<len(pb["image"]) and -1==getBlockIndex(wi,lang, BlockType.IMAGE):
        blocks.append({"tgt":wi, "lang":lang, "bt":BlockType.IMAGE, "content":pb["image"]})
    if 0<len(pb["quote"]) and -1==getBlockIndex(wi,lang, BlockType.QUOTE):
        blocks.append({"tgt":wi, "lang":lang, "bt":BlockType.QUOTE, "content":pb["quote"]})
    if 0<len(pb["stinger"]) and -1==getBlockIndex(wi,lang, BlockType.STINGER):
        blocks.append({"tgt":wi, "lang":lang, "bt":BlockType.STINGER, "content":pb["stinger"]})
    addImportedExamplesForPage(wi, lang, ptex, exPageType)

def importTrope(path, lang, dest=None, pageType=PageType.TROPE, addPrimaryAlias = False):
    importPage(path, lang, dest, pageType, pageType, addPrimaryAlias)

def importWork(path, lang, dest=None, exPageType=PageType.TROPE, addPrimaryAlias = False):
    importPage(path, lang, dest, PageType.WORK, exPageType, addPrimaryAlias)
