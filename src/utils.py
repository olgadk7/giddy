import pandas as pd
import yfinance as yf
import numpy as np

import nltk
nltk.download('punkt')
from textblob import TextBlob

keywords_original = ["feel", "believe", "sense", "why does", "how does", "how come", "how much", 
"when will", "isn’t it", "wait for", "add to", "should I", "should we", "scale in", "scale out"
           ]

keywords = [
    "to the moon", "diamond hands", "printing money", "rocketing", "skyrocketing", "moonshot", 
    "going parabolic", "stonks only go up", "tendies", "loaded", "rolling in dough", "yolo'd", 
    "hit the jackpot", "we're rich, baby", "feeling bullish", "bonkers", "confused", "don't understand", 
    "what's happening", "can't believe", "mind blown", "can't wrap my head around", "baffled", "stumped", 
    "flabbergasted", "scratching my head", "out of the loop", "lost", "in the dark", 
    "can't make heads or tails", "doesn't compute", "doesn't add up", "what the heck", "bamboozled", 
    "puzzled", "thrown for a loop", "at a loss", "what in the stonks", "surprised", "feel", "believe", 
    "sense", "why does", "how does", "how come", "how much", "when will", "isn’t it", "wait for", 
    "add to", "should I", "should we", "scale in", "scale out"
]

def get_posts_df(stock_name, stock_ticker):
    df_wsb = pd.read_csv('../data/raw/wallstreetbets/posts.csv')
    print("Full data: ", df_wsb.shape)

    # check if there are missing values in the col that we later need to not have any
    df_wsb[df_wsb['title'].isna()]
    # deleting those 
    df_noNan = df_wsb.dropna(subset=['title'])
    # confirm the amount of rows reduced accordingly 
    print("No NaN data: ", df_noNan.shape)

    df_noNan = df_noNan.rename(columns={'selftext': 'text'})

    # This will return a DataFrame containing only the rows where the posts "title" and "text" column contains "GameStop"
    posts = df_noNan[(df_noNan['title'].str.contains(stock_name, case=False) | df_noNan['title'].str.contains(stock_ticker, case=False) |
                             df_noNan['text'].str.contains(stock_name, case=False) | df_noNan['text'].str.contains(stock_ticker, case=False))]
    print("Stock data only: ", posts.shape)

    posts['date'] = pd.to_datetime(df_noNan['created_utc'], unit='s')

    posts_df = posts[['title', 'text', 'date', 'removed_by_category','link_flair_text', 'full_link', 'url', 'id', 'over_18', 'pinned']]
    print("Useful cols only: ", posts_df.shape)
    
    return posts_df
    

def get_stock_prices(ticker, start_date, end_date):
    # Download the data
    gme = yf.Ticker(ticker)

    # Get the data for the specified period
    df = gme.history(start=start_date, end=end_date)

    df = df.reset_index()

    # print(df.shape)
    
    return df


def count_bewildered_keywords(df, keywords):
    # Function to count number of bewildered keywords in a string
    def count_keywords(text):
        if isinstance(text, str):
            text = text.lower()
            count = sum(text.count(keyword) for keyword in keywords)
            return count
        else:
            return 0
        
    # # Fill missing values in 'text' column with empty strings
    # posts_df['text'].fillna("", inplace=True)

    # Function to count total number of words in a string
    def count_words(text):
        if isinstance(text, str):
            return len(text.split())
        else:
            return 0

    # Apply the functions to 'title' and 'text' columns and store the results in new columns
    df['keyword_count'] = df['title'].apply(count_keywords) + df['text'].apply(count_keywords)
    df['word_count'] = df['title'].apply(count_words) + df['text'].apply(count_words)

    # Calculate the percentage of keywords and store the result in a new column
    df['keyword_percentage'] = ((df['keyword_count'] / df['word_count'] * 100)).round(2)
    
    # Define a new order of columns
    new_order = ['keyword_count', 'word_count', 'keyword_percentage', 'title', 
                 'text', 'date', 'id', 'link_flair_text', 'over_18', 
                 'pinned', 'removed_by_category', 'full_link', 'url']
    
    # Reorder the DataFrame
    df = df.reindex(columns=new_order)
    
    return df.sort_values(by='keyword_percentage', ascending=False)




def get_total_keyword_df(df, keywords, frequency_string): # input 'D' or 'H'
    
    # Function to count keyword mentions
    def keyword_mentions(text):
        if isinstance(text, int):
            return 0
        else:
            tokens = TextBlob(text).words
            keyword_tokens = sum(token in keywords for token in tokens)
            return keyword_tokens

    # Function to count total tokens
    def total_tokens(text):
        if isinstance(text, int):
            return 0
        else:
            tokens = TextBlob(text).words
            total_tokens = len(tokens)
            return total_tokens
    
    # Create a new DataFrame with 'date' as index, 'title' and 'text' as columns
    new_df = df[['date', 'title', 'text']].copy()
    new_df.set_index('date', inplace=True)
    # print(type(new_df.index))
    
    # Concatenate 'title' and 'text' columns and then resample
    concatenated_text = (new_df['title'].fillna('') + ' ' + new_df['text'].fillna(''))
    resampled_concatenated_text = concatenated_text.resample(frequency_string).sum()

    # Apply the functions
    total_mentions = resampled_concatenated_text.apply(keyword_mentions)
    total_tokens = resampled_concatenated_text.apply(total_tokens)

    # Construct the final DataFrame
    total_keyword_df = pd.DataFrame({
        'total_mentions': total_mentions, 
        'total_tokens': total_tokens
    })

    # Calculate percentage
    total_keyword_df['percentage'] = (total_keyword_df['total_mentions'] / total_keyword_df['total_tokens']) * 100
    
    return total_keyword_df




def get_per_keyword_df(posts_df, keywords, frequency_string):
    # Function to tokenize text and count occurrences of keywords; returns percentages per keword
    def keyword_percentage_per_keyword(text_series):
        text_series = text_series.astype(str).replace('nan', '')
        total_tokens = 0
        keyword_counts = dict.fromkeys(keywords, 0)
        for text in text_series:
            tokens = TextBlob(text).words
            total_tokens += len(tokens)
            for token in tokens:
                if token in keywords:
                    keyword_counts[token] += 1
        # Convert counts to percentages
        for keyword in keyword_counts:
            keyword_counts[keyword] = np.nan if total_tokens == 0 else (keyword_counts[keyword] / total_tokens) * 100
        return pd.Series(keyword_counts)

    # Make sure 'date' set as index for resampling to work
    posts_df.set_index('date', inplace=True)

    # Resample DataFrame and apply function
    percentage_keyword_df = posts_df.resample(frequency_string).apply(lambda x: keyword_percentage_per_keyword(x['title'] + ' ' + x['text']))
    
    return percentage_keyword_df