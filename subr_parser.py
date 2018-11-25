import sys, re, json
import praw
import datetime as dt

credentials_file = sys.argv[1]
with open(credentials_file, 'r') as cf:
    credentials = json.load(cf)[0]

    start_string = "Found following credentials in " + str(credentials_file) + " :"
    print "=" * len(start_string)
    print start_string
    print "-" * len(start_string)
    print json.dumps(credentials, sort_keys=True, indent=2, encoding='utf-8')

reddit = praw.Reddit(client_id=credentials['client_id'],
                     client_secret=credentials['client_secret'],
                     user_agent=credentials['user_agent'],
                     username=credentials['username'],
                     password=credentials['password'])

sub = reddit.subreddit('the_donald')
tops = sub.top(limit=500)

posts = []

for i, s in enumerate(tops):
    # replace special characters and UTF-8 encoding
    body = s.selftext
    title = s.title
    url = s.url
    replacements = [
        (r'\n', ' '),
        (r'\s{2,}', ' '),
        (r'#+', '')
    ]
    for old, new in replacements:
        body = re.sub(old, new, body)
        title = re.sub(old, new, title)
        url = re.sub(old, new, url)

    posts.append({
        "title": title,
        "score": s.score,
        "id": s.id,
        "url": url,
        "comms_num": s.num_comments,
        "created": str(dt.datetime.fromtimestamp(s.created)),
        "body": body
    })

    print i, "of", tops.limit, "processed", "\033[1A\r"

# print posts

data = json.dumps(posts, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
output_file = 'reddited.json'
with open(output_file, 'w') as fo:
    fo.write(data)