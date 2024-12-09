from bs4 import BeautifulSoup
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

class NewsScraper:
    def __init__(self, url): 
        
        self.url = url
        self.headlines_dict = {}
        self.sid = SentimentIntensityAnalyzer()

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to retrieve content, Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error during request: {e}")
        return None

    def get_sentiment(self, headline):
        sentiment_scores = self.sid.polarity_scores(headline)
        compound_score = sentiment_scores['compound']
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"

    def parse_headlines(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        index = 1
        for headline in soup.find_all('h3'):
            a_tag = headline.find('a')
            if a_tag:
                headline_text = a_tag.get_text(strip=True)
                headline_link = a_tag['href']
                sentiment = self.get_sentiment(headline_text)
                self.headlines_dict[index] = [headline_text, headline_link, sentiment]
                index += 1

    def get_headlines(self):
        html_content = self.fetch_content()
        if html_content:
            self.parse_headlines(html_content)
            return self.headlines_dict
        return None

# Example usage:
# url = 'https://www.ndtv.com/'
# news_scraper = NewsScraper(url)
# headlines = news_scraper.get_headlines()

# if headlines:
#     for index, data in headlines.items():
#         print(f"Index: {index}, Headline: {data[0]}, Link: {data[1]}, Sentiment: {data[2]}")
