from util import *
from importer import *

def test():
    def assertEq(x,y):
        if x != y:
            print('exp:{}\nact:{}'.format(y,x))
            raise Exception('test failed')

    def assertIn(x,y):
        if x not in y:
            print('exp:{}\nact:{}'.format(x,y))
            raise Exception('test failed')

    def testParse(text, expOut):
        assertEq(parseWiki(text,0)[0], expOut)

    def testRenderHTML(elem, expOut):
        assertEq(renderHTMLElem(elem, "en", None), expOut)

    def testParseAndRender(text, expOut):
        assertEq(renderHTMLList(parseWiki(text,0)[0], "en", None), expOut)

    initDB()

    testParse('<br>', [(PageElementType.TEXT, '<br>')])
    testParse('30 €', [(PageElementType.TEXT, '30 €')])
    testParse('aaaa', [(PageElementType.TEXT, 'aaaa')])
    testParse('AAAA', [(PageElementType.TEXT, 'AAAA')])
    testParse('Aaaa', [(PageElementType.TEXT, 'Aaaa')])
    testParse('Aaaa\nBbbb', [(PageElementType.TEXT, 'Aaaa Bbbb')])
    testParse('A2', [(PageElementType.TEXT, 'A2')])
    testParse('AAaa', [(PageElementType.LINK, 'AAaa', None)])
    testParse('AaAa', [(PageElementType.LINK, 'AaAa', None)])
    testParse('Aa20', [(PageElementType.LINK, 'Aa20', None)])
    testParse('AA20', [(PageElementType.LINK, 'AA20', None)])
    testParse('AaA', [(PageElementType.LINK, 'AaA', None)])
    testParse('AaAAa', [(PageElementType.LINK, 'AaAAa', None)])
    testParse('AaAAAa', [(PageElementType.LINK, 'AaAAAa', None)])
    testParse('AAaAAA', [(PageElementType.LINK, 'AAaAAA', None)])
    testParse('Aa/BbBb', [(PageElementType.LINK, 'Aa/BbBb', None)])
    testParse('AaAa/BbBb', [(PageElementType.LINK, 'AaAa/BbBb', None)])
    testParse('"Aaaa/BbBb"', [(PageElementType.TEXT, '"'),(PageElementType.LINK, 'Aaaa/BbBb', None),(PageElementType.TEXT, '"')])
    testParse('Aa/{{Bb}}', [(PageElementType.LINK, 'Aa/Bb', None)])
    testParse('{{AaAa/Bb}}', [(PageElementType.LINK, 'AaAa/Bb', None)])
    testParse('[=AaA=]', [(PageElementType.ESCAPE, 'AaA')])
    testParse("[a]", [(PageElementType.TEXT, "[a]")])
    testParse("don't", [(PageElementType.TEXT, "don't")])
    testParse("''don't''", [(PageElementType.EMPHASIS,2,[(PageElementType.TEXT, "don't")])])
    testParse("'''don't'''", [(PageElementType.EMPHASIS,3,[(PageElementType.TEXT, "don't")])])
    testParse("''''don't''''", [(PageElementType.EMPHASIS,3,[(PageElementType.TEXT, "'don't")]),(PageElementType.TEXT, "'")])
    testParse("'''''don't'''''", [(PageElementType.EMPHASIS,5,[(PageElementType.TEXT, "don't")])])
    testParse("aa''bb", [(PageElementType.TEXT, "aa''bb")])
    testParse("''aa'''bb'''''", [(PageElementType.EMPHASIS,2,[(PageElementType.TEXT, "aa"),(PageElementType.EMPHASIS,3,[(PageElementType.TEXT, "bb")])])])
    testParse("*''aa'''bb\n*cc", [(PageElementType.LIST, [(PageElementType.LISTITEM, [(PageElementType.EMPHASIS, 2, [(PageElementType.TEXT, 'aa')]), (PageElementType.TEXT, "'bb")]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, 'cc')])])])
    testParse('{{aa bb}}', [(PageElementType.LINK, 'AaBb', None)])
    testParse('{{aa|bb}}', [(PageElementType.LINK, 'Aabb', 'aa')])
    testParse('[[{{aa bb}} cc dd]]', [(PageElementType.LINK, 'AaBb', 'cc dd')])
    testParse('[[{{aa bb}}The]]', [(PageElementType.LINK, 'AaBb', '[1]')])
    testParse('[[{{AaAa/Bb20}} Cc]]', [(PageElementType.LINK, 'AaAa/Bb20', 'Cc')])
    testParse('[[AaAa bb cc]] dd [=EeE=] ff', [
        (PageElementType.LINK, 'AaAa', 'bb cc'),
        (PageElementType.TEXT, ' dd '),
        (PageElementType.ESCAPE, 'EeE'),
        (PageElementType.TEXT, ' ff')
    ])
    testParse('[[Aaaa/Bb20CcCc DdDd]]', [(PageElementType.LINK, 'Aaaa/Bb20CcCc', 'DdDd')])
    testParse("[[AaAa ''bb'' cc]]", [(PageElementType.LINK, 'AaAa', "''bb'' cc")])
    testParse('[[Aa/{{Bb}} Cc]]', [(PageElementType.LINK, 'Aa/Bb', 'Cc')])
    testParse('AaAa aa Bb/CcCc', [(PageElementType.LINK, 'AaAa', None), (PageElementType.TEXT, ' aa '), (PageElementType.LINK, 'Bb/CcCc', None)])
    testParse('[[https://example.com/index.html The website]]', [(PageElementType.WEBLINK, 'https://example.com/index.html', 'The website')])
    testParse('[[https://example.com/AaB The website]]', [(PageElementType.WEBLINK, 'https://example.com/AaB', 'The website')])
    testParse('[[https://example.com/_A0 aaaa]]Bbbb', [(PageElementType.WEBLINK, 'https://example.com/_A0', 'aaaa'), (PageElementType.TEXT, 'Bbbb')])
    testParse('[[quoteright:350:https://example.com/image.jpg]]', [(PageElementType.IMAGE, 350, 'https://example.com/image.jpg')])
    testParse('[[caption-width-right:350:The Caption]]', [(PageElementType.INFOBOX, 350, [(PageElementType.TEXT, 'The Caption')])])
    testParse('[[caption-width-right:350:TheCaption]]', [(PageElementType.INFOBOX, 350, [(PageElementType.LINK, 'TheCaption', None)])])
    testParse('[[quoteright:350:https://example.com/image.jpg]][[caption-width-right:400:The Caption]]',
        [(PageElementType.CAPTIONED_IMAGE, 350, 'https://example.com/image.jpg', 400, [(PageElementType.TEXT, 'The Caption')])])
    testParse('[[quoteright:325:[[Aaaa/BbBb https://example.com/image.jpg]]]]',
        [(PageElementType.IMAGE, 325, 'https://example.com/image.jpg')])
    testParse('[[quoteright:325:[[Aaaa/BbBb https://example.com/image.jpg]]]][[caption-width-right:325:[[CcCc Dddd]]]]',
        [(PageElementType.CAPTIONED_IMAGE, 325, 'https://example.com/image.jpg', 325, [(PageElementType.LINK, 'CcCc', 'Dddd')])])
    testParse('hey!', [(PageElementType.TEXT, 'hey!')])
    testParse('!hey', [(PageElementType.HEADER, 1, [(PageElementType.TEXT, 'hey')])])
    testParse('hey!\n!hey', [(PageElementType.TEXT, 'hey!'), (PageElementType.HEADER, 1, [(PageElementType.TEXT, 'hey')])])
    testParse('!!hey', [(PageElementType.HEADER, 2, [(PageElementType.TEXT, 'hey')])])
    testParse('!!!hey', [(PageElementType.HEADER, 3, [(PageElementType.TEXT, 'hey')])])
    testParse('7*6=42', [(PageElementType.TEXT, '7*6=42')])
    testParse('*1\n* 2\n*  3', [(PageElementType.LIST, [
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '1')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
    ])])
    testParse('*1\n**2\n**3', [(PageElementType.LIST, [
        (PageElementType.LISTITEM, [
            (PageElementType.TEXT, '1'),
            (PageElementType.LIST, [
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
            ])
        ])
    ])])
    testParse('*1\n**2\n**3\n*4\n**5\n**6', [(PageElementType.LIST, [
        (PageElementType.LISTITEM, [
            (PageElementType.TEXT, '1'),
            (PageElementType.LIST, [
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
            ])
        ]),
        (PageElementType.LISTITEM, [
            (PageElementType.TEXT, '4'),
            (PageElementType.LIST, [
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '5')]),
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '6')])
            ])
        ])
    ])])
    testParse('***1', [(PageElementType.LIST, [
        (PageElementType.LIST, [
            (PageElementType.LIST, [
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '1')])
            ])
        ])
    ])])
    testParse('*1\n-->2', [
        (PageElementType.LIST, [
            (PageElementType.LISTITEM, [
                (PageElementType.TEXT, '1'),
                (PageElementType.QUOTE, [(PageElementType.TEXT, '2')])
            ])
        ])
    ])
    testParse('--->1\n***2', [
        (PageElementType.LIST, [
            (PageElementType.LIST, [
                (PageElementType.QUOTE, [(PageElementType.TEXT, '1')]),
                (PageElementType.LIST, [
                    (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')])
                ])
            ])
        ])
    ])
    testParse('*1\n**2\n--->3\n***4\n**5\n***6', [
        (PageElementType.LIST, [
            (PageElementType.LISTITEM, [
                (PageElementType.TEXT, '1'),
                (PageElementType.LIST, [
                    (PageElementType.LISTITEM, [
                        (PageElementType.TEXT, '2'),
                        (PageElementType.QUOTE, [(PageElementType.TEXT, '3')]),
                        (PageElementType.LIST, [
                            (PageElementType.LISTITEM, [
                                (PageElementType.TEXT, '4')
                            ])
                        ])
                    ]),
                    (PageElementType.LISTITEM, [
                        (PageElementType.TEXT, '5'),
                        (PageElementType.LIST, [
                            (PageElementType.LISTITEM, [
                                (PageElementType.TEXT, '6')
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
    testParse('a % b', [(PageElementType.TEXT, 'a % b')])
    testParse('a %0% b', [(PageElementType.TEXT, 'a %0% b')])
    testParse('a %aa% b', [(PageElementType.TEXT, 'a '), (PageElementType.BLOCK_COMMENT, 'aa'), (PageElementType.TEXT, ' b')])
    testParse('a %%aa% b', [(PageElementType.TEXT, 'a '), (PageElementType.LINE_COMMENT, 'aa% b')])
    testParse('a %%aa% b\nc', [(PageElementType.TEXT, 'a '), (PageElementType.LINE_COMMENT, 'aa% b'), (PageElementType.TEXT, 'c')])
    testParse('*Aaaa\n%%* Bbbb', [(PageElementType.LIST, [(PageElementType.LISTITEM, [(PageElementType.TEXT, 'Aaaa')])]), (PageElementType.FORCE_NEWLINE,), (PageElementType.LINE_COMMENT, '* Bbbb')])
    testParse('a[[spoiler:b]]c', [(PageElementType.TEXT, 'a'), (PageElementType.SPOILER, [(PageElementType.TEXT, 'b')]), (PageElementType.TEXT, 'c')])
    testParse('a[[note]]b[[/note]]c', [(PageElementType.TEXT, 'a'), (PageElementType.NOTE, '', [(PageElementType.TEXT, 'b')]), (PageElementType.TEXT, 'c')])
    testParse('a[[labelnote:c]]b[[/labelnote]]c', [(PageElementType.TEXT, 'a'), (PageElementType.NOTE, 'c', [(PageElementType.TEXT, 'b')]), (PageElementType.TEXT, 'c')])
    testParse('-A', [(PageElementType.TEXT, '-A')])
    testParse('--A', [(PageElementType.TEXT, '--A')])
    testParse('->A', [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A')])])
    testParse('-->A', [(PageElementType.LIST, [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A')])])])
    testParse('--> A', [(PageElementType.LIST, [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A')])])])
    testParse('-->A\n-->A', [(PageElementType.LIST, [
        (PageElementType.QUOTE, [(PageElementType.TEXT, 'A')]),
        (PageElementType.QUOTE, [(PageElementType.TEXT, 'A')])
    ])])
    testParse('-->A\\\\\nA', [(PageElementType.LIST, [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A\nA')])])])
    testParse('---', [(PageElementType.TEXT,'---')])
    testParse('A->B', [(PageElementType.TEXT, 'A->B')])
    testParse('----', [(PageElementType.SECTION_SEPARATOR,)])
    testParse('a\n----\nb', [(PageElementType.TEXT,'a'), (PageElementType.SECTION_SEPARATOR,), (PageElementType.TEXT,'b')])
    testParse('a\n\nb', [(PageElementType.TEXT,'a'), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.TEXT,'b')])
    testParse('[[index]]abc[[/index]]', [(PageElementType.INDEX, [(PageElementType.TEXT, 'abc')])])
    testParse('[[index]]\nabc\n[[/index]]', [(PageElementType.INDEX, [(PageElementType.TEXT, 'abc')])])
    testParse('[[foldercontrol]]', [(PageElementType.FOLDERCONTROL,)])
    testParse('[[folder:Aaaa]][[/folder]][[folder:Bbbb]][[/folder]]', [(PageElementType.FOLDER, 'Aaaa', []), (PageElementType.FOLDER, 'Bbbb', [])])
    testParse('[[folder:Aaaa]]Bbbb[[/folder]]', [(PageElementType.FOLDER, 'Aaaa', [(PageElementType.TEXT, 'Bbbb')])])
    testParse("[[folder:Aaaa]]aa''bb[[/folder]]", [(PageElementType.FOLDER, 'Aaaa', [(PageElementType.TEXT, "aa''bb")])])
    testParse('[[folder:Aaaa]]* Bbbb[[/folder]]', [(PageElementType.FOLDER, 'Aaaa', [(PageElementType.TEXT, '* Bbbb')])])
    testParse('[[folder:a]]\nb\n[[/folder]]', [(PageElementType.FOLDER, 'a', [(PageElementType.TEXT, 'b')])])
    testParse('[[folder:Aaaa]][[/folder]]\n\n[[folder:Bbbb]][[/folder]]', [(PageElementType.FOLDER, 'Aaaa', []), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.FOLDER, 'Bbbb', [])])
    testParse('[[folder:Aaaa]][[/folder]]\n%%\n\n[[folder:Bbbb]][[/folder]]', [(PageElementType.FOLDER, 'Aaaa', []), (PageElementType.FORCE_NEWLINE,),
        (PageElementType.LINE_COMMENT, ''), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.FOLDER, 'Bbbb', [])])
    testParse('[[strike:a]]', [(PageElementType.STRIKE,[(PageElementType.TEXT, 'a')])])
    testParse('[[AC:Aaaa]]', [(PageElementType.ASSCAPS,[(PageElementType.TEXT, 'Aaaa')])])
    testParse("!!A:\n\nB.", [(PageElementType.HEADER, 2, [(PageElementType.TEXT, 'A:')]), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.TEXT, 'B.')])
    testParse("->A\n\nB", [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A')]), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.TEXT, 'B')])

    testRenderHTML((PageElementType.TEXT, '<br>'),'&lt;br&gt;')
    testRenderHTML((PageElementType.ESCAPE, '<br>'),'&lt;br&gt;')
    testRenderHTML((PageElementType.IMAGE, 350, 'https://example.com/image.jpg'),
        '<div class="quoteright" style="width:350px;"><img src="https://example.com/image.jpg" height="500"></div>')
    testRenderHTML((PageElementType.CAPTIONED_IMAGE, 350, 'https://example.com/image.jpg', 350, [(PageElementType.TEXT, 'The Caption')]),
        '<div class="quoteright" style="width:350px;"><img src="https://example.com/image.jpg" height="500">The Caption</div>')
    testRenderHTML((PageElementType.EMPHASIS, 2, [(PageElementType.TEXT, 'Aaaa')]),'<em>Aaaa</em>')
    testRenderHTML((PageElementType.EMPHASIS, 3, [(PageElementType.TEXT, 'Aaaa')]),'<strong>Aaaa</strong>')
    testRenderHTML((PageElementType.EMPHASIS, 5, [(PageElementType.TEXT, 'Aaaa')]),'<em><strong>Aaaa</strong></em>')
    testRenderHTML((PageElementType.LINK, 'AaA', None), '<a href="/Main/AaA" class="red" title="Main/AaA (page does not exist)">Aa A</a>')
    testRenderHTML((PageElementType.LINK, 'AaBb', 'CC DD'),'<a href="/Main/AaBb" class="red" title="Main/AaBb (page does not exist)">CC DD</a>')
    testRenderHTML((PageElementType.LINK, 'Film/AaBb', 'CC DD'),'<a href="/Film/AaBb" class="red" title="Film/AaBb (page does not exist)">CC DD</a>')
    testRenderHTML((PageElementType.WEBLINK, 'https://example.com/index.html', 'The website'),
        '<a href="https://example.com/index.html">The website<img src="https://static.tvtropes.org/pmwiki/pub/external_link.gif" style="border:none;" width="12" height="12"></a>')
    testRenderHTML((PageElementType.SECTION_SEPARATOR,), '<hr>')
    testRenderHTML((PageElementType.HEADER, 1, [(PageElementType.TEXT, 'hey')]), '<h1>hey</h1>')
    testRenderHTML((PageElementType.HEADER, 2, [(PageElementType.TEXT, 'hey')]), '<h2>hey</h2>')
    testRenderHTML((PageElementType.HEADER, 3, [(PageElementType.TEXT, 'hey')]), '<h3>hey</h3>')
    testRenderHTML((PageElementType.LIST, [
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '1')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
    ]), '<ul><li>1</li><li>2</li><li>3</li></ul>')
    testRenderHTML((PageElementType.ESCAPE, 'AaA'),'AaA')
    testRenderHTML((PageElementType.SPOILER, [(PageElementType.TEXT, 'Aaaa')]),'<span class="spoiler">Aaaa</span>')
    testRenderHTML((PageElementType.NOTE, '', [(PageElementType.TEXT, 'Aaaa')]),'<span class="notelabel">note</span>'
        +'<span class="note" style="display:none">Aaaa</span>')
    testRenderHTML((PageElementType.NOTE, 'Bbbb', [(PageElementType.TEXT, 'Aaaa')]),'<span class="notelabel">Bbbb</span>'
        +'<span class="note" style="display:none">Aaaa</span>')
    testRenderHTML((PageElementType.QUOTE, [(PageElementType.TEXT, 'Aaaa')]),'<div class="quote">Aaaa</div>')
    testRenderHTML((PageElementType.INDEX, [(PageElementType.LIST, [
        (PageElementType.LISTITEM, [(PageElementType.LINK, 'AaAa/Bb', 'Bb')]),
        (PageElementType.LISTITEM, [(PageElementType.LINK, 'CcCc/Dd', 'Dd')]),
    ])]),'<ul><li><a href="/AaAa/Bb" class="red" title="AaAa/Bb (page does not exist)">Bb</a></li><li><a href="/CcCc/Dd" class="red" title="CcCc/Dd (page does not exist)">Dd</a></li></ul>')
    testRenderHTML((PageElementType.FOLDERCONTROL,), '<div class="foldercontrol-closed" id="folderCtrlGlobal">open/close all folders</div>')
    testRenderHTML((PageElementType.FOLDER, 'a', [(PageElementType.TEXT, 'b')]), '<div class="foldercontrol-closed">a</div><div class="folder-closed">b</div>')
    testRenderHTML((PageElementType.EXAMPLE, 3, [(PageElementType.TEXT, 'Aaaa')]),'<div class="example" data-idx="3">Aaaa</div>')
    testRenderHTML((PageElementType.NEW_EXAMPLE_PLACEHOLDER, 1, 2, 'Aaaa'),'<div id="nxp" data-side="1" data-pi="2" data-title="Aaaa"></div>')
    testRenderHTML((PageElementType.STRIKE,[(PageElementType.TEXT, 'a')]),'<strike>a</strike>')
    testRenderHTML((PageElementType.ASSCAPS,[(PageElementType.TEXT, 'a')]),'<span class="asscaps">a</span>')

    def testRenderWiki(elem, expOut):
        assertEq(renderWikiElem(elem), expOut)
    def testRenderWikiList(lst, expOut):
        assertEq(renderWikiList(lst), expOut)
    testRenderWiki((PageElementType.TEXT, '<br>'),'<br>')
    testRenderWiki((PageElementType.IMAGE, 350, 'https://example.com/image.jpg'),
        '[[quoteright:350:https://example.com/image.jpg]]')
    testRenderWiki((PageElementType.CAPTIONED_IMAGE, 350, 'https://example.com/image.jpg', 350, [(PageElementType.TEXT, 'The Caption')]),
        '[[quoteright:350:https://example.com/image.jpg]][[caption-width-right:350:The Caption]]')
    testRenderWiki((PageElementType.EMPHASIS,3,[(PageElementType.TEXT, "don't")]),"'''don't'''")
    testRenderWiki((PageElementType.LINK, 'AaAa/Bb20', None), '{{AaAa/Bb20}}')
    testRenderWiki((PageElementType.LINK, 'AaAa/Bb20', 'Cc'), '[[{{AaAa/Bb20}} Cc]]')
    testRenderWikiList([(PageElementType.TEXT,'a'), (PageElementType.SECTION_SEPARATOR,), (PageElementType.TEXT,'b')],'a\n----\nb')
    testRenderWikiList([(PageElementType.TEXT,'a'), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.TEXT,'b')], 'a\n\nb')
    testRenderWiki((PageElementType.WEBLINK, 'https://example.com/index.html', 'The website'), '[[https://example.com/index.html The website]]')
    testRenderWiki((PageElementType.HEADER, 3, [(PageElementType.TEXT, 'hey')]), '!!!hey')
    testRenderWiki((PageElementType.LIST, [
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '1')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
        (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
    ]), '* 1\n* 2\n* 3')
    testRenderWiki((PageElementType.LIST, [
        (PageElementType.LISTITEM, [
            (PageElementType.TEXT, '1'),
            (PageElementType.LIST, [
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '2')]),
                (PageElementType.LISTITEM, [(PageElementType.TEXT, '3')])
            ])
        ])
    ]), '* 1\n** 2\n** 3')
    testRenderWiki((PageElementType.ESCAPE, 'AaA'), '[=AaA=]')
    testRenderWiki((PageElementType.SPOILER, [(PageElementType.TEXT, 'a')]), '[[spoiler:a]]')
    testRenderWiki((PageElementType.NOTE, '', [(PageElementType.TEXT, 'a')]),'[[note]]a[[/note]]')
    testRenderWiki((PageElementType.NOTE, 'a', [(PageElementType.TEXT, 'b')]), '[[labelnote:a]]b[[/labelnote]]')
    testRenderWiki((PageElementType.LIST, [
        (PageElementType.QUOTE, [(PageElementType.TEXT, 'A')]),
        (PageElementType.QUOTE, [(PageElementType.TEXT, 'A')])
    ]), '-->A\n-->A')
    testRenderWiki((PageElementType.LINE_COMMENT, 'aa% b'),'%%aa% b\n')
    testRenderWiki((PageElementType.INDEX, [(PageElementType.TEXT, 'abc')]),'[[index]]\nabc\n[[/index]]\n')
    testRenderWiki((PageElementType.FOLDERCONTROL,), '[[foldercontrol]]')
    testRenderWiki((PageElementType.FOLDER, 'a', [(PageElementType.TEXT, 'b')]), '[[folder:a]]\nb\n[[/folder]]\n')
    testRenderWiki((PageElementType.STRIKE,[(PageElementType.TEXT, 'a')]), '[[strike:a]]')
    testRenderWiki((PageElementType.ASSCAPS,[(PageElementType.TEXT, 'a')]), '[[AC:a]]')
    testRenderWikiList([(PageElementType.QUOTE, [(PageElementType.TEXT, 'A')]), (PageElementType.PARAGRAPH_BREAK,), (PageElementType.TEXT, 'B')],"->A\n\nB")
    testRenderWiki((PageElementType.QUOTE, [(PageElementType.TEXT, 'A')]),'->A')
    testRenderWiki(
        (PageElementType.LIST, [
            (PageElementType.LISTITEM, [
                (PageElementType.TEXT, '1'),
                (PageElementType.QUOTE, [(PageElementType.TEXT, '2')])
            ])
        ]), '* 1\n-->2'
    )
    testRenderWiki((PageElementType.LIST, [(PageElementType.QUOTE, [(PageElementType.TEXT, 'A\nA')])]), '-->A\\\\\nA')
    testRenderWikiList([(PageElementType.TEXT, 'Aaaa'),(PageElementType.LIST, [(PageElementType.LISTITEM, [(PageElementType.TEXT, 'Bbbb')])])], 'Aaaa\n* Bbbb')

    testParseAndRender('* Aaaa\n* Bbbb','<ul><li>Aaaa</li><li>Bbbb</li></ul>')
    testParseAndRender('--> Aaaa','<ul><div class="quote">Aaaa</div></ul>')
    testParseAndRender('a %aa% b', 'a  b')
    testParseAndRender('a %%aa% b', 'a ')
    testParseAndRender('a %%aa% b\nc', 'a c')

    def testImportExamples(text, expOut):
        assertEq(importExamples(parseWiki(text,0)[0], None, False), expOut)

    testImportExamples('* AaAa: BbBb', [('AaAa', [(PageElementType.LINK, 'BbBb', None)])])
    testImportExamples("* ''AaAa'': BbBb", [('AaAa', [(PageElementType.LINK, 'BbBb', None)])])
    testImportExamples('* AaAa: \n** Bbbb', [('AaAa', [(PageElementType.LIST, [(PageElementType.LISTITEM, [(PageElementType.TEXT, 'Bbbb')])])])])
    testImportExamples('* AaAa BbBb: Cccc', [('AaAa', [
        (PageElementType.LINK, 'AaAa', None),
        (PageElementType.TEXT, ' '),
        (PageElementType.LINK, 'BbBb', None),
        (PageElementType.TEXT, ': Cccc')
    ])])
    testImportExamples("* ''AaAA/BbBb'' Cccc", [('AaAA/BbBb', [(PageElementType.EMPHASIS, 2, [(PageElementType.LINK, 'AaAA/BbBb', None)]), (PageElementType.TEXT, ' Cccc')])])
    testImportExamples("* Aaaa BbBb Cccc", [('BbBb', [(PageElementType.TEXT, 'Aaaa '), (PageElementType.LINK, 'BbBb', None), (PageElementType.TEXT, ' Cccc')])])
    testImportExamples("* [[http://aaa Bbbb]] CcCc", [('CcCc', [(PageElementType.WEBLINK, 'http://aaa', 'Bbbb'), (PageElementType.TEXT, ' '), (PageElementType.LINK, 'CcCc', None)])])
    testImportExamples("[[folder:Zzzz]]\n* [[http://aaa Bbbb]] CcCc\n[[/folder]]", [('CcCc', [
        (PageElementType.WEBLINK, 'http://aaa', 'Bbbb'), (PageElementType.TEXT, ' '), (PageElementType.LINK, 'CcCc', None)])])
    testImportExamples("[[folder:Real Life]]\n* Aaaa\n* Bbbb\n[[/folder]]", [('Misc/RealLife', [(PageElementType.TEXT, 'Aaaa')]), ('Misc/RealLife', [(PageElementType.TEXT, 'Bbbb')])])
    testImportExamples("[[folder:A]]\n* {{Myth/Aaaa}}:\n** Aaaa\n** Bbbb\n[[/folder]]\n[[folder:Real Life]]\n* Aaaa\n* Bbbb\n[[/folder]]",[
            ('Myth/Aaaa', [(PageElementType.LIST, [(PageElementType.LISTITEM, [(PageElementType.TEXT, 'Aaaa')]), (PageElementType.LISTITEM, [(PageElementType.TEXT, 'Bbbb')])])]),
            ('Misc/RealLife', [(PageElementType.TEXT, 'Aaaa')]), ('Misc/RealLife', [(PageElementType.TEXT, 'Bbbb')])
        ])
    testImportExamples("* Aaaa", [('Misc/UnlinkedExample', [(PageElementType.TEXT, 'Aaaa')])])

    #def testGroupExamples(text, expOut):
    #    assertEq(groupExamples(importExamples(parse(text,0)[0])), expOut)
    def testGroupExamples(exs, expOut):
        assertEq(groupExamples(exs), expOut)

    testGroupExamples([('AaAa', [(PageElementType.TEXT, 'Bbbb')], 1, 0, 0, PlayingWithType.STRAIGHT, True)], [('AaAa', [(1,[(PageElementType.TEXT, 'Bbbb')], PlayingWithType.STRAIGHT, True)])])
    testGroupExamples([('AaAa', [(PageElementType.TEXT, 'Bbbb')], 1, 0, 0, PlayingWithType.STRAIGHT, False), ('AaAa', [(PageElementType.TEXT, 'Cccc')], 2, 0, 0, PlayingWithType.STRAIGHT, False)],
        [('AaAa', [(1,[(PageElementType.TEXT, 'Bbbb')], PlayingWithType.STRAIGHT, False), (2,[(PageElementType.TEXT, 'Cccc')], PlayingWithType.STRAIGHT, False)])])

    def testTieExamples(exs, expOut):
        assertEq(tieExamples(groupExamples(exs), 'en', lambda x:[(PageElementType.LINK, x, x)]), expOut)

    testTieExamples([('AaAa', [(PageElementType.TEXT, 'Bbbb')], 1, 0, 0, PlayingWithType.STRAIGHT, False)], [(PageElementType.LIST, [(PageElementType.LISTITEM, [
        (PageElementType.EXAMPLE,1,[(PageElementType.LINK, 'AaAa', 'AaAa'),  (PageElementType.TEXT, ': '), (PageElementType.TEXT, 'Bbbb')])
    ])])])
    testTieExamples([('AaAa', [(PageElementType.TEXT, 'Bbbb')], 1, 0, 0, PlayingWithType.AVERTED, False)], [(PageElementType.LIST, [(PageElementType.LISTITEM, [
        (PageElementType.EXAMPLE,1,[(PageElementType.LINK, 'AaAa', 'AaAa'),  (PageElementType.TEXT, ': '), (PageElementType.EMPHASIS, 2, [(PageElementType.TEXT, 'Averted: ')]),
        (PageElementType.TEXT, 'Bbbb')])
    ])])])
    testTieExamples([('AaAa', [(PageElementType.TEXT, 'Bbbb')], 1, 0, 0, PlayingWithType.STRAIGHT, True), ('AaAa', [(PageElementType.TEXT, 'Cccc')], 2, 0, 0, PlayingWithType.AVERTED, False)],
        [(PageElementType.LIST,
            [(PageElementType.LISTITEM, [
                (PageElementType.LINK, 'AaAa', 'AaAa'),
                (PageElementType.TEXT, ':'),
                (PageElementType.LIST, [
                    (PageElementType.LISTITEM, [(PageElementType.EXAMPLE,1,[(PageElementType.FORMATTER, {"class":"hidden"}, [(PageElementType.TEXT, 'Bbbb')])])]),
                    (PageElementType.LISTITEM, [(PageElementType.EXAMPLE,2,[(PageElementType.EMPHASIS, 2, [(PageElementType.TEXT, 'Averted: ')]), (PageElementType.TEXT, 'Cccc')])])
                ])
            ])]
        )]
    )

    addTestUsers()
    hg=lambda x:handleGet(x,0)
    hp=lambda x,y:handlePost(x,y,0)
    def getUserId(user):
        for i,u in enumerate(users):
            if u["name"]==user:
                return i
        raise Exception("user not found: {}".format(user))
    regUser=getUserId("alice")
    modUser=getUserId("karen")
    admUser=getUserId("wordya")


    assertEq(hg("/api/v1/example/0?lang=en&side=0"),{"type": "json", "code": hrc.BAD_REQUEST, "content": '{"error": "example not found"}'})
    assertEq(handlePost("/createPage", {"path": ["Main/TestTrope"], "displayName":["Test trope"], "pageType": [PageType.TROPE.value]}, modUser), 
        {'type': 'text', 'code': hrc.FOUND, 'content': '', 'headers': {'Location': 'Main/TestTrope'}})
    assertEq(genListPage(0, "en"),{'code': hrc.OK, 'type': 'text', 'content': '<html><body><ul><li><a href="/wiki/2?lang=en">Test trope</a></li></ul></body></html>'})
    assertEq(hp("/createPage", {"path": ["Film/TestWork"], "displayName":["Test work"], "pageType": [PageType.WORK.value]}), 
        {'type': 'text', 'code': hrc.FOUND, 'content': '', 'headers': {'Location': 'Film/TestWork'}})
    assertEq(hp("/api/v1/example?lang=en", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":0, "content":"Example text 0", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 0, "content": "<em><a href=\\"/Film/TestWork\\" title=\\"Film/TestWork\\">Test work</a></em>: Example text 0"}'})
    assertEq(examples[0]["asymmetric"], False)
    assertEq(hp("/api/v1/example?lang=en", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":0, "content":"Example text 1", "asym": True, "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "content": "<em><a href=\\"/Film/TestWork\\" title=\\"Film/TestWork\\">Test work</a></em>: Example text 1"}'})
    assertEq(examples[1]["asymmetric"], True)
    assertEq(examples[1]["backContent"], examples[1]["content"])
    assertEq(hg("/api/v1/example/0?lang=en&side=0"),{'type': 'json', 'code': hrc.OK, 'content': '{"id": 0, "linkSource": "Main/TestTrope", "linkTarget": "Film/TestWork", '+
        '"content": "Example text 0", "asym": false, "play": 0, "hide": false, "lock": false}'})
    assertEq(handleGet("/api/v1/example/0?lang=en&side=0",modUser),{'type': 'json', 'code': hrc.OK, 'content': '{"id": 0, "linkSource": "Main/TestTrope", "linkTarget": "Film/TestWork", '+
        '"content": "Example text 0", "asym": false, "play": 0, "hide": false, "lock": false, "embargo": false}'})
    assertEq(hg("/api/v1/example/1?lang=en&side=0"),{'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "linkSource": "Main/TestTrope", "linkTarget": "Film/TestWork", '+
        '"content": "Example text 1", "asym": true, "play": 0, "hide": false, "lock": false}'})
    assertEq(hp("/api/v1/example/0", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":1, "content":"Example text 0 on work page", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 0, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: Example text 0 on work page"}'})
    assertEq(examples[0]["content"], [(PageElementType.TEXT, 'Example text 0 on work page')])
    assertEq(hp("/api/v1/example/1", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":1, "content":"Example text 1 on work page", "asym": True, "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: Example text 1 on work page"}'})
    assertEq(examples[1]["content"], [(PageElementType.TEXT, 'Example text 1')])
    assertEq(examples[1]["backContent"], [(PageElementType.TEXT, 'Example text 1 on work page')])
    assertEq(hp("/api/v1/example/1", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":0, "content":"Example text 1 on trope page", "asym": True, "save": True, "play": "1"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "content": "<em><a href=\\"/Film/TestWork\\" title=\\"Film/TestWork\\">Test work</a></em>: <em>Averted: </em>Example text 1 on trope page"}'})
    assertEq(examples[1]["content"], [(PageElementType.TEXT, 'Example text 1 on trope page')])
    assertEq(examples[1]["backContent"], [(PageElementType.TEXT, 'Example text 1 on work page')])
    assertEq(hg("/api/v1/example/1?lang=en&side=0"),{'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "linkSource": "Main/TestTrope", "linkTarget": "Film/TestWork", '+
        '"content": "Example text 1 on trope page", "asym": true, "play": 1, "hide": false, "lock": false}'})
    assertEq(hg("/api/v1/example/1?lang=en&side=1"),{'type': 'json', 'code': hrc.OK, 'content': '{"id": 1, "linkSource": "Main/TestTrope", "linkTarget": "Film/TestWork", '+
        '"content": "Example text 1 on work page", "asym": true, "play": 1, "hide": false, "lock": false}'})
    assertEq(hp("/createPage", {"path": ["VideoGame/TestGame"], "displayName":["Test video game"], "pageType": [PageType.WORK.value]}), 
        {'type': 'text', 'code': hrc.FOUND, 'content': '', 'headers': {'Location': 'VideoGame/TestGame'}})
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"VideoGame/TestGame", "pageSide":1, "content":"Example for video game", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 2, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: Example for video game"}'})
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example for real life", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 3, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: Example for real life"}'})
    assertEq(getNamespaceDisplayName('VideoGame', 'en'), "Video Game")
    assertEq(getNamespaceDisplayName('VideoGame', 'es'), "Videojuego")
    assertEq(getNamespaceDisplayName('RealLife', 'en'), "Real Life")
    assertEq(getPageDisplayName(getPageIndex(REALLIFE), 'en'), "Real life")
    assertEq(getPageDisplayName(getPageIndex(REALLIFE), 'es'), "Real life")

    ast=genExamplesAst(getPageIndex("Main/TestTrope"), "en", None, SortType.AZ, False)
    folders=[x for x in ast if x[0]==PageElementType.FOLDER]
    folderNames=[x[1] for x in folders]
    assertIn("Video Game", folderNames)
    assertEq(renderWikiList(folders[folderNames.index('Real Life')][2]), "* Example for real life")

    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example 2 for real life", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 4, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: Example 2 for real life"}'})
    ast=genExamplesAst(getPageIndex("Main/TestTrope"), "en", None, SortType.AZ, False)
    folders=[x for x in ast if x[0]==PageElementType.FOLDER]
    folderNames=[x[1] for x in folders]
    assertEq(renderWikiList(folders[folderNames.index('Real Life')][2]), "* Example for real life\n* Example 2 for real life")

    #importPage("Main/Example", "en", "Main/Example", PageType.TROPE, PageType.WORK, False, customContent=open('example.txt',encoding="utf-8").read())
    importPage("Main/Example", "en", "Main/Example", PageType.TROPE, PageType.WORK, False, customContent='* OlderThanDirt: aaaa')

    # ignore Main/ link in heading
    importPage("Main/Example2", "en", "Main/Example2", PageType.TROPE, PageType.WORK, False, customContent='* AaAa: {{Literature/Bbbb}}\n* {{UsefulNotes/Cccc}}: {{Literature/Dddd}}')
    exs=getExamples(getPageIndex("Main/Example2"), "en", None, None, False)
    assertEq(getPagePrimaryAlias(exs[0][0],"en")["path"], "Literature/Bbbb")
    assertEq(getPagePrimaryAlias(exs[1][0],"en")["path"], "Literature/Dddd")

    assertEq(hp("/api/v1/page/"+str(getPageIndex("Main/TestTrope"))+"/block/1", {"content":"description", "save": True}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"content": "description"}'})

    # can't edit locked page
    ti=getPageIndex("Main/TestTrope")
    wi=getPageIndex("Misc/RealLife")
    assertEq(pageLocked(ti, regUser, "en"), False)
    assertEq(pageLocked(ti, modUser, "en"), False)
    assertEq(pageLocked(ti, admUser, "en"), False)
    pageDetail[ti]["locked"]=True
    assertEq(pageLocked(ti, regUser, "en"), True)
    assertEq(pageLocked(ti, modUser, "en"), False)
    assertEq(pageLocked(ti, modUser, "es"), True)
    assertEq(pageLocked(ti, admUser, "en"), False)
    assertEq(hp("/api/v1/example/0", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example 2 for real life", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.BAD_REQUEST, 'content': '{"error": "Page Main/TestTrope is locked"}'})
    assertEq(hp("/api/v1/page/"+str(getPageIndex("Main/TestTrope"))+"/block/1", {"content":"description", "save": True}),
        {'type': 'json', 'code': hrc.BAD_REQUEST, 'content': '{"error": "Page Main/TestTrope is locked"}'})
    pageDetail[ti]["locked"]=False
    pageDetail[wi]["locked"]=True
    assertEq(hp("/api/v1/example/0", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example 2 for real life", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.BAD_REQUEST, 'content': '{"error": "Page Misc/RealLife is locked"}'})

    pageDetail[wi]["locked"]=False
    pageDetail[ti]["fakeRedlink"]=True
    # blocked from using fake redlink as example source
    assertEq(hp("/api/v1/example/0", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example 2 for real life", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.BAD_REQUEST, 'content': '{"error": "page Main/TestTrope is an invalid example source"}'})
    pageDetail[ti]["fakeRedlink"]=False
    ti2=getPageIndex("Main/Example")
    pageDetail[ti2]["fakeRedlink"]=True
    # blocked from using fake redlink in the example content
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"See also {{Main/Example}}", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.BAD_REQUEST, 'content': '{"error": "Page does not exist, create it here: ", "badLinks": ["Main/Example"]}'})
    pageDetail[ti2]["fakeRedlink"]=False
    # create an example with a valid link...
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"See also {{Main/Example}}", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 8, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: '+
            'See also <a href=\\"/Main/Example\\" title=\\"Main/Example\\">Example</a>"}'})
    pageDetail[ti2]["fakeRedlink"]=True
    # ... then turn the target into a fake redlink to see if it now actually shows up in red
    assertEq(renderHTMLElem(examples[8]["content"][1], "en", None), '<a href="/Main/Example" class="red" title="Main/Example (page does not exist)">Example</a>')
    pageDetail[ti2]["fakeRedlink"]=False
    # ensure current page is not linked
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"See also {{Misc/RealLife}}", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.OK, 'content': '{"id": 8, "content": "<a href=\\"/Main/TestTrope\\" title=\\"Main/TestTrope\\">Test trope</a>: See also Real life"}'})
    # ensure opposite page is linked
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"See also {{Misc/RealLife}}", "save": True, "play": "0"}),
        {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'See also <a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a>"}'})

    # regular user forbidden from altering the mod settings
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"See also {{Misc/RealLife}}", "save": True, "play": "0",
        "lock": True}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "You are not authorized to perform this action"}'})
    # mod user NOT forbidden from altering the mod settings
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"See also {{Misc/RealLife}}", "save": True, "play": "0",
        "lock": True}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'See also <a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a>"}'})

    genWikiPage(0, "en") # just to check it doesn't error
    hg("/api/v1/page/0/exampleHtml?lang=en&filter=tropes&sort=ctimeUp")
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Hidden", "save": True, "play": "0",
        "lock": False,"hide": True}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        '<span class=\\"hidden\\">Hidden</span>"}'})
    assertEq(len(getExamplesRaw(getPageIndex("Main/TestTrope"), "en", None, None, False)), 5)
    assertEq(len(getExamplesRaw(getPageIndex("Main/TestTrope"), "en", None, None, True)), 6)

    # add an example with a hidden combination
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Hidden!", "save": True, "play": "0",
        "hide": True}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "There is already a hidden example for this page combination.'+
        ' Please check \\"Include hidden examples\\", edit and unhide the example."}'})

    # move an example to a hidden combination
    assertEq(hp("/api/v1/example/7", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Hidden!", "save": True, "play": "0",
        "hide": True}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "There is already a hidden example for this page combination.'+
        ' Please check \\"Include hidden examples\\", edit and unhide the example."}'})

    # unhide
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Unhidden", "save": True, "play": "0",
        "hide": False}), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'Unhidden"}'})

    # lock
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Locked", "save": True, "play": "0",
        "lock": True}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'Locked"}'})

    # try to edit while locked
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Still locked", "save": True, "play": "0",
        "hide": False}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "This example is locked."}'})

    # unlock
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Unlocked", "save": True, "play": "0",
        "lock": False}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'Unlocked"}'})

    # enable embargo
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Locked", "save": True, "play": "0",
        "embargo": True}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'Locked"}'})

    # try to add dupe example while there is an embargo
    assertEq(hp("/api/v1/example", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Still locked", "save": True, "play": "0",
        "hide": False}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "This page combination is under embargo."}'})

    # try to move example FROM an embargoed combination
    assertEq(hp("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Film/TestWork", "pageSide":0, "content":"Still locked", "save": True, "play": "0",
        "hide": False}), {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "This page combination is under embargo."}'})

    # try to move example TO an embargoed combination
    assertEq(hp("/api/v1/example/2", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":1, "content":"Example for video game", "save": True, "play": "0"}),
        {'type': 'json', 'code': hrc.FORBIDDEN, 'content': '{"error": "This page combination is under embargo."}'})

    # disable embargo
    assertEq(handlePost("/api/v1/example/8", {"linkSource":"Main/TestTrope", "linkTarget":"Misc/RealLife", "pageSide":0, "content":"Unlocked", "save": True, "play": "0",
        "embargo": False}, modUser), {'type': 'json', 'code':hrc.OK, 'content': '{"id": 8, "content": "<em><a href=\\"/Misc/RealLife\\" title=\\"Misc/RealLife\\">Real life</a></em>: '+
        'Unlocked"}'})

    # try to merge pages as regular user
    assertEq(hp("/mergePage", {"page":getPageIndex("Film/TestWork"), "target":"VideoGame/TestGame"}), {'type': 'text', 'code': hrc.FORBIDDEN,
        'content': 'You are not authorized to perform this action'})

    # try to merge pages as admin
    assertEq(len(getExamplesRaw(getPageIndex("Film/TestWork"), "en", None, None, False)), 2)
    assertEq(len(getExamplesRaw(getPageIndex("VideoGame/TestGame"), "en", None, None, False)), 1)
    assertEq(handlePost("/mergePage", {"page":[getPageIndex("Film/TestWork")], "target":["VideoGame/TestGame"]}, admUser),
        {'type': 'text', 'code': hrc.FOUND, 'content': '', 'headers': {'Location': '/VideoGame/TestGame'}})
    assertEq(len(getExamplesRaw(getPageIndex("VideoGame/TestGame"), "en", None, None, False)), 3) # count is the sum of the two above

    assertIn("user wordya moved alias Film/TestWork from Film/TestWork to VideoGame/TestGame", hg('/pageHistory?id=3')["content"])  # event on source side
    assertIn("user wordya moved alias Film/TestWork from Film/TestWork to VideoGame/TestGame", hg('/pageHistory?id=4')["content"])  # event on target side

    # bulk edit a symmetric example
    assertEq(hp("/bulkEditPreview", {'excont1': ['Example text 1 on trope page aaa'], 'excont1.back': ['Example text 1 on work page aaa']}),
        {'type': 'text', 'code': hrc.FORBIDDEN, 'content': 'You are not authorized to perform this action'})
    assertEq(hp("/bulkEditSave", {'excont1': ['Example text 1 on trope page aaa'], 'excont1.back': ['Example text 1 on work page aaa']}),
        {'type': 'text', 'code': hrc.FORBIDDEN, 'content': 'You are not authorized to perform this action'})
    assertEq(handlePost("/bulkEditPreview", {'excont1': 'aaa'}, admUser), {'type': 'text', 'code': hrc.BAD_REQUEST, 'content': 'invalid value for parameter: excont1'})
    assertEq(handlePost("/bulkEditPreview", {'excont1': ['Example text 1 on trope page aaa'], 'excont1.back': ['Example text 1 on work page aaa']}, admUser)["code"], hrc.OK)
    assertEq(handlePost("/bulkEditSave", {'excont1': ['Example text 1 on trope page aaa'], 'excont1.back': ['Example text 1 on work page aaa']}, admUser),
        {'type': 'text', 'code': hrc.FOUND, 'content': '', 'headers': {'Location': '/bulkEdit'}})
    assertEq(examples[1]["content"], [(PageElementType.TEXT, "Example text 1 on trope page aaa")])
    assertEq(examples[1]["backContent"], [(PageElementType.TEXT, "Example text 1 on work page aaa")])

    print('test complete')
