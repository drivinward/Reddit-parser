'''
script by Edoardo Guido
https://edoardoguido.com
contact@edoardoguido.com

It is recommended to ugprade pip first...
    pip install --upgrade pip
    pip3 install --upgrade pip

...before installing PRAW modules
    pip install praw
    pip3 install praw

# HOW TO USE THIS SCRIPT
Two arguments are needed in order to correctly run this script:
1 - credentials file in .json format
    (you can fill in 'credentials.json' and then use this one)
2 - output filename (no need to specify extension)
3 - (optional) tells the script how to sort the comments of a post. 
    can be 'controversial', 'best', 'top', and so on. 
    If not specified, 'hot' is used.
'''

import sys, re, json
import datetime as dt

# importing Reddit's API
import praw

## ---------------------------- ##
##            METHODS           ##
## ---------------------------- ##

# valid_meta must be a python list of wanted elements
# to insert as keys in output json file
def get_meta(self, valid_meta):
    # get current comment's metadata
    comment_meta = {}
    for meta_key, meta_value in vars(self).items():
        if meta_key in valid_meta:
            comment_meta[meta_key] = meta_value
        if meta_key in valid_meta and meta_key is 'created_utc':
            comment_meta["created_utc"] = str(dt.datetime.fromtimestamp(meta_value))
        if meta_key is 'created':
            comment_meta["created_local"] = str(dt.datetime.fromtimestamp(meta_value))
    # returns a dictionary
    return comment_meta

# TO-DO: figure out how to use this
def get_comments_depth_n(comments, n, depth=0):
    # First check the end condition: reaching the desired depth
    # Return the comments list, which will be merged with other comment lists
    if depth == n:
        return comments
    
    # Otherwise continue to recur through the comment tree
    n_comments = list()         # List to store result comments
    for comment in comments:
        # Recur the method and get the result: a list of comments at the desired depth
        result = get_comments_depth_n(comment.replies, n, depth+1)
        # Store these comments with the rest of 'em
        n_comments.extend(result)
    
    return n_comments

## ---------------------------- ##
##            METHODS           ##
## ---------------------------- ##

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

# sub = reddit.submission(url='https://www.reddit.com/r/politics/comments/969lx1/what_happened_in_charlottesville_was_terrorism/?sort=controversial')
# sub = reddit.submission(id='969lx1')

# selecting which post to scrape based on its ID
which_post = raw_input("\nWhich post would you like to get data from?\nInsert post ID: ")
sub = reddit.submission(id=which_post)

if len(sys.argv) is 4 and sys.argv[3]:
    sub.comment_sort = str(sys.argv[3])
else:
    sub.comment_sort = 'top'

sub.comments.replace_more(limit=None, threshold=0)

input_data = []
replacements = [
    (r'\n', ' '),
    (r'^\n', ''),
    (r'\s{2,}', ' '),
    (r'#+', ''),
    (r'^>', ''),
    ('\"', '"')
]
for i, comment in enumerate(sub.comments):
    body = comment.body
    for old, new in replacements:
        body = re.sub(old, new, body)
    score = comment.score

    # list of desired keys to save from comment's metadata
    valid_meta = ['ups', 'downs', 'controversiality', 'id', 'created_local', 'created_utc']
    comment_meta = get_meta(comment, valid_meta)

    comment_id_no = str(i+1)
    if comment.score < 0:
        input_data.append({
            "body": body,
            "score": score,
            "score_isnegative": True,
            "id_order": comment_id_no,
            "meta": comment_meta
        })
    elif comment.score >= 0:
        input_data.append({
            "body": body,
            "score": score,
            "score_isnegative": False,
            "id_order": comment_id_no,
            "meta": comment_meta
        })
    
    # .list() method returns all the replies - and replies of replies, and so on -.
    for t, reply in enumerate(comment.replies.list()):
        body = reply.body
        for old, new in replacements:
            body = re.sub(old, new, body)
        score = reply.score

        reply_meta = get_meta(reply, valid_meta)
        comment_id_no = str(str(i+1) + "." + str(t+1))

        if score < 0:
            input_data.append({
                "body": body,
                "score": score,
                "score_isnegative": True,
                "id_order": comment_id_no,
                "meta": reply_meta
            })
        elif score >= 0:
            input_data.append({
                "body": body,
                "score": score,
                "score_isnegative": False,
                "id_order": comment_id_no,
                "meta": reply_meta
            })

## checking that everything's right before writing data to file
# print input_data

# post metadata
post_meta = {}
for var_key, var_value in vars(sub).items():
    if type(var_value) is int or type(var_value) is float or type(var_value) is bool:
        print var_key, "is a", type(var_value)
        post_meta[var_key] = var_value
    else:
        print var_key, "is a", type(var_value)
        post_meta[var_key] = str(var_value)
    

# formatting data to JSON before output
output_data = json.dumps(input_data, sort_keys=False, indent=2, ensure_ascii=False).encode('utf-8')
post_meta = json.dumps(post_meta, sort_keys=False, indent=2, ensure_ascii=False).encode('utf-8')
output_file = sys.argv[2] + ".json"

# writing data to JSON file
with open(output_file, 'w') as fo:

    # for var_key, var_value in vars(sub).items():
    #     fo.write("# ")
    #     fo.write(str(var_key))
    #     fo.write(": ")
    #     fo.write(str(var_value))
    #     fo.write("\n")

    fo.write(post_meta)
    fo.write(",\n")
    fo.write(output_data)

end_string = "Done writing " + str(len(input_data)) + " entries in " + output_file + "."
print "-" * len(end_string)
print end_string
print "=" * len(end_string)

## checking that everything's right in what's been written on file
# print output_data