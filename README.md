# P1sty

<p align="center">
<img src="https://user-images.githubusercontent.com/37407314/89568417-2d109700-d81b-11ea-9f28-07f983bdcb14.PNG" height="250" />
</p>

P1sty is a python Tool that allows you to generate fully coded P1sty spiders 
for any given paste website in less than a second.

P1sty's spiders allows you to monitor a given paste website for occurrence of
 your business name, domain, emails, credentials, Credit cards, etc.

Once the fraudulent information is detected, you will be notified in real time
by e-mail, and a MISP event will be automatically created.

In case of true positive alert, you should inform your Fraud departement also
you can notify your MISP community.



# System architecture

![architecture](https://user-images.githubusercontent.com/37407314/89589782-470fa100-d83e-11ea-8030-ca1d97057eb5.png)


## Installation

~~~
git clone https://github.com/jonathan6661/P1sty.git
cd P1sty
sudo pip install -r requirements.txt
~~~


## Usage

~~~
$ python p1sty.py -h
Usage: p1sty.py [options]

Options:
  -h, --help                            Show this help message and exit
  -n NAME, --name NAME                  Spider name
  -s START, --start START               Archive url
  -m MISP, --misp MISP                  Misp events url
  -k KEY, --key KEY                     Misp key
  -lpx LPX                              Latest pastes XPath
  -rpx RPX                              Raw paste data XPath
  -ux UX                                Username XPath
  -d DOMAIN, --domain DOMAIN            Company domain
  -b BIN, --bin BIN                     Company BIN
  -se SENDER, --sender SENDER           Sender email address
  -p PASSWORD, --password PASSWORD      Sender email password
  -r RECIPIENT, --recipient RECIPIENT   Recipient email

~~~

## Examples

Let's suppose your domain is p1sty.com and your Bank BIN is 123456 and you want to monitor pastebin.com, pastebin.fr, gist.github.com, paste.debian.net,etc for occurance of your domain, urls, emails, credentials and your credit cards.
There is no need to develop for each website a specific crawler from scratch because with p1sty, you can generate a fully coded spider in less than a second based on specific parameters.

Example 1: monitoring pastebin.com (Without email notification)
~~~
$ python p1sty.py -n "pastebin" -s "http://pastebin.com/archive" -m "https://Misp_URL/events" -k "MISP key" -lpx "//tr/td[1]/a/@href" -rpx "//textarea/text()" -ux "//div[@class='username']/a/text()" -d "p1sty.com" -b "123456"

$ scrapy crawl pastebin 
~~~
Example 2: monitoring pastebin.fr (With email notification)

~~~
$ python p1sty.py -n "pastebin_fr" -s "http://pastebin.fr/" -m "https://Misp_URL/events" -k "MISP key" -lpx "//a[contains(@href,'http://pastebin.fr/')]/@href" -rpx "//textarea/text()" -ux "//div/h1/em/text()" -d "p1sty.com" -b "123456" -se "sender email" -p "password" -r "recipient email"

$ scrapy crawl pastebin_fr
~~~

# P1sty spiders to MISP
Besides extracting raw paste data, p1sty spiders extract usernames, Bitcoin addresses, email addresses, cards numbers and add it to MISP event as attributes and enable their correlation.
In this case, we will be able to correlate all of our findings to identify who is the criminal/malicious group behind data exposure.
We all know that most criminals uses single bitcoin address, so when a criminal adds parts of card or credential dumps and then mentions his Bitcoin address, we can identify all usernames used by him in different paste websites, this will allows us to perform tracking and we may be able to identify him ;)

<p align="center">
<img src="https://user-images.githubusercontent.com/37407314/89597019-d625b480-d850-11ea-9dce-d602df7899e7.PNG" height="250" />
</p>

# Are we limited to that ?

Of course not, this project was developed for an article about Fraud prevention :) 

In the following articles, i will extend P1sty to monitor dark web also i will develop intelligente crawlers.

## License

~~~

    Copyright (c) 2020 Abdelkader BEN ALI

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
~~~

