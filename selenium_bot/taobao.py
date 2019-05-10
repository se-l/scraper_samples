import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import sys, os, json, datetime
import numpy as np
import importlib.util
import pickle
import ctypes

# custom imports
class Paths:
    base = r'your_path\selenium'
    logger = r'your_path\selenium\common\logger.py'
    log = r'your_path\selenium\logs'
    settings = r'your_path\iomv2\settings.py'
    img_path = r'your_path\selenium\img'
    data = r'your_path\selenium\data'


spec = importlib.util.spec_from_file_location("Logger", Paths.logger)
py_logger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(py_logger)
Logger = py_logger.Logger
Logger.init_log(os.path.join(Paths.log, 'log_{}'.format(datetime.date.today())))

spec = importlib.util.spec_from_file_location("KEYWORDS", Paths.settings)
py_settings = importlib.util.module_from_spec(spec)
py_settings = spec.loader.exec_module(py_settings)

class XPaths:
    tb_main_search_bar = '//input[@type="search"]'
    listing_search_bar = '//*[contains(@class, "search-combobox-input-wrap")]'
    itemlist = '//*[contains(@class, "m-itemlist")]'

class Pages:
    login = 0
    tbmain = 1
    listings = 2
    listings_wo_results = 3
    page_after_login = 4
    product = 5

