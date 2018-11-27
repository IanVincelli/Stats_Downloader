import requests
import lxml.html as lh
import pandas as pd
import numpy as np
import os
import pickle
#create a directory
directory = os.path.dirname("C/HockeyStats")
#create a list of urls from espn which allows me to make a list of the top 80 offenseman and defenseman and the top 40 goalies
f_urls = ['http://www.espn.com/nhl/statistics/player/_/stat/points/sort/points/position/forwards', 'http://www.espn.com/nhl/statistics/player/_/stat/points/sort/points/position/forwards/count/41']
d_urls = ['http://www.espn.com/nhl/statistics/player/_/stat/points/sort/points/position/defensemen' ,'http://www.espn.com/nhl/statistics/player/_/stat/points/sort/points/position/defensemen/count/41']
g_url = 'http://www.espn.com/nhl/statistics/player/_/stat/goaltending/sort/savePct/year/2019/seasontype/2'
test_page = requests.get('http://www.espn.com/nhl/statistics/player/_/stat/points/sort/points/position/forwards/yy')
print(test_page)
#this function grabs the data from the website tables
def get_player_list(url):

    #create a handle page to handle the contents of the website
    page = requests.get(url)
    #store the contents of the page under doc
    doc = lh.fromstring(page.content)
    #parse the data that is stored between <tr>..</tr> of html
    tr_elements = doc.xpath('//tr')
    
    #create empty list
    col = []
    i=0

    #print([len(T) for T in tr_elements[:25]])
    
    #For each row, store each first element (header) and an empty list
    for t in tr_elements[1]:
        i+=1
        name=t.text_content()
        #print('%d:"%s"'%(i,name))
        col.append((name,[]))

#next is a variable that tells us if we are at a new table 
    next = 0
    for j in range(2, len(tr_elements)):
        if next == 1:
            next = 0
            continue
        #T is the j'th row
        T = tr_elements[j]
        if len(T)!=17:
            next = 1
            continue
       
        #i is the index of the column
        i=0

        #iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()

            #check if row is empty
            if i>0:
                #convert any numerical value to integers
                try:
                    data = int(data)
                except:
                    pass

            #print(data)
            #append the data to the empty list of the i'th column
            col[i][1].append(data)
            #increment i for the next column
            i+=1
    return col

#this function creates lists of the player names from the espn top player data
def get_player_urls(urls,_list):
    #creates empty list
    tr_elements = []
    for i in range(0,len(urls)):
        #create a handle page to handle the contents of the website
        page = requests.get(urls[i])

        #store the contents of the page under doc
        doc = lh.fromstring(page.content)

        #parse the data that is stored as hyperlinks 
        tr_elem = doc.xpath('//a/@href')
        
        #convert everything into strings for searching
        tr_elem = [str(i) for i in tr_elem]
        #if the main list is empty then make it equal to the elemts from the first page
        if len(tr_elements) == 0:
            tr_elements = tr_elem
        #if the main list is not empty then extend it using the elemtns from the subsequent pages
        else:
            tr_elements.extend(tr_elem)
    #create empty list for the player urls taken from the top player web pages
    p_urls = []

    #this for loop converts the players first and last names to a similar format as used in the sites hyperlinks for each player
    for i in range(0,len(_list)):
        #parse the list of names by the space in first and last name
        first, last = _list[i].split(" ",1)
        #the split and adding of the first or last names is for names with a period or a comma in them, like T.J. Oshie
        #this converts the names to the formats used in the hyperlinks
        if any('.' in s for s in first):
            f = first.split(".")
            first = f[0]+f[1]
        if any("'" in s for s in last):
            l = last.split("'")
            last = l[0] + l[1]
        #this part searches though all the links on the webpage and checks them against the list of player names and saves their individual stas urls 
        p_url = [s for s in tr_elements if first.lower()+'-'+last.lower() in s]

        if len(p_url) != 0:
            p_urls.append(p_url)

    #we now need to fix the urls to contain "gamelog" within the url to access the gamelog page
    for i in range(0,len(p_urls)):
        placeholder = p_urls[i][0].split("_")
        p_urls[i][0] = placeholder[0] + "gamelog/_" + placeholder[1]

    return p_urls

