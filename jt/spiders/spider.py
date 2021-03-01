import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import JtItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class JtSpider(scrapy.Spider):
	name = 'jt'
	start_urls = ['http://www.jtbanka.hr/novosti/13?godina=2021']

	def parse(self, response):
		yield response.follow(response.url, self.parse_article, dont_filter=True)

		next_page = response.xpath('//div[@class="important_links hide-on-small-only"]//a/@href').getall()[:-1]
		yield from response.follow_all(next_page, self.parse)

	def parse_article(self, response):
		year = response.xpath('//div[@class="section_title with_border"]/text()').get()
		articles = response.xpath('//ul[@class="expandable_list"]/li')
		items = []
		for article in articles:
			date = article.xpath('.//div[@class="collapsible-header expandable_list_head"]//span[@class="day"]/text()').get()+'.'+ article.xpath('.//div[@class="collapsible-header expandable_list_head"]//span[@class="month"]/text()').get()+'.'+year
			title = article.xpath('.//div[@class="collapsible-header expandable_list_head"]/div[@class="title"]/div/text()').get()
			content = article.xpath('.//div[@class="collapsible-body"]//text()').getall()
			content = [p.strip() for p in content if p.strip()]
			content = re.sub(pattern, "",' '.join(content))


			item = ItemLoader(item=JtItem(), response=response)
			item.default_output_processor = TakeFirst()

			item.add_value('title', title)
			item.add_value('link', response.url)
			item.add_value('content', content)
			item.add_value('date', date)
			items.append(item.load_item())
		return items

