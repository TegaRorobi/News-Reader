import requests
import pyttsx3
import bs4

from threading import Thread

class NewsReader:

	home = "https://www.bbc.com"
	target = "https://www.bbc.com/news/technology"

	def __init__(self):
		self.engine = pyttsx3.init()
		self.news = []
		self.configure_speaking_engine()
		td = Thread(target=self.extract_news, args=())
		td.start()
		self.introduce()
		td.join()


	def configure_speaking_engine(self) -> None:
		# a female voice and a slower rate.
		self.engine.setProperty('voice', self.engine.getProperty('voices')[1].id)
		self.engine.setProperty('rate', self.engine.getProperty('rate')-50)


	def introduce(self) -> None:
		with open('introduction.txt', 'r') as f:
			self.engine.say(f.read())
			self.engine.runAndWait()


	def extract_news(self) -> None:
		page_content = requests.get(self.target)
		scraper = bs4.BeautifulSoup(page_content.text, 'lxml')
		a_tag = scraper.find('div', class_="gs-c-promo-body gs-u-mt@xxs gs-u-mt@m gs-c-promo-body--primary gs-u-mt@xs gs-u-mt@s gs-u-mt@m gs-u-mt@xl gel-1/3@m gel-1/2@xl").find('a')
		top_story = a_tag.h3.text
		top_story_url = a_tag.get('href')
		top_story_details = self.get_details(top_story_url)
		self.news.append((top_story, top_story_details))

		container = scraper.find('div', class_='gel-layout__item gel-1/1@s gel-1/2@m gel-1/2@l gel-3/5@xl gel-3/4@xxl')
		other_headlines = container.find_all('div', class_="gs-c-promo-body gs-u-mt@xxs gs-u-mt@m gs-c-promo-body--flex gs-u-mt@xs gs-u-mt0@xs gs-u-mt--@s gs-u-mt--@m gel-1/2@xs gel-1/1@s")
		for tag in other_headlines:
			headline = tag.h3.text 
			self.news.append((headline,))


	def get_details(self, headline_url:str):
		page_content = requests.get(self.home + headline_url)
		scraper = bs4.BeautifulSoup(page_content.text, 'lxml')

		main = scraper.find('main', id='main-content')
		details = []
		for div in main.find_all('div', class_='ssrcss-11r1m41-RichTextComponentWrapper ep2nwvo0', attrs={'data-component':'text-block'}):
			details.append(div.p.text)
		return details


	def read(self) -> None:
		"""
		The `news` instance attribute contains the extracted text as tuples of strings.
		The first tuple is the top story and contains the headline,
		and a list of paragraphs for the details.
		All other tuples have only headlines and no details.
		"""
		self.engine.say("The top story on technology reads out as follows: ")
		self.engine.say(self.news[0][0])

		self.engine.say("And here are the other headlines")
		for headline in self.news[1:]:
			self.engine.say(headline[0])

		self.engine.say("Now here's more information on the top story...")
		for paragraph in self.news[0][1]:
			self.engine.say(paragraph)


		self.engine.say("And there you have it!, thanks for listening, and be sure to  have a nice day.")
		self.engine.runAndWait()


if __name__ == "__main__":
	reader = NewsReader()
	reader.read()