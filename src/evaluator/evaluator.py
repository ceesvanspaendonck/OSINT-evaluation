# local imports
import json
import os
from scraper import extract_tweets_from_url

# third party imports
import pandas as pd
from openai import OpenAI

def evaluate_user(user, keys, instructions):
	# evaluate all threads in local data of specified user

	# open .csv file of tweets by user
	tweets_filename = f'./local_data/{user}/{user}_tweets.csv'
	tweets_df = None
	try:
		tweets_df = pd.read_csv(tweets_filename)
	except:
		print(f'{user}: no file for tweets found at: {tweets_filename} - evaluation skipped')
		return

	# extract all tweets, grouped per thread
	user_evaluations = list()
	threads = tweets_df.groupby('thread_id')
	for thread_id, group in threads:
		thread_tweets = []
		for index, row in group.iterrows():
			tweet = {
			'body': row['body'],
			'tweet_urls': row['tweet_urls'],
			'tweet_images': row['tweet_images']}
			thread_tweets.append(tweet)

		# get evalation of thread tweets
		usage, result = get_evaluation(thread_tweets, keys, instructions)
		if result is not None:
			# add result to user_evaluations if in JSON format
			try:
				result = json.loads(result)
				result['thread'] = thread_id
				user_evaluations.append(result)
			except:
				print(f'{user}: evaluation of {thread_id} is not saved as the response is not structured in JSON format. please check /secrets/instructions.txt')
		else:
			print(f'{user}: error encountered when evaluting thread {thread_id}')

	# export user_evaluations to json file
	if user_evaluations:
		results_file = f'./local_data/{user}/{user}_evaluations.json'
		with open(results_file, 'w') as file:
			json.dump(user_evaluations, file, indent = 4)
		print(f'{user}: saved evaluations of {len(threads)} threads to to {results_file}')
	else:
		print(f'{user}: no evaluations saved')

def evaluate_single_thread(thread_url, keys, instructions, skip_scrape, skip_evaluation):
	# evaluate single thread

	# get thread_id from url, determine filename
	thread_id = thread_url[thread_url.rindex('/') + 1:]
	if '.' in thread_id:
		thread_id = thread_id[:thread_id.rindex('.')]
	tweets_filename = f'./local_data/individual threads/{thread_id}_tweets.csv'

	if skip_scrape:
		# attempt to read tweets from /local_data/ if scraping is skipped
		try:
			tweets_df = pd.read_csv(tweets_filename)
		except:
			print(f'{thread_id}: error reading tweets from {tweets_filename}')
			return
	else:
		# scrape tweets
		tweets_df = pd.DataFrame(columns = ['thread_id', 'id', 'url', 'author', 'body', 'tweet_urls', 'tweet_images'])
		tweets_df = extract_tweets_from_url(thread_url, tweets_df)

		# create folder for individual results of not present
		if not os.path.isdir('./local_data/individual threads/'):
			os.makedirs('./local_data/individual threads/')

		tweets_df.to_csv(tweets_filename)
		print(f'{thread_id}: saved {len(tweets_df)} tweets of thread to {tweets_filename}')
	
	# make sure tweets have been extracted
	if len(tweets_df) < 1:
		print(f'{thread_url}: error in extracting tweets')
		return

	# evaluate tweets of thread
	if not skip_evaluation:
		thread_tweets = list()
		for index, row in tweets_df.iterrows():
			tweet = {
			'body': row['body'],
			'tweet_urls': row['tweet_urls'],
			'tweet_images': row['tweet_images']}
			thread_tweets.append(tweet)

		# get evalation of thread tweets
		usage, result = get_evaluation(thread_tweets, keys, instructions)
		if result is not None:
			# export result if in JSON format
			try:
				result = json.loads(result)
				results_filename = f'./local_data/individual threads/{thread_id}_evaluation.json'
				with open(results_filename, 'w') as file:
					json.dump(result, file, indent = 4)
				print(f'{thread_id}: saved evaluation of thread to {results_filename}')
			except:
				print(f'{thread_id}: evaluation is not saved as the response is not structured in JSON format. please check /secrets/instructions.txt')
		else:
			print(f'{thread_id}: error encountered when evaulting thread')

def get_evaluation(thread, keys, instructions):
	# get response from GPT API based on system instructions and thread

	# make sure open_ai api key is present
	if 'open_ai_key' not in keys:
		print('error: no open_ai_key present in keys.json')
		exit()

	# post to API, return result if no error occurs
	client = OpenAI(api_key = keys['open_ai_key'])
	try:
		response = client.chat.completions.create(
						model = 'gpt-3.5-turbo',
						temperature = 0.2,
						response_format = {
							'type': 'json_object'
						},
						messages = [
							{
	        					"role": "system", 
								"content": instructions
							},
	        				{
								"role": "user",
	            				"content": f"First, closely look at your custom instructions. Then, stick to them precisely to evaluate the following thread: {thread}"}
	      				]
	    				)
		return (response.usage, response.choices[0].message.content)
	except Exception as e:
		print(f'error: evaluation response from GPT: {e}')
		return (None, None)