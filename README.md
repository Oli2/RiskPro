# RiskPro

Step-by-step instructions:


1. Create conda environment with python 3.11 using the requirements.txt file. Switch to the newly created environment.

2. Store the sec api key in SEC_API environment variable before running the scripts.

2. sec_forms_downloader.py downloads SEC 5 latest S-1 forms issued over the last yearand saves them to the sec_forms directory as json objects.


3. sec_forms_downloader.py takes the url of S-1 form (available in the json object) as an argument and processes the form and saves the text of the form to a processed_document.txt in the main dicrectory. The name of the file can be defined with the optional output argument.