from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import time
from selenium.common.exceptions import TimeoutException,StaleElementReferenceException
import pymongo

client = pymongo.MongoClient(host='localhost')
db=client['Product']

KEYWORD = '美食'

browser = webdriver.Chrome()
wait = WebDriverWait(browser,20)

def save_to_mongo(info):
    if db[KEYWORD].insert(info):
        print('保存成功',info)
    else:
        print('保存失败',info)

# def login(name, passwd):
#     login_switch = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_LoginBox > div.hd > div.login-switch')))
#     login_switch.click()
#     name1 = browser.find_element_by_css_selector('#TPL_username_1')
#     passwd1 = browser.find_element_by_css_selector('#TPL_password_1')
#     button = browser.find_element_by_css_selector('#J_SubmitStatic')
#     name1.clear()
#     name1.send_keys(name)
#     time.sleep(1)
#     passwd1.clear()
#     passwd1.send_keys(passwd)
#     time.sleep(1)
#
#     element_id = browser.find_element_by_css_selector('#nc_1_n1z')
#     element_id2 = browser.find_element_by_css_selector('#nc_1__scale_text > span')
#     actions = ActionChains(browser)
#     actions.drag_and_drop(element_id)
#     actions.perform()

    # button.click()


def search():
    url = 'https://www.jd.com/'
    browser.get(url)#输入网址
    inputs = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#key')))#找到搜索框
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#search > div > div.form > button')))
    inputs.clear()
    inputs.send_keys(KEYWORD)#输入搜索关键字
    button.click()#点击
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_goodsList > span.clr')))
    #获得页码信息
    page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p-skip > em > b')))
    return int(page.text)

#提取信息
def get_info(html):
    soup = BeautifulSoup(html,'html.parser')#将字符串转化为BeautifulSoup
    results = soup.select('.gl-warp .gl-item')#定位到包含商品信息的位置
    for result in results:
        product={
            'url':result.select('.p-img a')[0].attrs['href'],#商品链接
            'price':result.select('.p-price i')[0].get_text(),#价格
            'name':result.select('.p-name em')[0].get_text().strip(),#商品描述
            'commit':result.select('.p-commit strong')[0].get_text(),#评价
            'shop':result.select('.p-shop')[0].get_text().strip()#店铺
        }
        save_to_mongo(product)#保存到数据库


def get_next_page(pn):
    #如果是第一页，不需要进行翻页
    if pn==1:
        get_info(browser.page_source)#解析提取商品信息
    else:
        try:
            #定位输入页码的文本框
            inputs = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > input')))
            inputs.clear()#清空
            inputs.send_keys(pn)#输入页码
            #定位确定按钮
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > a.btn')))
            button.click()#点击
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_goodsList > span.clr')))
            #判断是否翻页成功，主要判断当前高亮的页数，是否对应想要翻的页码
            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.p-num a.curr'),str(pn)))
            get_info(browser.page_source)#提取信息
        except TimeoutException:
            get_next_page(pn)
        except StaleElementReferenceException:
            get_next_page(pn)


def main():
    page = search()#搜索商品，并返回对应商品的页数
    for i in range(1,page+1):#翻页
        get_next_page(i)

if __name__=='__main__':
    main()