#this function uses the list of player urls to get their per game history for each player for x number of years
def get_player_gamelog(url):
    #add the years to the url so that we can search through all active years easily to get all past performance
    url_ = url.split("/")
    url_2 = ""
    urls = []

    for i in range(0,len(url_)-1):
        url_2 = url_2 + str(url_[i])+'/'

    for i in range(0,5):
        urls.extend([url_2 + "year/" + str(2019 - i) + "/" + url_[len(url_)-1]])
    tr_elements = []
    for i in range(0,len(urls)):
        #create a handle page to handle the contents of the website
        page = requests.get(urls[i])
        #store the contents of the page under doc
        doc = lh.fromstring(page.content)
        #parse the data that is stored between <tr>..</tr> of html
        tr_elem = doc.xpath('//tr')
                
        #convert everything into strings for searching
        #tr_elem = [str(i) for i in tr_elem]
        #if the main list is empty then make it equal to the elemts from the first page
        if len(tr_elements) == 0:
            tr_elements = tr_elem
        #if the main list is not empty then extend it using the elemtns from the subsequent pages
        else:
            tr_elements.extend(tr_elem)

    
    #print([len(T) for T in tr_elements[:70]])
    labels = []
    col =[]
    i=0
    #For each row, store each first element (header) and an empty list
    for t in tr_elements[4]:
        i+=1
        name=t.text_content()
        labels.append(name)
        #print('%d:"%s"'%(i,name))
        col.append((name,[]))

    #next is a variable that tells us if we are at a new table 
    next = 0
    for j in range(5, len(tr_elements)):
        if next == 1:
            next = 0
            continue
        #T is the j'th row
        T = tr_elements[j]
        if len(T)!=17:
            next = 1
            continue
        #i is the index of the column
        i=0

        #iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()

            #check if row is empty
            if i>0:
                #convert any numerical value to integers
                try:
                    data = int(data)
                except:
                    pass

            # check to make sure we arent adding a set of column labels
            if str(data) not in labels:              
                #append the data to the empty list of the i'th column
                col[i][1].append(data)
                #increment i for the next column
                i+=1
    return col, labels

#this functions creates a list from the top plyer web pages
def create_list(urls):
    _list = []
    for i in range(0,len(urls)):
        data = get_player_list(urls[i])   
        if len(_list) == 0:
            _list = data[:][1][1]
        else:
            _list.extend(data[:][1][1])
    return _list
#this list converts the player names to strings and seperates out the postion from the player
def convert_to_str(_list):
    for i in range(0,len(_list)):
        _list[i] = str(_list[i])
        _list[i],_pos = _list[i].split(",",1)
    return _list, _pos

#these use the approptriate functions to create the lists of top forwards and defenseman names
f_list,f_pos = convert_to_str(create_list(f_urls))
d_list,d_pos = convert_to_str(create_list(d_urls))

#these use the forwards and defenseman lists to create the lists of top player urls 
f_urls = get_player_urls(f_urls,f_list)
d_urls = get_player_urls(d_urls,d_list)

#create a data array of size (# of players) x (# of games) x (# of stats)  

def create_dataframes(_urls,_list):
    _frames = {}
    for i in range(0,len(_list)):
        stat, labels = get_player_gamelog(_urls[i][0])
        for j in range(0,len(stat)):
            if j==0:
                _data = pd.DataFrame({labels[j]: stat[j][1]}) 
            else:
                _data[labels[j]] = stat[j][1]

        _frames[_list[i]] = _data
    return _frames
        
def save_obj(obj, name ):
    os.makedirs(os.path.dirname('C:/HockeyStats/'+ name + '.pkl'), exist_ok=True)
    with open('C:/HockeyStats/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    return
f_frames = create_dataframes(f_urls,f_list)
d_frames = create_dataframes(d_urls,d_list)

save_obj(f_frames, 'forward_stats')
save_obj(d_frames, 'defense_stats')