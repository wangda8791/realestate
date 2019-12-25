import scrapy
from bs4 import BeautifulSoup

from ..items import ScrapperItem
from ..utils import Util


class FSBOSpider(scrapy.Spider):
    name = 'fsbo'
    start_urls = ['https://fsbo.com/listings/search/']
    search_url = 'https://fsbo.com/listings/search/basicsearch/'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'Cache-Control': "max-age=0",
        'Connection': 'keep-alive',
        'Host': 'fsbo.com',
        'Referer': 'https://fsbo.com/listings/search/',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/79.0.3945.88 Safari/537.36',
    }

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response=response,
            formid='submitstate',
            formdata={
                'paging': '1',
                'page': '2',
                'size': '100000000',
                'sort': 'distance asc'
            },
            callback=self.success_parse)

    def success_parse(self, response):
        houses = response.css('.listings .listing-right a::attr(href)').extract()
        for house in houses:
            yield response.follow(house, headers=self.headers, callback=self.house_parse_with_link(house))

    def house_parse_with_link(self, link):
        def house_parse(response):
            soup = BeautifulSoup(response.body, 'html.parser')
            infos = soup.select('#sellerModal div.modal-body > div:nth-child(1) > div')
            owner_name = ''
            owner_contact = ''
            for index in range(len(infos)):
                if infos[index].text.strip() == "Contact:":
                    owner_name = infos[index + 1].text.strip()
                if infos[index].text.strip() == "Phone:":
                    contact_candidate = Util.normalize_phone(infos[index + 1].text.strip())
                    if contact_candidate.find('@') == -1:
                        owner_contact = contact_candidate
            if owner_contact == '':
                return

            address = Util.normalize_address(address=soup.select("span.address")[0].text)

            images = soup.select('#imageGallery li')
            image = soup.select('#listing-images img')
            image_url = ''
            if len(images) > 0:
                image_url = 'https://fsbo.com' + images[0]['data-src']
            elif len(image) > 0:
                image_url = 'https://fsbo.com' + image[0]['src']

            description = soup.select('div.property-description')[0].text
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
