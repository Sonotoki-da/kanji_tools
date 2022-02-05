from pprint import pprint
import scrapy
from scrapy.http.response.html import HtmlResponse
from anki_tool import invoke


class KanjiSpider(scrapy.Spider):
    name = "kanji"
    # start_urls = [
    #     f'https://jlptsensei.com/jlpt-n{x}-kanji-list/' for x in range(5, 0, -1)
    # ]
    start_urls = ['https://jlptsensei.com/jlpt-n5-kanji-list/']

    def parse(self, response: HtmlResponse):
        kanji_dict = {
            'kanji': [],
            'on': [],
            'kun': [],
            'en': []
        }
        kanji_dict['kanji'] = response.css("a[class='jl-link jp']::text").getall()
        kanji_dict['on'] = response.css("td[class='jl-td-on align-middle'] > a > p::text").getall()
        kanji_dict['kun'] = response.css("td.jl-td-kun.align-middle > a > p::text").getall()
        kanji_dict['en'] = response.css("td.jl-td-m.align-middle::text").getall()
        for key in kanji_dict:
            pprint(invoke(
                'addNote',
                note={
                    'deckName': 'JLPT Sensei N5 Kanji',
                    'modelName': 'japanese',
                    'fields': {
                        'Kanji': kanji
                    }
                }
            ))
        kanji = response.xpath('//*[@class="jl-link jp"]/text()').getall()
