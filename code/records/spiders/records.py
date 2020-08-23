import scrapy

# links = '//div[@class="explore-list-inner"]/a/@href''
# next_page_link = '//li[@class="pagination-next"]/a/@href'
# records' name = '//div[@class="page-header block block-11-12"]/h1/text()'

# Need to improve what

#what = what.strip() # --> removes only left white space
#what = ''.join(what.split()) # --> removes all white space

class RecordsSpider(scrapy.Spider):
    name = 'records'
    start_urls = ['https://www.guinnessworldrecords.com/records/showcase/human-body?page=1']

    custom_settings = {
        'FEED_URI': 'records.json',
        'FEED_FORMAT': 'json',
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'PepitoMartinez',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }


    def parse_note(self, response, **kwargs):
        if kwargs:
            link = kwargs['link']
        
        record = response.xpath('//div[@class="page-header block block-11-12"]/h1/text()').get()
        body = response.xpath('//p[not(@class)]/text()').get()
        body = body.replace('\n','').replace('\t','')
        image_src = response.xpath('//div[@class="region-inner"]//img/@src').get()
        image = response.urljoin(image_src)

        who_section = response.xpath('//div[@class="equal-one block block-4-12"]/dd/text()').get()
        if who_section: 
            who = who_section

        what_section = response.xpath('//dt/text()="What"').get()
        if what_section == '1':
            what = response.xpath('//section[@class="record-details block block-8-12"]//div[2]/dd/text()').get()
            what = what.replace('\n', '').replace('  ', '') # removes all white
            where = response.xpath('//section[@class="record-details block block-8-12"]//div[3]/dd/text()').get()
            where = where.replace('\n','').replace('  ', '')
            yield {
                'record': record,
                'who': who,
                'what' : what,
                'desc': body,
                'where': where,
                'image': image,
                'url': link
            }
        else:
            where = response.xpath('//section[@class="record-details block block-8-12"]//div[2]/dd/text()').get()
            where = where.replace('\n','').replace('  ', '')
            yield {
                'record': record,
                'who': who,
                'desc': body,
                'where': where,
                'image': image,
                'url': link
            }
            



    def parse_link(self, response, **kwargs):
        if kwargs:
            links = kwargs['links']
        
        links.extend(response.xpath('//div[@class="explore-list-inner"]/a/@href').getall())

        next_page_button_link = response.xpath('//li[@class="pagination-next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_link, cb_kwargs={'links': links})
        else: 
            for link in links:
                yield response.follow(link, callback=self.parse_note, cb_kwargs={'link': response.urljoin(link)})


    def parse(self, response):

        links = response.xpath('//div[@class="explore-list-inner"]/a/@href').getall()

        next_page_button_link = response.xpath('//li[@class="pagination-next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_link, cb_kwargs={'links': links})

