from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re
import threading


def getMangaList(pattern, serverpage):
    list = pattern.findall(serverpage)
    return list


def getImageIcon(pattern, serverpage, counterManga=0, mangaIconNull=[]):
    list = pattern.findall(serverpage)
    for iconNull in mangaIconNull:
        list.insert(iconNull, '')
    iconLink = ['https://komikcast.ch/wp-content/uploads/' + list[counterManga] + '.jpeg']
    iconLink.append('https://komikcast.ch/wp-content/uploads/' + list[counterManga] + '.jpg')
    iconLink.append('https://komikcast.ch/wp-content/uploads/' + list[counterManga] + '.png')
    iconLink.append('https://komikcast.ch/wp-content/uploads/' + list[counterManga] + '.webp')
    i = 0
    iconResult = None
    while i < len(iconLink):
        try:
            req = Request(
                url=iconLink[i],
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            iconResult = urlopen(req).read()
            break
        except HTTPError as err:
            if err.code == 404:
                i += 1
            pass
    if i < len(iconLink):
        iconLinkResult = iconLink[i]
    else:
        print(list[counterManga])
        iconLinkResult = ''
    return iconResult, iconLinkResult


def getLastIndex(webpage):
    pat = re.compile('<a class="page-numbers" href="https://komikcast.ch/daftar-komik/page/(.+?)</a>')
    listPath = getMangaList(pat, webpage)
    lastIndex = listPath[len(listPath) - 1]
    lastIndex = re.sub(r'^.*?">', '', lastIndex)


class ListMangaScreen(Screen):
    def on_enter(self, *args):
        Factory.CustomButton(text='txt', size_hint=(1, None))


class CustomButton(Button):
    pass


class CustomButtonChapter(Button):
    pass


class NewGameScreen(Screen):
    def on_enter(self, *args):
        Factory.CustomButtonChapter(text='txt', size_hint=(1, None), height="50dp")
        self.threadListChapter = threading.Thread(target=self.getAllListChapter)
        self.threadListChapter.daemon = True
        self.threadListChapter.start()

    def getAllListChapter(self):
        title = self.ids.mangatittle_id.text
        for manga in mangaServer.listManga:
            if manga.title == title:
                break
        else:
            manga = None
        self.ids.listChapter_id.clear_widgets()
        for listChapter in manga.listChapter:
            patCh = re.compile('chapter-(.+?)b')
            a = patCh.findall(listChapter.linkChapter)[0]
            if a[-1] == '-':
                a = a[:-1]
            button = Factory.CustomButtonChapter(size_hint=(1, None), height="50dp",
                                                 chapter="Chapter " + a.replace('-', '.'),
                                                 update_chapter=listChapter.updatedChapter)
            self.ids.listChapter_id.add_widget(button)


class Server:
    def __init__(self, serverLink, linkMangaPattern):
        self.counterManga = 0
        self.counterPage = 1
        self.serverLink = serverLink
        self.webpage = []
        self.listIconNull = ['i-can-modify-the-timeline-of-everything','utsuro-naru-regalia']
        self.webpage.append(getWebpage(self.serverLink).decode('utf-8'))
        self.listManga = []
        self.listMangaIcon = []
        self.listMangaJunk = []
        self.listMangaIconNull = []
        self.totalListManga = 0
        self.linkMangaPattern = linkMangaPattern
        self.getMangaList()
        self.getLastIndex()
        self.threadAllWebpage = threading.Thread(target=self.getAllWebPage)
        # set daemon to true so the thread dies when app is closed
        self.threadAllWebpage.daemon = True
        # print(self.t1)
        self.threadAllWebpage.start()

    def getMangaList(self):
        listMangaJunk = self.linkMangaPattern.findall(self.webpage[self.counterPage - 1])
        self.listMangaJunk = listMangaJunk
        for mangaJunk in listMangaJunk:
            print(mangaJunk)
            for iconNull in self.listIconNull:
                print(iconNull)
                print(mangaJunk)
                if mangaJunk == iconNull:
                    print('yes')
                    self.listMangaIconNull.append(self.counterManga)
            manga = Manga(mangaJunk, self.webpage[self.counterPage - 1], self.counterManga, self.listMangaIconNull)
            self.listManga.append(manga)
            self.counterManga += 1
            if (self.counterManga == 2):
                break

    def getAllWebPage(self):
        for i in range(2, int(self.totalListManga)):
            print('jalan')
            serverLink = "https://komikcast.ch/daftar-komik/page/" + str(
                i) + "/?sortby=update"
            self.webpage.append(getWebpage(serverLink).decode('utf-8'))

    def getLastIndex(self):
        pat = re.compile('<a class="page-numbers" href="https://komikcast.ch/daftar-komik/page/(.+?)</a>')
        listPath = getMangaList(pat, getWebpage(self.serverLink).decode('utf-8'))
        lastIndex = listPath[len(listPath) - 1]
        lastIndex = re.sub(r'^.*?">', '', lastIndex)
        self.totalListManga = lastIndex


class Manga:
    def __init__(self, mangaJunk='', webpage='', counterManga=0, mangaIconNull=[]):
        if (mangaJunk == ''):
            self.linkIconPattern = re.compile('<img\s*src="https://komikcast.ch/wp-content/uploads/(.+?)\.')
            self.lastChapterPattern = re.compile(
                '<div\s*class=\"chapter\" href=\"https://komikcast.ch/chapter/.+?/\">\s+(.+?)\s+</div>')
            self.link = ''
            self.icon = ''
            self.title = ''
            self.webpage = ''
            self.lastChapter = ''
            self.listChapter = []
        else:
            mangaJunkIcon = mangaJunk
            self.linkIconPattern = re.compile('<img\s*src="https://komikcast.ch/wp-content/uploads/(.+?)\.')
            if len(mangaJunkIcon) > 25:
                mangaJunkIcon = mangaJunkIcon[:20]
            self.lastChapterPattern = re.compile('<div class=\"chapter\" href=\"https://komikcast.ch/chapter/(.+?)/')
            addedDetailLink = "https://komikcast.ch/komik/"
            self.link = addedDetailLink + mangaJunk + "/"
            print(mangaIconNull)
            imageIcon, linkIcon = getImageIcon(self.linkIconPattern, webpage, counterManga, mangaIconNull)
            self.icon = linkIcon
            self.title = mangaJunk.replace('-', ' ') if mangaJunk else ''
            self.getLastChapter(webpage, counterManga)
            self.webpage = getWebpage(self.link).decode('utf-8')
            self.getLastUpdated()
            self.listChapter = []
            self.getListChapter()

    def getListChapter(self, i=0):
        listMangaChapPat = re.compile(
            '<a\s+class=\"chapter-link-item\"\s+href=\"https://komikcast.ch/chapter/(.+?)/.+\s+.+\s+.+\s+(.+?)\s+</div>')
        listChapterJunk = listMangaChapPat.findall(self.webpage)
        for chapter in listChapterJunk:
            ch = Chapter()
            ch.linkChapter = chapter[0]
            ch.updatedChapter = chapter[1]
            self.listChapter.append(ch)

    def getLastChapter(self, webpage, counterManga):
        listChap = self.lastChapterPattern.findall(webpage)
        lastChapPat = re.compile('<div\s+class=\"chapter\"\s+href=\"https://komikcast.ch/chapter/' + listChap[
            counterManga] + '.+?>\s+(.+?)\s+</div>')
        self.lastChapter = lastChapPat.findall(webpage)[0]

    def getLastUpdated(self):
        lastch = self.lastChapter
        lastch = lastch.replace('Ch.', '')
        pat = re.compile('Chapter\s*' + lastch + '</a>\s*<div class=\"chapter-link-time\">\s*(.+?)</div>')
        self.lastUpdated = pat.findall(self.webpage)[0]


class Chapter:
    def __init__(self):
        self.linkChapter = ''
        self.updatedChapter = ''
        self.listChapterImage = []


class MainView(MDApp):
    sm = Builder.load_file("test.kv")
    listLinkManga = []
    listButton = []

    def build(self):
        return self.sm

    def on_start(self):
        # testi=0
        for manga in mangaServer.listManga:
            button = Factory.CustomButton(title=manga.title if manga else '', size_hint=(1, None),
                                          halign='center', valign='bottom', height="400dp", image_source=manga.icon,
                                          last_chapter=manga.lastChapter, last_updated=manga.lastUpdated)
            button.bind(size=self.resize)
            button.bind(on_press=lambda x, manga=manga: self.open_manga(manga))
            self.listButton.append(button)
            self.root.get_screen('ListMangaScreen').ids.listManga_id.add_widget(button)
        self.root.get_screen('ListMangaScreen').ids.listManga_id.remove_widget(
            self.root.get_screen('ListMangaScreen').ids.remove_id)
        self.t1 = threading.Thread(target=self.my_callback)
        # set daemon to true so the thread dies when app is closed
        self.t1.daemon = True
        # print(self.t1)
        self.t1.start()
        # print('test thread pass')

    def my_callback(self):
        if mangaServer.counterPage < 5:
            if mangaServer.counterManga < len(mangaServer.listMangaJunk):
                if mangaServer.listMangaJunk[mangaServer.counterManga] == 'i-can-modify-the-timeline-of-everything':
                    mangaServer.listMangaIconNull.append(mangaServer.counterManga)
                manga = Manga(mangaServer.listMangaJunk[mangaServer.counterManga],
                              mangaServer.webpage[mangaServer.counterPage - 1],
                              mangaServer.counterManga, mangaServer.listMangaIconNull)
                mangaServer.listManga.append(manga)
                button = Factory.CustomButton(title=manga.title if manga else '', size_hint=(1, None),
                                              halign='center', valign='bottom', height="400dp", image_source=manga.icon,
                                              last_chapter=manga.lastChapter, last_updated=manga.lastUpdated)
                button.bind(size=self.resize)
                button.bind(on_press=lambda x, manga=manga: self.open_manga(manga))
                self.listButton.append(button)
                self.root.get_screen('ListMangaScreen').ids.listManga_id.add_widget(button)
                mangaServer.counterManga += 1
                # print(manga.icon)
            else:
                mangaServer.counterPage += 1

                # serverLink = "https://komikcast.ch/daftar-komik/page/" + str(
                #     mangaServer.counterPage) + "/?sortby=update"
                # mangaServer.webpage.append(getWebpage(serverLink).decode('utf-8'))

                # print(mangaServer.counterManga)
                mangaServer.counterManga = 0
                mangaServer.listMangaIconNull = []
                # print(mangaServer.counterManga)
                # mangaServer.getMangaList()
                listMangaJunk = mangaServer.linkMangaPattern.findall(mangaServer.webpage[mangaServer.counterPage - 1])
                mangaServer.listMangaJunk = listMangaJunk
            self.my_callback()
        else:
            print(self.t1)

    def open_manga(self, manga=Manga()):
        self.sm.get_screen('NewGameScreen').ids.icon_id.source = manga.icon
        self.sm.current = "NewGameScreen"
        self.sm.get_screen('NewGameScreen').ids.mangatittle_id.text = manga.title
        # self.sm.get_screen('NewGameScreen').ids.mangatittleBig_id.text = manga.title

    def resize(self, butt, new_size):
        butt.text_size = new_size


def getWebpage(serverLink):
    # default_headers = urllib3.make_headers(proxy_basic_auth='myusername:mypassword')
    # proxy = urllib3.ProxyManager("https://myproxy.com:8080/", proxy_headers=default_headers)
    # r = proxy.urlopen('GET', serverLink)
    #
    # print(r.data.decode('utf-8'))
    req = Request(
        url=serverLink,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    # gcontext = ssl.SSLContext()
    webpage = urlopen(req).read()
    return webpage


# Press the green button in the gutter to run the script.

serverLink = "https://komikcast.ch/daftar-komik/?sortby=update"
linkMangaPattern = re.compile('<a href="https://komikcast.ch/komik/(.+?)/"')
mangaServer = Server(serverLink, linkMangaPattern)
if __name__ == '__main__':
    app = MainView()
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
