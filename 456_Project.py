from nltk.twitter import Query, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy
MAXTWEETS = 100
FAVE_RATIO = 0.01
RETWEET_RATIO = 0.001
FOLLOWERS_RATIO = 0.0001
    
def getTopTrends(totalTrends, name, api):
    ID = 0
    for trend in api.trends_available():
        if (trend['name'] == name):
            ID = trend['woeid']
    trends = api.trends_place(ID)
    trendNames = [trend['name'] for trend in trends[0]['trends'][0:totalTrends]]
    return trendNames

def pre_process_words(tweet_words):
    for item in list(tweet_words):
        for word in list(item):
            if word.startswith("http"):
                item.remove(word)

        if item[0] == "RT":
            item.remove("RT")

        if item[0].startswith("@"):
            item.remove(item[0])

def preprocess_tweet(raw_tweets):
    tweet_text = []
    processed_tweet_sents = []
    retweet_counts = []
    fave_counts = []
    followers_counts = []

    i = 0
    for tweet in raw_tweets:
        i+=1
        #if i<2:
        #    print(tweet)
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])
            retweet_counts.append(tweet['retweet_count'])
            fave_counts.append(tweet['favorite_count'])
            followers_counts.append(tweet['user']['followers_count'])

    # list of list of tweet words
    tweet_words = []
    for i in tweet_text:
        tweet_words.append(i.split())

    pre_process_words(tweet_words)

    for i in tweet_words:
        processed_tweet_sents.append(" ".join(i))

    return processed_tweet_sents, retweet_counts, fave_counts, followers_counts

#gets user input 
def get_user_input(options):
    invalid = 1
    while(invalid):
        entry = input("Enter 1 for trends of the US: \n" 
                      + "Enter 2 for trends of Seattle: \n"
                      + "Enter 3 for trends of a city in the US: \n")
        selection = []
        if entry == '1':
             print('<US>')
             selection = "United States"
             invalid = 0
        elif entry == '2':
            print('<Seattle>')
            selection = 'Seattle'
            invalid = 0
        elif entry == '3':
            print('<City>')
            city = input("Enter a city name from the following options: {}\n".format(options))
            selection = city
            while selection not in options:
                selection = input("Enter a valid city name:\n")
            invalid = 0
        else:
            print("Invalid Selection. Try again.")
    notInt = 1
    while(notInt):
        totalTrends = input("Enter the number of trends you would like to have. Pick a number between 0 and 20:\n")
        try:
            totalTrends = int(totalTrends)
        except ValueError:
            print("That's not an integer, try again")
        else:
            if totalTrends > 0 and totalTrends <= 20:
                notInt = 0
            else:
                print("Enter a total between 0 and 20.")
                
    return totalTrends, selection

def getOpinionTotals(tweets, retweet_counts, fave_counts, followers_count):
    analyser = SentimentIntensityAnalyzer()
    totals = {'Positive': 0, 'Negative': 0, 'Neutral': 0}

    i = 0
    for tweet in tweets:
        sentiment = analyser.polarity_scores(tweet)
        #print("{:-<40} {}".format(tweet, str(sentiment)))
        if (sentiment['compound'] > 0 and sentiment['pos'] > 0):
            totals['Positive'] += (1 + RETWEET_RATIO * retweet_counts[i] + FAVE_RATIO * fave_counts[i] + followers_count[i] * FOLLOWERS_RATIO)
        elif (sentiment['compound'] < 0 and sentiment['neg'] > 0):
            totals['Negative'] += (1 + RETWEET_RATIO * retweet_counts[i] + FAVE_RATIO * fave_counts[i] + followers_count[i] * FOLLOWERS_RATIO)
        elif (sentiment['neu'] == 1):
            totals['Neutral'] += (1 + RETWEET_RATIO * retweet_counts[i] + FAVE_RATIO * fave_counts[i] + followers_count[i] * FOLLOWERS_RATIO)
        i+=1
    return totals

def getOpinionsOfTopic(topic, oauth):
    client = Query(**oauth)
    tweets = client.search_tweets(keywords=topic, limit=MAXTWEETS)
    tweets, retweet_counts, fave_counts, followers_count = preprocess_tweet(tweets)
    totals = getOpinionTotals(tweets, retweet_counts, fave_counts, followers_count)

    adjustedTotal = totals['Positive'] + totals['Negative'] + totals['Neutral']
    posPercent = totals['Positive'] / adjustedTotal
    negPercent = totals['Negative'] / adjustedTotal
    neuPercent = totals['Neutral'] / adjustedTotal
    print("Opinions for the topic \"{}\":\nPositive: {:.0%}, Negative: {:.0%}, Neutral: {:.0%} out of {} tweets.\n"
                  .format(topic, posPercent, negPercent, neuPercent, MAXTWEETS))

def main():
    oauth = credsfromfile()

    while True:
        entry = input("Enter 1 to search a topic: \n"
                      + "Enter 2 to analyze trends: \n")
        if entry == '1':
            keyword = input("Enter a keyword or hashtag to search: ")
            getOpinionsOfTopic(keyword, oauth)

        elif entry == '2':
            auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
            auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
            api = tweepy.API(auth)

            options = []
            for trend in api.trends_available():
                if (trend['countryCode'] == 'US' and trend['name'] != 'United States'):
                    options.append(trend['name'])

            totalTrends, location = get_user_input(options)
            trends = getTopTrends(totalTrends, location, api)
            for trend in trends:
                getOpinionsOfTopic(trend, oauth)
        else:
            break
    
if __name__ == "__main__": main()