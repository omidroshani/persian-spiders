import scrapy
import json
import requests


class RadioJavanSpider(scrapy.Spider):
    name = 'radio_javan'
    allowed_domains = ['radiojavan.com']
    current_page = 700
    base_url = 'https://www.radiojavan.com'

    def start_requests(self):
        yield scrapy.Request(
            url =f'https://www.radiojavan.com/mp3s/content?type=featured&query=all&page={self.current_page}',
            callback = self.parse
        )

    def get_details_of_item(self, response):
        item = response.meta['item']
        item['likes'] = response.xpath(".//span[@class='rating']/text()").get().replace(' likes', '').replace(',', '')

        item['album'] = response.xpath(".//div[@class='songInfo']//span[@class='album']/text()").get()
        item['album_fa'] = response.xpath(".//div[@class='farsiText']//span[@class='album']/text()").get()
        item['song_fa'] = response.xpath(".//div[@class='farsiText']//span[@class='song']/text()").get()
        item['artist_fa'] = response.xpath(".//div[@class='farsiText']//span[@class='artist']/text()").get()
        item['dateAdded'] = response.xpath(".//div[@class='mp3Description']//div[@class='dateAdded']/text()").get().replace('Date Added: ', '')
        item['plays'] = response.xpath(".//div[@class='mp3Description']//div[@class='views']/text()").get().replace('Plays: ', '').replace(',', '')

        response = requests.post(url='https://www.radiojavan.com/mp3s/mp3_host', data={'id':item['id']})
        item['file'] = f'{response.json()["host"]}/media/mp3/mp3/{item["id"]}.mp3'


        yield item
        

    def parse(self, response):
        
        items = response.xpath("//div[@class ='itemContainer']")
        for item in items:
            item = {
                'id': item.xpath(".//a/@href").get().split('/')[-1],
                'song': item.xpath(".//span[@class ='song']/text()").get(),
                'artist': item.xpath(".//span[@class ='artist']/text()").get(),
                'link': f'{self.base_url}{item.xpath(".//a/@href").get()}',
                'cover': item.xpath(".//img/@src").get(),
            }
            yield scrapy.Request(url = item['link'],callback=self.get_details_of_item,meta={'item':item})

        if len(items) == 0:
            return


        self.current_page += 1
        yield scrapy.Request(
            url = f'https://www.radiojavan.com/mp3s/content?type=featured&query=all&page={self.current_page}',
            callback = self.parse
        )

