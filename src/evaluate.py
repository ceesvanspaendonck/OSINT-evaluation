# local imports
import argparse
from helpers import check_connection, read_local_keys, read_instructions, check_user_blacklist, add_user_to_blacklist
from evaluator import evaluate_single_thread, evaluate_user
from scraper import scrape_threads, get_tweets_from_threads

def evaluate(item, keys, instructions, force_scrape, skip_scrape, skip_evaluation):
	# evalutate single thread if threadreader url
	if item.startswith('https://threadreaderapp.com/'):
		url = item
		evaluate_single_thread(url, keys, instructions, skip_scrape, skip_evaluation)
	# invalid url
	elif item.startswith('https://'):
		print(f'{item}: invalid url')
	# evaluate user
	else:
		user = item
		# skip users present in blacklist
		if check_user_blacklist(user):
			print(f'{user}: present in /local_data/blacklist_users.txt (due to previous search having no results)')
		else:
			# scrape threads if not skipped
			if not skip_scrape:
				results, query_limit = scrape_threads(user, keys, force_scrape)
				# extract tweets if threads have been found
				if results:
					if get_tweets_from_threads(user, force_scrape):
						# evaluate tweets if found and not skipped
						if not skip_evaluation:
							evaluate_user(user, keys, instructions)
					else:
						print(f'{user}: no tweets could be scraped for evaluation')
				else:
					# if no threads have been found and query limit has not been hit
					# add user to blacklist
					if query_limit == False:
						print(f'{user}: no threads have been found in search, add user to blacklist')
						add_user_to_blacklist(user)
			else:
				# evaluate user directly
				if not skip_evaluation:
					evaluate_user(user, keys, instructions)

def main():
	# add arguments
	parser = argparse.ArgumentParser(prog = 'evaluate.py',
									 description =  'Tool to evaluate threads of X/Twitter users based on custom instructions using GPT',
									 epilog = 'Cees van Spaendonck - University of Amsterdam - 12425001 - New Media & Digital Culture MA Thesis - June 2024')
	parser.add_argument('input', type = str, help = 'help')
	parser.add_argument('--force_scrape', type = bool, default = False)
	parser.add_argument('--skip_scrape', type = bool, default = False)
	parser.add_argument('--skip_evaluation', type = bool, default = False)
	args = parser.parse_args()

	# check internet connection
	if check_connection() is False:
		print('no internet connection')
		exit()

	# check if keys and instructions can be read
	try:
		keys = read_local_keys()
	except:
		print('error: keys could not be read from /secrets/keys.json')
		exit()
	try:
		instructions = read_instructions()
	except:
		print('error: instructions could not be read from /secrets/instructions.txt')
		exit()

	# evaluate item(s)
	if ',' in args.input:
		for item in args.input.split(','):
			evaluate(item, keys, instructions, args.force_scrape,
											   args.skip_scrape,
											   args.skip_evaluation)
	else:
		evaluate(args.input, keys, instructions, args.force_scrape,
											 	 args.skip_scrape,
												 args.skip_evaluation)
if __name__ == '__main__':
	main()