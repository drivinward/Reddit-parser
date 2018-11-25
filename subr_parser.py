import re
import json, csv
import praw
import datetime as dt

reddit = praw.Reddit(client_id='WSLpAk1pojs9bg',
                     client_secret='5qay_6Hr3RjA041rfHbYH_5Zij8',
                     user_agent='ward_scraper',
                     username='drivinward',
                     password='M26UtyvHgkAg7J4HqjfxG83X')

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