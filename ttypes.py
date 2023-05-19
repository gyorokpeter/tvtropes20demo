from enum import Enum

class PageType(Enum): # must match i18n[lang]["pageType"]
    WORK=0
    TROPE=1
    YMMV=2
    TRIVIA=3
    USEFUL_NOTES=4
    ADMIN=5

class PageElementType(Enum):
    NONE=0
    TEXT=1
    ESCAPE=2
    LINK=3
    WEBLINK=4
    LIST=5
    LISTITEM=6
    IMAGE=7
    INFOBOX=8
    CAPTIONED_IMAGE=9
    EMPHASIS=10
    HEADER=11
    BLOCK_COMMENT=12
    LINE_COMMENT=13
    SPOILER=14
    NOTE=15
    QUOTE=16
    SECTION_SEPARATOR=17
    INDEX=18
    FOLDERCONTROL=19
    FOLDER=20
    STRIKE=21
    ASSCAPS=22
    PARAGRAPH_BREAK=23
    EXAMPLE=24
    FORCE_NEWLINE=25
    NEW_EXAMPLE_PLACEHOLDER=26
    PAGE_BLOCK=27
    CONTAINER=28
    FORMATTER=29
    RESOLVED_LINK=30

class Side(Enum):
    DESCRIPTOR=0
    DESCRIPTEE=1
    OTHER=2

class BlockType(Enum):
    TITLE=0
    DESCRIPTION=1
    QUOTE=2
    IMAGE=3
    STINGER=4
    ANALYSIS=5

pageTypeToSide={
    PageType.WORK : 1,
    PageType.TROPE : 0,
    PageType.YMMV : 0,
    PageType.TRIVIA : 0,
    PageType.USEFUL_NOTES : 2,
    PageType.ADMIN : 2,
}

class SortType(Enum):
    AZ=0
    CTIME_UP=1
    CTIME_DOWN=2
    MTIME_UP=3
    MTIME_DOWN=4

class PlayingWithType(Enum):
    STRAIGHT=0
    AVERTED=1
    JUSTIFIED=2
    INVERTED=3
    SUBVERTED=4
    DOUBLE_SUBVERTED=5
    PARODIED=6
    ZIGZAGGED=7
