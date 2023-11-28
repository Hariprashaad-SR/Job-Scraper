'''
This program scraps only the mentioned webpage, 
and if you want to scrap other website,
modify the code as needed.

For help, see the tutorial attached!
'''
# Importing Libraries

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests


# User - defined functions


def parse(url):
    try:
        page = requests.get(url)

        # Check if the request was successful(status code 200)
        if page.status_code == 200:
            print("Request successful")

            # Storing the parsed contents
            response = BeautifulSoup(page.text,"html.parser")
        else:
            print(f"Request failed with status code {page.status_code}")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    
    else:
        return response
    

def clean_text(text):
    # This function removes all the escape characters - ['\n' ,'\t' , '\r']
    cleaned_text = text.replace('\t','').replace('\n','').replace('\r','').strip()
    
    # This removes the blank spaces
    cleaned_text = ' '.join(cleaned_text.split()) 
    
    return cleaned_text



def scrap_title(response):
    #This function is used to scrap the job_titles from each webpage
    
    # find_all() is used to find all the occurance of the search element - <h4> tags
    all_h4 = response.find_all('h4')
    
    # find() is used to find the first occurance of the search element - <a> tags
    all_a_tags = [h4.find('a',style = 'color: #02b44a;') for h4 in all_h4]
    
    # .text is used to strip of the contents of a particular tag - <a> tag
    job_titles = [a.text for a in all_a_tags if a != None]
    
    # Clean the scraped job titles using the clean_text function
    job_titles = [clean_text(title) for title in job_titles]
    
    return job_titles



def get_href(response):
    # This function is used to get the links to each job in a web-page
    
    # Retrieving all the <a> tags with a link to each jobs
    all_h4s = response.find_all("h4")
    all_a_tag = [h4.find('a',style = 'color: #02b44a;') for h4 in all_h4s]
    
    # .attrs[] is used to retrieve the mentioned tag out from a HTML source
    href = [a.attrs['href'] for a in all_a_tag if a != None]
    
    return href



def scrap_info(response):
    gender = age = opening = exp = city = landmark = field = desc = sal = qual = " "
    
    # Get the contents from the <div> tags
    all_divs = response.find_all('div',class_ = 'location')
    
    conts = [div.text for div in all_divs]
    # Clean each retrieved data using the clean_text() function
    
    conts = [clean_text(cont) for cont in conts]
    # Store the needed contents in a list
    cleaned_conts = [] 

    for cont in conts:
        # temps store the splitted elements
        temps = cont.split('|')
        
        temps = [temp.strip() for temp in temps]
        cleaned_conts.append(temps) 
        
    field, desc = map(str, cleaned_conts[0])   
    sal, qual, city = map(str,cleaned_conts[1])
    landmark = str(cleaned_conts[2][0])
    
    for cont in cleaned_conts[3]:
        if cont.startswith('Gender :'):
            gender = cont[9:]
        if cont.startswith('Age Limit -'):
            age = cont[12:]
        if cont.startswith('Openings -'):
            opening = cont[11:]
        if cont.startswith('Experience - '):
            exp = cont[13:]
    
    return (gender,age,opening,exp,city,landmark,desc,sal,qual,field)



def ret_info(href):
    # This function gets the urls from the get_href() function and retreives the data
    
    # The info_list is used to store all the acquired data
    info_list = []
    for url in href:
        # Request and parse each url and append the information to the info_list
        res_1 = parse(url)
        info_list.append(scrap_info(res_1))
        
    # Convert the list to a np.array() and get the transpose to group each attributes
    info_list = (np.array(info_list)).T
    return info_list



def scrap_add_data(response):
    # This function is to get all the additional information from the main webpage
    post_date = [] 
    last_date = []
    roles = []
    company_name = []
    
    # Retrieving other information
    all_div = response.find_all("div",class_ = 'companyName')
    all_datas = [div.text for div in all_div]
    all_datas = [clean_text(data) for data in all_datas]

    # Retrieving the post_date and the last_date to apply
    for i in range(1,len(all_datas),3):
        post, last = map(str,all_datas[i].split('|'))
        post_date.append(post)
        last_date.append(last)
    
    # Removing the text from the dates
    post_date = [post.split(':')[1] for post in post_date]
    last_date = [last.split(':')[1] for last in last_date]

    # Retrieving the company name
    for i in range(0,len(all_datas),3):    
        # temp variable is used to store the unwanted data when we split the lists
        temp, name = map(str,all_datas[i].split('|'))
        company_name.append(name)
        
    # Retrieving the roles needed for each job
    for i in range(2,len(all_datas),3):
        role = all_datas[i]
        roles.append(role)
    
    return (post_date,last_date,roles,company_name)



def append_data(info):
    # This function is used to append the data scraped from the each child webpage into the respective variable
    [gender.append(i) for i in info[0]]
    [age.append(i) for i in info[1]]
    [opening.append(i) for i in info[2]]
    [exp.append(i) for i in info[3]]
    [city.append(i) for i in info[4]]    
    [landmark.append(i) for i in info[5]]    
    [desc.append(i) for i in info[6]]
    [sal.append(i) for i in info[7]]
    [qual.append(i) for i in info[8]]
    [field.append(i) for i in info[9]]



def append_add_data(info):
    # This function is used to append the data scraped to their respective variables
    [post_date.append(i) for i in info[0]]
    [last_date.append(i) for i in info[1]]
    [roles.append(i) for i in info[2]]
    [company_name.append(i) for i in info[3]]



def scrap_webpage(url):
    # Request and Parse the URL
    response = parse(url)
    
    # Get the child URLs for each job using the get_href() function
    hrefs = get_href(response)
    
    # Retrieve all the information from each urls using the ret_info() and scrap_info() function
    all_info = ret_info(hrefs)
    # append all the data using the append_data() function
    append_data(all_info)
    
    # Retrieve other additional information from the main webpages
    all_add_info = scrap_add_data(response)
    # append it using the append_add_data() function
    append_add_data(all_add_info)
    
    [job_title.append(i) for i in scrap_title(response)]


# Main function ... 


# base_url
base_url = "https://www.tnprivatejobs.tn.gov.in/Home/jobs"

# Create a list to store all the urls
urls = [] 

# Appending the base url to the list
urls.append(base_url)

for i in range(10,281,10):
    # Appending all urls to the list
    urls.append(f"{base_url}/{i}")


# Initialise all the list to store the required data(s)
job_title = []
gender = []
age = []
opening = []
exp = []
city = []
landmark = []
field = []
desc = []
sal = []
qual = []
post_date = [] 
last_date = []
roles = []
company_name = []


# For Retrieving all the jobs from the urls appended in the `urls` list
for url in urls:
    scrap_webpage(url)

# Converting the acquired data into a dictionary
dic = {
    "Job Title" : job_title,
    "Description" : desc,
    "Field" : field,
    "Company Name" : company_name,
    "City" : city,
    "Landmark" : landmark,
    "Post Date" : post_date, 
    "Last Date" : last_date,
    "Salary" : sal,
    "Gender" : gender,
    "Age" : age,
    "Experience" : exp,
    "Qualification" : qual,
    "Roles" : roles,
    "Openings" : opening
}



# Creating a table using the DataFrame function of the pandas library for easy viewing
df = pd.DataFrame(dic)
print(df.head(5))


# Store the contents of the DataFrame df to a file
df.to_csv('job_postings.csv',index = False)

print('Sayonara!!!')