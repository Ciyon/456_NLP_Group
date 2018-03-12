from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy

def getTopTrends(name, oauth):
    auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    api = tweepy.API(auth)
    ID = 0
    for trend in api.trends_available():
        if (trend['name'] == name):
            ID = trend['woeid']
    trends = api.trends_place(ID)
    trendNames = [trend['name'] for trend in trends[0]['trends']]
    return trendNames

def pre_process_words(tweet_words):
    for item in list(tweet_words):
        if item.count == 0:
            tweet_words.remove(item)

        for word in list(item):
            if word.startswith("http"):
                item.remove(word)

        if item[0] == "RT":
            item.remove("RT")

        if item[0].startswith("@"):
            item.remove(item[0])

        if item.count == 0:
            tweet_words.remove(item)

def get_final_tweet_sents(num_of_tweets, trend, oauth):
    processed_tweet_sents = []
    client = Query(**oauth)
    tweets = client.search_tweets(keywords=trend, limit=num_of_tweets)

    tweet_text = []

    for tweet in tweets:
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])

    # list of list of tweet words
    tweet_words = []

    for i in tweet_text:
        tweet_words.append(i.split())

    pre_process_words(tweet_words)

    for i in tweet_words:
        processed_tweet_sents.append(" ".join(i))
        
    return processed_tweet_sents



def main():
    oauth = credsfromfile()
    # Retrieve the WOEID (Where on Earth ID) for Seattle
    city = "Seattle"
    
    # Retrieve the top trends in Seattle
    trends = getTopTrends(city, oauth)
    trend = trends[0]
    tweets = get_final_tweet_sents(10, trend, oauth)
    analyser = SentimentIntensityAnalyzer()
    
    print("\nCurrent Trend: %s\n" % trend)
    for tweet in tweets:
         sentiment = analyser.polarity_scores(tweet)
         print("{:-<40} {}".format(tweet, str(sentiment)))
         if (sentiment['compound'] > 0 and sentiment['pos'] > 0):
             print("This tweet was positive!\n")
         elif (sentiment['compound'] < 0 and sentiment['neg'] > 0):
             print("This tweet was negative!\n")
         elif (sentiment['neu'] == 1):
             print("This tweet was neutral!\n")

if __name__ == "__main__":
    main()