class TaobaoSpider():

    extension_directory = r'your_path\selenium'  #extension
    path_chrome = r'your_webdriver_path\chromedriver_win32_42\chromedriver.exe'
    start_url = r'https://login.taobao.com'
    driver = None
    settings_path = r'your_path\iomv2'
    settings = py_settings
    tb_username = 'your_tb_username'
    tb_password = 'your_tb_password'
    tb_mobile_number = None
    max_listing_pages = 2
    dataStore = None

    item_fields = ['word', 'date_scraped', 'url',
                   'user_id', 'user_name', 'post_content', 'post_datetime', 'post_id',
                   'comments',
                   'image_urls', 'image_post_id',
                   # taobao specifics
                   'price', 'post_title', 'sell_count', 'comment_reply', 'product_origin'
                   ]
    comment_fields = ['comment_user_id', 'comment_user_name', 'comment_content',
                       'comment_datetime', 'comment_id', 'comment_img_urls']

    KEYWORDS = ['sample_keyword1', 'sample2']

    def start_browser(s):
        options = webdriver.ChromeOptions()
        options.add_argument(f'load-extension={s.extension_directory}')
        options.add_argument("--start-maximized")
        # chrome_options.add_argument('--disable-extensions')
        # chrome_options.add_argument('--profile-directory=Default')
        # options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery")
        # # chrome_options.add_experimental_option("excludeSwitches",
        # #                                        ["ignore-certificate-errors",
        # #                                         "safebrowsing-disable-download-protection",
        # #                                         "safebrowsing-disable-auto-update",
        # #                                         "disable-client-side-phishing-detection"]
        # #                                        )
        s.driver = webdriver.Chrome(s.path_chrome, chrome_options=options)
        # go taobao main page
        s.driver.get(s.start_url)
        ctypes.windll.user32.MessageBoxW(0, "Login complete?", "ALERT", 1)

    def scrape(s):
        # loop over key words
        for word in s.KEYWORDS:
            s.dataStore = DataStore(word)
            try:
                # enter search search
                cnt_tabs = s.driver.window_handles
                s.search_from_main(word)
                # identify new page
                ActionChains(s.driver).pause(1)
                if s.driver.window_handles > cnt_tabs:
                    # close main search bar where we come from. now only use listing search
                    s.driver.switch_to.window(s.driver.window_handles[0])
                    s.close_tab()
                    # s.driver.switch_to.window(s.driver.window_handles[-1])
                page = s.identify_page()
                if page == Pages.login:
                    s.tb_login()
                    s.parse_listings(word)
                elif page == Pages.tbmain:
                    s.scrape()  # if somehow falling into this -> infinite loop
                elif page == Pages.listings:
                    s.parse_listings(word)
                elif page == Pages.listings_wo_results:
                    Logger.info('Keyword {}: No results'.format(word))
                    continue
                else:
                    Logger.info('Lost our way at {}'.format(word))
                    raise ('Dont know where we are')
                    # send a webhook to Slack in case of this
                s.dataStore.store_record()
            except Exception as e:
                Logger.debug('Error processing word {}. Traceback: {}'.format(word, e.__traceback__))
                continue

    def parse_listings(s, word):
        # product_urls = s.extract('//*[contains(@class, "m-itemlist")]//*[contains(@class, "pic")]/@data-href')
        # product_urls = [s.prepend_url_schema(url) for url in product_urls]

        next_button = True
        listing_page = 0
        while next_button and listing_page < s.max_listing_pages:
            product_elem = s.driver.find_elements_by_xpath('//*[contains(@class, "m-itemlist")]//div/div/a[contains(@class, "pic") and not(contains(@href, "tmall"))]')
            for product in product_elem:
                cnt_tabs = len(s.driver.window_handles)
                actions = ActionChains(s.driver)
                actions.pause(np.random.randint(200, 600) / 1000)
                # actions.perform()
                # s.move_w_delay_to(product, 5, 5)
                # actions = ActionChains(s.driver)
                actions.click(product)
                actions.pause(np.random.randint(200, 600) / 1000)
                # actions.click()
                actions.perform()
                # load post
                s.driver.implicitly_wait(2)
                # did a new tab open?
                if len(s.driver.window_handles) > cnt_tabs:
                    s.driver.switch_to.window(s.driver.window_handles[-1])
                # check it's a product site
                page = s.identify_page()
                if page == Pages.product:
                    s.parse_product(word)
                    s.close_tab()
                elif page == Pages.login:
                    s.tb_login()
                    if len(s.driver.window_handles) > cnt_tabs:
                        s.driver.switch_to.window(s.driver.window_handles[-1])
                    s.parse_product(word)
                    s.close_tab()
            next_button = s.elem_xpath('//*[@id="mainsrp-pager"]//li[@class="item next"]/a')
            if next_button:
                ok = s.click_next()
                s.driver.implicitly_wait(2)
                listing_page += 1
            # ActionChains(s.driver).pause(1)
            # else means while loop stops because next button is false condition in while

    def click_next(s):
        next_button = s.elem_xpath('//*[@id="mainsrp-pager"]//li[@class="item next"]/a')
        if next_button is False:
            return False
        actions = ActionChains(s.driver)
        actions.pause(0.1)
        actions.click(next_button)
        # actions.move_to_element_with_offset(next_button, 5, 5).click()
        # s.move_w_delay_to(next_button, 2, 2)
        # actions = ActionChains(s.driver)
        actions.pause(0.5)
        actions.perform()
        return True

    def move_w_delay_to(s, elem, off_x, off_y):
        html_00 = s.driver.find_element_by_xpath('//*[@id]')
        # html_00 = s.driver.find_element_by_xpath('/html')
        tx = elem.location['x'] + off_x + 10
        ty = elem.location['y'] + off_y + 10
        i_dx = int(tx / 2)
        i_dy = int(ty / 2)
        steps_xy = min(i_dx, i_dy)
        steps_single = max(i_dx, i_dy) - steps_xy
        actions = ActionChains(s.driver)
        actions.move_to_element_with_offset(html_00, -html_00.location['x'], -html_00.location['y']).perform()
        actions = ActionChains(s.driver)
        actions.pause(0.005)
        # go to 0,0
        for i in range(0, steps_xy):
            actions.move_by_offset(2, 2)
            actions.pause(0.002)
        actions.perform()
        # ActionChains(s.driver).context_click().perform()
        actions = ActionChains(s.driver)
        for i in range(0, steps_single):
            if i_dx > i_dy:
                actions.move_by_offset(2, 0)
            else:
                actions.move_by_offset(0, 2)
            actions.pause(0.002)
        actions.perform()

    def close_tab(s):
        s.driver.close()
        # ActionChains(s.driver).send_keys(Keys.LEFT_CONTROL + 'w').perform()
        s.driver.switch_to.window(s.driver.window_handles[-1])

    def elem_id(s, id):
        return '//li[@id="{}"]'.format(id)

    def parse_product(s, word):
        s.driver.implicitly_wait(1)
        """Note that the xpath selectors are written such as that is also works with tmall tb/tm prefixes"""
        r = {k: None for k in s.item_fields}
        # for i in range(3):
        #     s.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        r['word'] = word
        r['date_scraped'] = datetime.datetime.today().strftime('%Y%m%d')
        r['post_id'] = s.driver.current_url  # ID is in there
        r['url'] = s.driver.current_url  # ID is in there
        r['post_datetime'] = None  # reference scrape date. datetime not shown in tb or tm

        # Xpath for TB
        x_prices = '//*[contains(@class, "-property")]//*[contains(@class, "-price")]//*[contains(@class, "-rmb-") or contains(@class, "-price")]'
        r['price'] = '||'.join(e.text for e in s.driver.find_elements_by_xpath(x_prices))
        r['post_content'] = ' '.join([e.text for e in s.driver.find_elements_by_xpath('//div[@id="description"]')])

        r['image_urls'] = [e.get_attribute('src') for e in s.driver.find_elements_by_xpath(
            '//*[contains(@id, "description")]//table//img//@src | //*[contains(@id, "description")]//p//img')]
        # append profile image
        prof_img = s.elem_xpath_w_attr('//img[@id="J_ImgBooth"]', 'src')
        if prof_img:
            r['image_urls'].append(prof_img)
        r['image_post_id'] = s.driver.current_url

        # TM AND TB SPECIFIC XPATHS FOLLOW
        x_title_tb = '//*[contains(@class, "-property")]'
        tb_shop_name = '//*[contains(@id,"ShopInfo")]//*[contains(@class,"shop-name")]'
        tb_seller_name = '//*[contains(@id,"ShopInfo")]//*[contains(@class,"seller-name")]'
        tb_sell_count = '//*[@id="J_SellCounter"]'
        tb_origin = '//*[@id="J-From"]'
        # Taobao
        # if s.elem_xpath(x_title_tb):
        r['post_title'] = s.elem_xpath_w_attr(x_title_tb, 'data-title')
        r['user_name'] = s.elem_xpath_w_text(tb_shop_name)
        r['user_id'] = s.elem_xpath_w_text(tb_seller_name)
        # r['sell_count'] = s.driver.find_element_by_xpath(tb_sell_count).text
        r['origin'] = s.elem_xpath_w_text(tb_origin)
        s.open_reviews('tb')
        # COMMENTS
        r['comments'] = []
        comment_ids = [el.get_attribute('id') for el in s.driver.find_elements_by_xpath('//li[contains(@id, "review")]')]
        for comment_id in comment_ids:
            c = {k: None for k in s.comment_fields}
            c['comment_id'] = comment_id
            c['comment_user_name'] = [e.text for e in s.driver.find_elements_by_xpath(
                s.elem_id(comment_id) + '/div[1]/div')]
            c['comment_content'] = [e.text for e in s.driver.find_elements_by_xpath(
                s.elem_id(comment_id) + '//div[contains(@class, "ReviewContent")]')]
            c['comment_img_urls'] = [s.prepend_url_schema(e.get_attribute('src')) for e in s.driver.find_elements_by_xpath(
                s.elem_id(comment_id) + '//li[@class="photo-item"]')]
            c['comment_datetime'] = [e.text for e in s.driver.find_elements_by_xpath(
                 s.elem_id(comment_id) + '//*[@class="tb-r-date"]')]

            r['comments'].append(c)
        s.dataStore.append_record(r)

    def open_reviews(s, tba):
        if tba == 'tm':
            open_reviews = s.elem_xpath('//a[contains(@href, "Reviews")]')
        elif tba == 'tb':
            open_reviews = s.elem_xpath('//*[@id="J_TabBar"]/li[2]/a')
        else:
            return
        ActionChains(s.driver).click(open_reviews).perform()
        s.driver.implicitly_wait(0.5)
        s.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    @staticmethod
    def get_floats_in_list(text: list) -> list:
        r = []
        for t in text:
            try:
                r.append(float(t))
            except TypeError:
                continue
        return r

    @staticmethod
    def min_number(numbers: list):
        try:
            return min(numbers)
        except ValueError:
            return None

    def identify_page(s):
        if s.elem_xpath('//*[@id="TPL_username_1"]'):
            return Pages.login
        elif s.elem_xpath('//span[@class="icon-supple-tips-cry"]'):
            return Pages.listings_wo_results
        elif s.elem_xpath('//*[contains(@class, "m-itemlist")]'):
            return Pages.listings
        elif s.elem_xpath(XPaths.tb_main_search_bar):
            return Pages.tbmain
        # elif s.driver.find_element_by_xpath() is not None:
        #     return Pages.page_after_login
        elif s.elem_xpath('//div[@id="J_DivItemDesc"] | //div[@id="J_DetailMeta"]'):
            return Pages.product
        else:
            return -1

    def elem_xpath(s, xpath):
        try:
            return s.driver.find_element_by_xpath(xpath=xpath)
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def elem_xpath_w_attr(s, xpath, attr):
        try:
            elem = s.driver.find_element_by_xpath(xpath=xpath)
            try:
                return elem.get_attribute(attr)
            except AttributeError:
                Logger.info('Didnt find attribute {}'.format(attr))
        except selenium.common.exceptions.NoSuchElementException:
            Logger.info('Didnt find element for {}'.format(xpath))
            return False

    def elem_xpath_w_text(s, xpath):
        try:
            elem = s.driver.find_element_by_xpath(xpath=xpath)
            try:
                return elem.text
            except AttributeError:
                Logger.info('Didnt find text')
        except selenium.common.exceptions.NoSuchElementException:
            Logger.info('Didnt find element for {}'.format(xpath))
            return False

    def elem_attr(s, attr):
        if s is False:
            print('No element provided to find attribute')
        else:
            return s.get_attribute(attr)


    def search_from_main(s, word):
        tbmain_search_bar = s.elem_xpath(XPaths.tb_main_search_bar)
        if not tbmain_search_bar:
            tbmain_search_bar = s.elem_xpath(XPaths.listing_search_bar)
            if not tbmain_search_bar:
                s.driver.get('https://world.taobao.com/')
                s.driver.implicitly_wait(1)
                tbmain_search_bar = s.elem_xpath(XPaths.tb_main_search_bar)
                # raise ("Couldnt find search bar")
        # s.move_w_delay_to(tbmain_search_bar, 100, 5)
        actions = ActionChains(s.driver)
        # move_to_element_with_offset(tbmain_search_bar, 5, 5).
        actions.click(tbmain_search_bar)
        actions.pause(np.random.randint(400, 800) / 1000)
        actions.send_keys(Keys.END)
        actions.pause(np.random.randint(90, 100) / 1000)
        for i in range(10):
            actions.send_keys(Keys.BACKSPACE)
            actions.pause(np.random.randint(40, 80) / 1000)
        for key in word:
            actions.send_keys(key)
            actions.pause(np.random.randint(400, 800) / 1000)
        actions.send_keys(Keys.ENTER)
        # load time - but combine with check for elements or addListener document.onload, but tb has some long running scripts even
        # when page appears fully loaded
        actions.pause(1)
        actions.perform()

    @staticmethod
    def delayed_key_input(actions, key_input):
        for key in key_input:
            actions.send_keys(key)
            actions.pause(np.random.randint(400, 800) / 1000)
        return actions

    def tb_login(s):
        username = s.elem_xpath('//*[@id="TPL_username_1"]')
        s.move_w_delay_to(username, 100, 10)
        actions = ActionChains(s.driver)
        actions.click()
        # actions.send_keys(Keys.TAB)
        # actions.move_to_element_with_offset(username, 10, 5).click()
        actions.pause(np.random.randint(400, 800) / 1000)

        actions = s.delayed_key_input(actions, s.tb_username)
        actions.send_keys(Keys.TAB)
        actions.pause(np.random.randint(400, 800) / 1000)
        # elem = s.driver.find_element_by_xpath('//*[@id="TPL_password_1"]')
        # elem.click()
        actions = s.delayed_key_input(actions, s.tb_password)
        actions.pause(np.random.randint(400, 800) / 1000)
        actions.perform()
        """if a captcha is requested, high chance that despite solving the captcha tb wont let us in
        because it has decided it's a bot for other reasons."""
        if s.elem_xpath('//div[@id="nc_1_wrapper"]'):
            s.solve_captcha()
            s.press_login()
            if s.elem_xpath('//*[@id="J_Message"]'):
                s.driver.get('https://login.tabao.com')
                s.tb_login()
            #     # detected as bot , captcha denied
            #     i = 0
            #     while i < 5 and s.elem_xpath('//*[@id="J_Message"]'):
            #         actions = ActionChains(s.driver)
            #         actions = s.delayed_key_input(actions, s.tb_password)
            #         actions.pause(np.random.randint(400, 800) / 1000)
            #         actions.perform()
            #         s.solve_captcha()
            #         ActionChains(s.driver).pause(1)
            #         s.press_login()
            #         i += 1
        #         s.restart_session()
        else:
            s.press_login()

    def press_login(s):
        submit = s.driver.find_element_by_xpath("//*[@id='J_SubmitStatic']")
        actions = ActionChains(s.driver)
        actions.move_to_element_with_offset(submit, 5, 5).pause(0.5).click().perform()
        # s.driver.save_screenshot(
        #     os.path.join(Paths.img_path, 'screen_{}.png'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))))

    @staticmethod
    def prepend_url_schema(url):
        if url is None:
            return url
        elif url[:2] == r"//":
            return "https:" + url
        else:
            return url

    def solve_captcha(s):
        """this works (2018.10.14) but copy pasted from trial code. needs some refactoring
        to fit class structure and references"""
        while True:
            try:
                # 定位滑块元素,如果不存在，则跳出循环
                show = s.driver.find_element_by_xpath("//*[@id='nocaptcha']")
                if not show.is_displayed():
                    break
                source = s.driver.find_element_by_xpath("//*[@id='nc_1_n1z']")
                s.driver.implicitly_wait(3)
                # 定义鼠标拖放动作
                # ActionChains(driver).drag_and_drop_by_offset(source,400,0).perform()
                # driver.save_screenshot('login-screeshot-11.png')
            except:
                pass
            action = ActionChains(s.driver)
            s.driver.implicitly_wait(1)
            action.click_and_hold(source).perform()
            for index in range(10):
                try:
                    action.move_by_offset(4, 0).perform()  # 平行移动鼠标
                    # driver.save_screenshot('login-screeshot-i-'+str(index)+'.png')
                except Exception as e:
                    print(e)
                    break
                if index == 9:
                    action.release()
                    s.driver.implicitly_wait(0.05)
                    # s.driver.save_screenshot(os.path.join(Paths.img_path, 'screen_{}.png'.format(
                    #     datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))))
                else:
                    s.driver.implicitly_wait(0.01)  # 等待停顿时间
                s.driver.implicitly_wait(.5)
                # s.driver.save_screenshot(
                #     os.path.join(Paths.img_path, 'screen_{}.png'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))))
                text = s.driver.find_element_by_xpath("//*[@id='nc_1__scale_text']/span")
                if text.text.startswith(u'验证通过'):
                    print('成功滑动')
                    break
                if text.text.startswith(u'请点击'):
                    print('成功滑动')
                    break
                if text.text.startswith(u'请按住'):
                    continue
                # except Exception as e:
                #     print(e)
                #     driver.find_element_by_xpath("//div[@id='nocaptcha']/div/span/a").click()
        # s.driver.save_screenshot(
        #     os.path.join(Paths.img_path, 'screen_{}.png'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))))

class DataStore:

    def __init__(s, word):
        s.word = word
        s.items = []

    def append_record(s, r):
        s.items.append(r)

    def store_record(s):
        with open(os.path.join(Paths.data, '{}_{}'.format(
                datetime.datetime.today().strftime('%Y%m%d'),
                s.word)), 'wb') as f:
            pickle.dump(s.items, f)

# every product is stored in object that's pickled to disk
    # best: mongo DB
    # next best: some object that's being pickled every 10 items or so
# img url are
    # send to boto to trigger download by AWS
    # or downloaded to server and send to boto for storage (more useful code later on)

if __name__ == '__main__':
    tb = TaobaoSpider()
    tb.start_browser()
    tb.scrape()

if False:
    ll = [el.get_attribute('href') for el in driver.find_elements_by_xpath("//a[@href][@class='content-city']")]
    ll2 = [e.split(r'//')[1] for e in ll]
    ll3 = [e.split(r'.')[0] for e in ll2]
    ll4 = list(set([e for e in ll3 if e != 'g']))
