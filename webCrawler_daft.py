import re
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import csv



# for main url
findlink = re.compile(r'<a.*href="(.*?)"')

# for suburl
findPrice = re.compile(r'class="TitleBlock__StyledSpan-sc-1avkvav-4 gDBFnc">€(.*?) per')
findPricePeriod = re.compile(r'class="TitleBlock__StyledSpan-sc-1avkvav-4 gDBFnc">(.*?) </span>')
findCode = re.compile(r'data-testid="address">(.*?)</h1>')
findType = re.compile(r'data-testid="property-type">(.*?)</p>')

findNumBedroom = re.compile(r'Bedroom</span>: <!-- -->(\d*)</li>')
findNumBathroom = re.compile(r'Bathroom</span>: <!-- -->(\d*)</li>')
findFurnished = re.compile(r'Furnished</span>: <!-- -->(.*?)</li>')
findDescription = re.compile(r'<div class="PropertyPage__StandardParagraph-sc-14jmnho-8 kDFIyQ" data-testid="description">(.*?)</div></div>', re.S)

districtCode = ['Dublin 1', 'Dublin 2', 'Dublin 3', 'Dublin 4', 'Dublin 5', 'Dublin 6', 'Dublin 6W',
                'Dublin 7', 'Dublin 8', 'Dublin 9', 'Dublin 10', 'Dublin 11', 'Dublin 12', 'Dublin 13',
                'Dublin 14', 'Dublin 15', 'Dublin 16', 'Dublin17', 'Dublin 18', 'Dublin 20',
                'Dublin 22', 'Dublin 24']
houseType = ['Apartment', 'House', 'Studio']
transportsVocabulary = [" bus ", " Bus ", " BUS ", " buses ", " Buses ", " Luas ", " luas ", " LUAS ",
                        " transport ", " transports ", " Transport ", " Transports ", " bus.", " buses.",
                        " Luas.", " luas.", " LUAS.", " transport.", " transports."]
shopVocabulary = [" shop ", " shops ", " shopping ", " store ", " stores ", " Shop ", " Store ", " Stores ", " Shopping ",
                  " shop.", " shops.", " shopping.", " store.", " stores."]
parkingVocabulary = ["Parking", "parking"]
internetVocabulary = ["Internet", "wifi", "Wifi", "WIFI"]
extraSpaceVocabulary = ["Garden", "Patio", "Balcony"]

number_data = 0
number_complete_data = 0
number_incomplete_data = 0

def main():

    savepath = "daft.csv"
    headRow = ['Price', 'Dublin 1', 'Dublin 2', 'Dublin 3', 'Dublin 4', 'Dublin 5', 'Dublin 6', 'Dublin 6W',
               'Dublin 7', 'Dublin 8', 'Dublin 9', 'Dublin 10', 'Dublin 11', 'Dublin 12', 'Dublin 13',
               'Dublin 14', 'Dublin 15', 'Dublin 16', 'Dublin17', 'Dublin 18', 'Dublin 20',
               'Dublin 22', 'Dublin 24', 'Apartment', 'House', 'Studio', 'Bedroom', 'Bathroom', 'Furnished',
               'Transports', 'Shops', 'Parking', 'Internet', 'ExtraSpace']
    f = open(savepath, 'a', encoding='utf-8-sig', newline="")
    csv_writer = csv.writer(f)
    csv_writer.writerow(headRow)
    f.close()

    baseurl = "https://www.daft.ie/property-for-rent/dublin-city?pageSize=20&from="
    getData(baseurl, savepath)


def getData(baseurl, savepath):

    for i in range(0, 10):
        time.sleep(1)

        url = baseurl + str(i*20)
        # url = baseurl
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")

        suburl = []
        for item in soup.find_all('li', class_="SubUnits__Item-sc-150tj2u-2 iKhaLF"):
            # print(item)
            item = str(item)
            link = re.findall(findlink, item)
            prefix = "https://www.daft.ie/"
            link = prefix + link[0]
            suburl.append(link)

        data = getData_suburl(suburl)
        saveData(data, savepath)


