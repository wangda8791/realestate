import re
from abc import ABC

import scrapy
from bs4 import BeautifulSoup

from ..items import ScrapperItem


class FSBOSpider(scrapy.Spider, ABC):
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
    state = ''
    page = 0
    houses = []

    def parse(self, response):
        states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
                  'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
                  'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC',
                  'MH', 'AE', 'AA', 'AE', 'AE', 'AE', 'AP']
        # for state in states:
        self.state = 'TX'
        self.page = 1
        self.houses = []
        yield scrapy.FormRequest.from_response(
            response=response,
            formid='submitstate',
            formdata={
                'searchQuery': self.state,
                'paging': '1',
                'page': str(self.page),
                'size': '100',
                'sort': 'distance asc'
            },
            callback=self.success_parse)

    def success_parse(self, response):
        house_links = response.css('.listings .listing-right a::attr(href)').extract()
        self.houses = self.houses + house_links
        print(self.page, len(house_links))
        if self.page == 2:
            print(response.body)

        if len(response.css('.nextPage')) == 0:
            # for house in self.houses:
            #     yield response.follow(house, headers=self.headers, callback=self.house_parse)
            pass
        else:
            self.page += 1
            # yield response.follow(
            #     url=self.search_url,
            #     headers=self.headers,
            #     method='POST',
            #     body='paging=1&page=' + str(self.page) + '&size=100&sort=distance+asc',
            #     callback=self.success_parse)
            yield scrapy.FormRequest.from_response(
                response=response,
                formid='pagingForm',
                formdata={
                    'searchQuery': self.state,
                    'paging': '1',
                    'page': str(self.page),
                    'size': '100',
                    'sort': 'distance asc'
                },
                callback=self.success_parse)

    def house_parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        house_id = soup.select('table.listing-data tr:first-child td')[1].text
        link = 'https://fsbo.com/listings/listings/show/id/' + house_id + '/'
        infos = soup.select('#sellerModal div.modal-body > div:nth-child(1) > div')
        owner_name = ''
        owner_contact = ''
        for index in range(len(infos)):
            if infos[index].text.strip() == "Contact:":
                owner_name = infos[index + 1].text.strip()
            if infos[index].text.strip() == "Phone:":
                contact_candidate = self.normalize_phone(infos[index + 1].text.strip())
                if contact_candidate.find('@') == -1:
                    owner_contact = contact_candidate
        if owner_contact == '':
            return

        address = self.normalize_address(address=soup.select("span.address")[0].text)

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

    def normalize_address(self, address):
        address = address.strip().replace('\n', ', ')
        address = re.sub(r'\s+', ' ', address)
        address = address.replace(' ,', ',')
        return address

    def normalize_phone(self, phone):
        phone = phone.lower().split('ext')[0].strip()
        phone = re.sub(r'[\s\-\(\)A-Za-z\.]+', '', phone)
        if len(phone) == 11 and phone[0] == '1':
            phone = phone[1:]
        return phone
