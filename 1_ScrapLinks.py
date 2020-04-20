from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlretrieve, urlopen as uReq  # Web client
from time import time
import os
import shutil
from multiprocessing import Process, Value, Pool

URL = "https://www.myauto.ge/en/s/00/0/00/00/00/00/00/cars?stype=0&currency_id=3&det_search=0&ord=7&category_id=m0&keyword=&page={}"


def processFunction(data):
    startInd, endInd, index, URL = data
    
    fileName = 'Links_{}.txt'.format(index+1)
    f = open(fileName, 'w')

    start = time()
    for pageNum in range(startInd, endInd):
        elapsed = int(time()-start)
        if elapsed == 0:
            Estimated = 0
            mean = 0
        else:
            mean = (pageNum-startInd)/elapsed
            Estimated = (endInd - pageNum)//mean
            
        print('Process {}  ---  Elapsed {}s  --- Estimated Time Left {} sec ---  {}/{}'.format(index, elapsed,Estimated, pageNum-startInd, endInd- startInd))
        page_url = URL.format(pageNum)
        uClient = uReq(page_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()

        resultArray = page_soup.findAll("h4", {"itemprop": "name"})
        resultArray = [x.a['href'] for x in resultArray]
        resultString = '\n'.join(resultArray)
        f.write('{}\n'.format(resultString))



def findMaxPage():
    page_url = URL.format('1')
    uClient = uReq(page_url)
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()

    lastPageLinkClass = page_soup.findAll(
        "li", {"class": "pagination-li last-page"})
    lastPageLink = lastPageLinkClass[0].a['href']
    pageNum = lastPageLink.split('=')[-1]
    return int(pageNum)


if __name__ == "__main__":
    folder = 'Links'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    os.chdir(folder)

    MaxPage = findMaxPage()


    totalProcesses = 1
    processChunkSize = MaxPage // totalProcesses
    processPageIndices = []
    for ind in range(totalProcesses):
        curData = [ind*processChunkSize,
                   (ind+1)*processChunkSize, ind, URL]
        processPageIndices += [curData]

    p = Pool(totalProcesses)
    records = p.map(processFunction, processPageIndices)


    fileName = 'AllLinks.txt'
    mainFile = open(fileName, 'w')
    for i in range(totalProcesses):
        fileName = 'Links_{}.txt'.format(i+1)
        f = open(fileName, 'r')
        mainFile.write(f.read())