def getData_suburl(suburl):

    global number_data, number_complete_data, number_incomplete_data
    datalist = []

    for i in suburl:
        time.sleep(0.1)

        data = []
        url = i
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")
        code = -1

        counter = 0
        # print("================================")

        for item in soup.find_all('div', class_="PropertyPage__MainFlexWrapper-sc-14jmnho-0 cqxrhg"):
            item = str(item)

            price_str = re.findall(findPrice, item)
            price = int(price_str[0].replace(',', ''))

            price_period = re.findall(findPricePeriod, item)
            if 'week' in price_period[0]:
                price *= 4.3
                price = int(price)
            # print("price per month: ", price)
            if price > 0:
                counter += 1
            data.append(price)

            code_text = re.findall(findCode, item)
            for i, j in enumerate(districtCode):
                if j in code_text[0]:
                    code = i
            # print("district code: ", code)
            if code > -1:
                counter += 1
            for i in range(len(districtCode)):
                if code != i:
                    data.append(0)
                else:
                    data.append(1)

            type = 0
            type_str = re.findall(findType, item)
            for i, j in enumerate(houseType):
                if j in type_str[0]:
                    type = i
            # print("house type: ", type)
            if type >= 0 and type <= 2:
                counter += 1
            for i in range(len(houseType)):
                if type != i:
                    data.append(0)
                else:
                    data.append(1)

        for item in soup.find_all('div', class_="PropertyPage__MainFlexWrapper-sc-14jmnho-0 cqxrhg"):

            item = str(item)

            numBedroom_list = re.findall(findNumBedroom, item)
            numBedroom = 0
            for i in numBedroom_list:
                numBedroom += int(i)
            # print("number of bedroom: ", numBedroom)
            if numBedroom >= 2 and data[0] <= 1200:
                numBedroom = 1
            if numBedroom >= 0:
                counter += 1
            data.append(numBedroom)

            numBathroom_list = re.findall(findNumBathroom, item)
            numBathroom = 0
            for i in numBathroom_list:
                numBathroom += int(i)
            # print("number of bathroom: ", numBathroom)
            if numBathroom >= 2 and data[0] <= 1200:
                numBathroom = 1
            if numBathroom >= 0:
                counter += 1
            data.append(numBathroom)

            furnished_list = re.findall(findFurnished, item)
            furnished = 0
            if furnished_list[0] == "Yes" or furnished_list[0] == "yes" or \
                    furnished_list[0] == "Optional" or furnished_list[0] == "optional":
                furnished = 1
            if furnished_list[0] == "No" or furnished_list[0] == "no":
                furnished = 0
            # print("whether furnished: ", furnished)
            if furnished >= 0:
                counter += 1
            data.append(furnished)

            description = re.findall(findDescription, item)
            transport = 0
            for i in transportsVocabulary:
                if i in description[0]:
                    transport = 1
                    break
            # print("whether near to transports: ", transport)
            if transport >= 0:
                counter += 1
            data.append(transport)

            shop = 0
            for i in shopVocabulary:
                if i in description[0]:
                    shop = 1
                    break
            # print("whether near to shops", shop)
            if shop >= 0:
                counter += 1
            data.append(shop)

        for item in soup.find_all('ul', class_="PropertyDetailsList__PropertyDetailsListContainer-sc-1cjwtjz-0 bnzQrB"):
            item = str(item)
            parking = 0
            for i in parkingVocabulary:
                if i in item:
                    parking = 1
                    break
            # print("whether have parking: ", parking)
            if parking >= 0:
                counter += 1
            data.append(parking)

            internet = 0
            for i in internetVocabulary:
                if i in item:
                    internet = 1
                    break
            # print("whether have the Internet: ", internet)
            if internet >= 0:
                counter += 1
            data.append(internet)

            extraSpace = 0
            for i in extraSpaceVocabulary:
                if i in item:
                    extraSpace = 1
                    break
            # print("whether have extra space: ", extraSpace)
            if extraSpace >= 0:
                counter += 1
            data.append(extraSpace)

        if counter == 11:
            datalist.append(data)
            number_complete_data += 1
        else:
            number_incomplete_data += 1
        number_data += 1

        print("Number of data: %4d, Number of complete data: %4d, Number of incomplete data: %4d"
              %(number_data, number_complete_data, number_incomplete_data))



    return datalist


def saveData(data, savepath):

    f = open(savepath, 'a', encoding='utf-8-sig', newline="")
    csv_writer = csv.writer(f)

    for i in data:
        csv_writer.writerow(i)

    f.close()


def askURL(url):
    # head = {
    #     "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome / 93.0.4577.82 Safari / 537.36"
    # }
    head = {
        "User-Agent": UserAgent(verify_ssl=False).random,
        # "Cookie": '_ga=GA1.2.1066675121.1634979729; daftCC="{\\"version\\":1,\\"createDate\\":1634979729322,\\"lastUpdated\\":1634979729322,\\"expires\\":1650704529322,\\"strictlyNecessary\\":true,\\"analytics\\":true,\\"functional\\":true,\\"advertising\\":true}"; NPS_215a2284_last_seen=1634979729890; _hjid=1fcbb432-4753-4e43-aeb6-f6f73361115d; _gid=GA1.2.1234493289.1635807597; daftBB=true; __gads=ID=45752a3b4446dcdf:T=1634979729:S=ALNI_MYw61Hh-Y-GKItHEtmuxK_jU2v9nA'
    }

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html

if __name__ == "__main__":
    main()