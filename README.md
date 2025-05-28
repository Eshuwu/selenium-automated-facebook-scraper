# selenium-automated-facebook-scraper
This is an automated scraper that uses python integrated with selenium

What it does?

Well recently I saw many people in sales/data analysis,that they have to manually look for information to be analysed

The script solves this issue by providing an architecture,an automated scraping that would specifically work for the website you want to work with , with the help of Selenium. 

In this particular one my main aim was to target the Facebook profiles of clothing brands in a specific location, whose details can be extracted by the script,and can be later used to contact them for various purposes(in my case to contact the for enhancing their profile for a much more interactive view).
The script searches for the given input and then extracts a users details like, name,address,phone number,e-mail and their website.


Workflow:
1.Goes to chrome browser and uses bing search engine to type the initialized command

2.After typing searches and visits every available facebook URl

3.After going on nth URL, it looks for the details by visiting the html attributes like phone number,address,website and name.

4.It then creates a jsonbin (if it does not exit),and then inserts the details in it.

5.Creates a backup CSV file where we can perform certain operations.

6.Saves the data in the bin as soon as it visits 10 URLs.


Features:
1.Selenium was one of the most helpful tool that helped me target specific attributes

2.Since Google is a pro for detecting automation , to avoid captcha verification it seraches through bing

3.Addition of random sleep time for a better disguise of human-like interaction(such as appealing like a human showing as if it is typing in the search bar), to avoid any interference

4.It detects any facebook's login popup and closes it so you dont have to login

5.Many users have created groups for thrifting purposes, it detects them and skips that page for scraping as we have to contact real-time available users

6.Usage of jsonbin for stroring data which can be used by anyone with the APi key

7.Creating a local backup CSV file.

8.shows all the status of the process, such as visitng a site, skipping a group and extracted information along with the percentage of the details grabbed.


Note: Do noy commit any changes, please fork it.
Execution:
Since it works on chrome ,download chrome drive according to you architecture from here: https://developer.chrome.com/docs/chromedriver/downloads
Before running the script, make sure that you have the required modules, if not run the commands in the terminal(mentioned in requirement.txt)
How to run this:
1. download the webdriver and in the 16th line replace it with your driver's location
2. download all the required modules in the project's directory itself
3. make sure to make an account on jsonbin.io and replace it with your key at 19th line
4. In the 24-25th line replace with the path of where you want to store yopur excel file.
5. Youre good to run the script,just make sure during the process none of the CSV files or the json bin is running.





