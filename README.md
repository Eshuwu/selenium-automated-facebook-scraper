# selenium-automated-facebook-scraper
This is an automated scraper that uses python integrated with selenium
What it does?
Well recently I saw many people in sales/data analysis,that they have to manually look for information to be analysed
The script solves this issue by providing an architecture,an automated scraping that would specifically for the website you want to work with , with the help of Selenium. 
In this particular one my main aim was to target clothing brands in a specific location, whose details can be extracted by the script,and can be later used to contact them for various purposes(in my case to contact the for enhancing their profile for a much more interactive view.
The script searches for the given input and then extracts a users details like, name,address,phone number,e-mail and their website.


Workflow:
1.Goes to chrome browser and uses bing search and types the initialized command
2.After typing searches and visits every available facebook URl
3.After going on nth URL, it searches for the details by visiting the html attributes of details like phone number,address,website and name.
4.It then creates a jsonbin (if it doesnt already exits),and then inserts the details in it.
5.Creates a backup CSV file where we can perform certain operations on it
6.Saves the data in the bin as soon as ot visits 10 URLs

Features:
1.Selenium was one of the most helpful tool that helped me target specific attributes
2.Since Google is a pro for detecting automation , to avoid captcha verification it seraches through bing
3.Addition of random sleep time for a better looking human-like interaction(such as appealing like a human is typing in the search bar), to avoid in any interference
4.It detects any facebook's login popup and closes it so you dont have to login
5.Many users have created groups for thrifting purposes, it detects them and skips that page for scraping as we have to contact real-time available users
6.Usage of jsonbin for stroring data which can be used by anyone with the APi key
7.Creating a local backup CSV file.
8.shows all the status of the process, such as visitng a site, skipping a group and extracted information along with the percentage of the details grabbed.




