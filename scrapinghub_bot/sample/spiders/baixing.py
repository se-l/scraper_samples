# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import datetime


class Spider(scrapy.Spider):

    name = "baixing"
    # key_url = 'search/?query={0}'
    regions = ['shanghai','beijing','tianjin','chongqing','jiangsu','zhejiang','fujian','shandong','jiangxi','anhui',
               'guangdong','hannan','guangxi','hubei','hunan','hebei','shanxi', 'liaoning','jilinn','heilongjiang',
               'sichuan','xizang','yunnan','guizhou','shaanxi','xinjiang','qinghai','ningxia','gansu']
    start_urls = ['http://baixing.com/']
    url_template = 'http://{0}.baixing.com/search/?query={1}'
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    item_fields = ['word', 'date_scraped', 'url'
                   'user_id', 'user_name', 'post_content', 'post_datetime', 'post_id',
                   #'comment_user_id', 'comment_user_name', 'comment_content', 'comment_datetime', 'comment_id',
                   'image_urls', 'image_post_id',
                   # Baxing specific
                   'post_title', 'region', 'other_details']

    def parse(self, response):
        for region in self.regions:
            for word in self.settings.get('KEYWORDS'):
                url = self.url_template.format(region, word)
                self.log('Parse_keyword: {}'.format(url))
                yield scrapy.Request(url=url, callback=self.parse_keyword,
                                     meta={"word": word, "region": region})

    def parse_keyword(self, response):
        article_urls = response.xpath('//div/ul[@class="list-ad-items"]/li/a[contains(@href, "http")]/@href').extract()

        for article_url in article_urls:
            yield scrapy.Request(url=article_url, callback=self.parse_article,
                                 meta={'word': response.meta['word'], 'region': response.meta['region']})

        next_page_url = self.extract(response, '//ul[@class="list-pagination"]//li[last()]/a/@href')
        if next_page_url is not None and len(next_page_url) > 0:
            next_page_url = response.urljoin(next_page_url[0])
            self.log(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse_keyword,
                                 meta={'word': response.meta['word'], 'region': response.meta['region']})

    def parse_article(self, response):
        r = {k: None for k in self.item_fields}
        r['word'] = response.meta['word']
        r['date_scraped'] = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
        r['region'] = response.meta['region']
        r['post_title'] = self.extract(response, '//div[@class="viewad-title"]//h1/text()')
        r['user_name'] = self.extract(response, '//div[@class="viewad-meta2-item"]//div[@class="content"]//span//text()')  # company name
        r['user_id'] = self.extract(response, '//a[@class="poster-name"]//text()')
        r['other_details'] = self.extract(response, '//div[contains(@class, "viewad-meta2-item fuwu-content")]//text()')
        r['post_content'] = self.extract(response, '//div[contains(@class, "viewad-text")]//text()')
        r['post_datetime'] = self.extract(response, '//div[@class="viewad-info-line"]/div/span[1]')
        r['post_id'] = response.url
        r['user_wechat_img'] = self.extract(response, '//span[@class="sendMobile"]/a/img/@src')
        image_urls_raw = self.extract(response, '//div[@class="viewad-content "]//div[contains(@class, "photo")]//@style')
        r['image_urls'] = self.get_urls(image_urls_raw)
        if len(r['user_wechat_img']) > 0:
            r['image_urls'].append(r['user_wechat_img'][0])
        r['image_urls'] = [self.prepend_url_schema(url) for url in r['image_urls']]
        r['image_post_id'] = response.url
        r['url'] = response.url
        yield r

    @staticmethod
    def get_urls(style):
        # style ="background:url(http://img6.baixing.net/56a266c08fc234faad4740d1e10f0bf4.jpg_biwbp) center center"
        if type(style) != list:
            style = [style]
        urls = []
        for txt in style:
            ix = txt.find('url(')
            if ix < 0:
                continue
            else:
                urls.append(txt[ix+4: txt.find(')')])
        return urls

    @staticmethod
    def prepend_url_schema(url):
        if url[:2] == r"//":
            return "https:" + url
        else:
            return url

    @staticmethod
    def extract(response, xpath):
        return Selector(response).xpath(xpath).extract()

    @staticmethod
    def extract_first(response, xpath):
        return Selector(response).xpath(xpath).extract_first()
