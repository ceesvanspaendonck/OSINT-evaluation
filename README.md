# OSINT-evaluation
Trust in OSINT [provisionary title]  
University of Amsterdam  
12425001  
MA Thesis (New Media and Digital Culture)
June 2024  
Cees van Spaendonck  

This tool allows researchers to automatically search for and scrape X/Twitter threads hosted on Threadreaderapp.com that in turn are sent to OpenAI's GPT for evaluation based on custom instructions. In the context of this thesis, this is done with the goal of evaluating the trustworthiness of OSINT investigations - but this tool can be used with other purposes of social media analysis as well based on the custom instructions (e.g. sentiment analysis, event tracking, misinformation detection). 

Please note that this tool is still being developed. No guarantees can be made regarding its success or safety.  
For questions or bugs or anything else, please send an email to cees.vanspaendonck ***[at]*** student.uva.nl

The tool makes use of the following procedures:
- Run main script with username or Threadreader URL as input *(detailed below)*  
- Search for threads of this user on Threadreader in Programmable Google Search Engine  
- Scrape and save thread URLs  
- Extract posts from threads  
- Evaluate posts per thread  
- Dump result

*Schematic overview of main processes:*
![tool_process_v2](https://github.com/ceesvanspaendonck/OSINT-evaluation/assets/10400578/a8702c72-d4bf-4962-9e48-56d97d8535e7)

Note: the daily limit of search queries on a Programmable Search Engine is fairly limited. Therefore, users that produce no results are now added to a blacklist file (created in local_data) in order to avoid multiple attempts to search for users that produce no results. This approach is still under consideration and might change in the future.  
## Prerequisites
### Requirements
Make sure the necessary packages are present by running:
```
  pip install -r requirements.txt
```
In the project directory, a folder needs to be created called 'secrets'  
In this folder, two files need to be made:  
  - keys.json
  - instructions.txt

The keys.json file should be constructed as following:
```
{  
    "google_cx": "",  
    "google_api_key": "",  
    "open_ai_key": ""  
}
```
The instructions.txt file should contain the instructions sent to GPT. These instructions *must* mention that the results should be presented in a .json format, due to the type of call that is made and to ensure a computer-readable format of the result. This can (for example) be done by including the following in your instructions.txt file:
```
You will output the final result in a JSON object containing the following information:
{
  "result": int // Number indicating something.
}
```
### Custom Google search engine
  - A [custom Google search engine](https://programmablesearchengine.google.com/controlpanel/all) has to be made
  - First, press the blue button to add a new custom search engine
  - Its name is not important. In the What to search? field, enter the following URLs:
     * www.threadreaderapp.com/*  
     * www.threadreaderapp.com/thread/*
  - Save the custom search engine
  - Next, open the details your search engine and copy the Search Engine ID
  - This ID should be saved in the keys.json file as the value of google_cx
  - An API key is also required. To create one, first a [Google Cloud project](https://console.cloud.google.com/apis/) must be created
  - Select Credentials in the left column, create new credentials, and create a new API key
  - This API key should be saved in the keys.json file as the value of google_api_key
  - The API must also be enabled. Select Enabled APIs and services on the left and then the blue +Enable APIs and Servces button
  - Search for custom search api and press enable.
### Open AI Key
  - An OpenAI account (with some balance) is also required
  - An [API key must be created](https://platform.openai.com/settings/profile?tab=api-keys)
  - This API key should be saved as the value of "open_ai_key" in the keys.json file

## Usage:
The main file (*evaluate.py*) is located in the \src\ folder, and has a positional argument of a username or a Threadreader URL as input. The other flags are optional and detailed below.
```
  py \src\evaluate.py [username or threadreader URL] [--force_scrape=] [--skip_scrape=] [--skip_evaluation=]
```
It is also possible to evaluate multiple items at once, seperated by a comma. Usernames and individual threadreader URLs can be mixed. For example:  
```
  py \src\evaluate.py bellingcat,tracelabs,https://threadreaderapp.com/thread/1649032534741663745
```
Optionally, some parts of the process in the tool can be forced or skipped based on the above mentioned optional flags.  
- Scraping can be forced to try and add results previously not found, even if list of threads (and posts) is already present. This can be done with the --force_scrape flag:
```
  py \src\evaluate.py [bellingcat] --force_scrape=True
```
- Scraping can also be skipped, which causes the tool to directly evaluate threads already present in the local_data folder, if for example only the evaluation instructions have to be tested. This can be done with the --skip_scrape flag:
```
  py \src\evaluate.py [bellingcat] --skip_scrape=True
```
- Evaluation can also be skipped, which causes the tool to only search for new threads in order to reduce the runtime. This can be done with the --skip_evaluation flag:
```
  py \src\evaluate.py [bellingcat] --skip_evaluation=True
```
