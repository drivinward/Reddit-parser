import re
import json
import praw
import datetime as dt

## ---------------------------- ##
##            METHODS           ##
## ---------------------------- ##

def get_meta(valid_meta):
    # get current comment's metadata
    comment_meta = {}
    for meta_key, meta_value in vars(comment).items():
        if meta_key in valid_meta:
            comment_meta[meta_key] = meta_value
        if meta_key in valid_meta and meta_key is 'created_utc':
            comment_meta["created_utc"] = str(dt.datetime.fromtimestamp(meta_value))
        if meta_key is 'created':
            comment_meta["created_local"] = str(dt.datetime.fromtimestamp(meta_value))
    return comment_meta

## ---------------------------- ##
##            METHODS           ##
## ---------------------------- ##

credentials_file = 'credentials.json'
with open(credentials_file, 'r') as cf:
    credentials = json.load(cf)
    print "Found credentials:"
    print json.dumps(credentials, sort_keys=True, indent=2, encoding='utf-8')
    print

reddit = praw.Reddit(client_id=credentials[0]['client_id'],
                     client_secret=credentials[0]['client_secret'],
                     user_agent=credentials[0]['user_agent'],
                     username=credentials[0]['username'],
                     password=credentials[0]['password'])

# reddit = praw.Reddit(client_id='WSLpAk1pojs9bg',
#                      client_secret='5qay_6Hr3RjA041rfHbYH_5Zij8',
#                      user_agent='ward_scraper',
#                      username='drivinward',
#                      password='M26UtyvHgkAg7J4HqjfxG83X')

sub = reddit.submission(
    url='https://www.reddit.com/r/politics/comments/969lx1/what_happened_in_charlottesville_was_terrorism/?sort=controversial')

sub.comment_sort = 'controversial'
sub.comments.replace_more(limit=None, threshold=0)


input_data = []
replacements = [
    (r'\n', ' '),
    (r'^\n', ''),
    (r'\s{2,}', ' '),
    (r'#+', '')
]
for i, comment in enumerate(sub.comments.list()):
    # if i is 20:
    #     print vars(comment).items()

    body = comment.body
    for old, new in replacements:
        body = re.sub(old, new, body)
    score = comment.score

    # list of desired keys to save from comment's metadata
    valid_meta = ['ups', 'controversiality', 'id', 'created_local', 'created_utc']
    comment_meta = get_meta(valid_meta)

    if comment.score < 0:
        input_data.append({
            "body": body,
            "score": score,
            "score_isnegative": True,
            "meta": comment_meta
        })
    elif comment.score >= 0:
        input_data.append({
            "body": body,
            "score": score,
            "score_isnegative": False,
            "meta": comment_meta
        })

## checking that everything's right before writing data to file
# print input_data

# formatting data to JSON before output
output_data = json.dumps(input_data, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
output_file = 'posts_test.json'
# writing data to JSON file
with open(output_file, 'w') as fo:
    fo.write(output_data)
    print "Done writing", len(input_data), "entries in", "'" + output_file + "'."
    ## checking that everything's right in what's been written on file
    # print output_data