import scrapy
from bs4 import BeautifulSoup

from ..items import ScrapperItem
from ..utils import Util


class ForSaleByOwnerSpider(scrapy.Spider):
    name = 'forsalebyowner'
    start_urls = ['https://www.forsalebyowner.com/homes-for-sale/']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'Cache-Control': "max-age=0",
        'Connection': 'keep-alive',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/79.0.3945.88 Safari/537.36',
    }

    def __init__(self):
        pass

    def parse(self, response):
        base_url = 'https://www.forsalebyowner.com/search/list/'
        urls = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware',
                'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky',
                'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri',
                'montana', 'nebraska', 'nevada', 'new_hampshire', 'new_jersey', 'new_mexico', 'new_york',
                'north_carolina', 'north_dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode_island',
                'south_carolina', 'south_dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
                'district-of-columbia', 'west_virginia', 'wisconsin', 'wyoming']

        for url in urls:
            url = base_url + url
            yield scrapy.Request(
                url=url,
                callback=self.success_parse)

    def success_parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        group = soup.select('.js-listings-list ol')
        if len(group) == 0:
            return
        elif len(group) == 1:
            houses = soup.select('.js-listings-list ol')[0].select('li div.estate-bd > a')
        else:
            houses = soup.select('.js-listings-list ol')[1].select('li div.estate-bd > a')

        for house in houses:
            yield response.follow(house['href'], headers=self.headers,
                                  callback=self.house_parse_with_link(house['href']))

    def house_parse_with_link(self, link):
        def house_parse(response):
            soup = BeautifulSoup(response.body, 'html.parser')
            owner_name = ''
            owner_contact = Util.normalize_phone(soup.select('#contact span strong')[0].text)
            if owner_contact == '':
                return
            address = Util.normalize_address(soup.select('ul[itemprop=address]>li')[0].text)
            image_url = ''
            images = soup.select('#gallery img')
            if len(images) > 0:
                image_url = images[0]['data-image']
            description = soup.select('div.details')[0].text
            item = ScrapperItem()
            item['link'] = link
            item['address'] = address
            item['image_url'] = image_url
            item['description'] = description
            item['owner_name'] = owner_name
            item['owner_contact'] = owner_contact
            item['active_search'] = ''

            yield item

        return house_parse
