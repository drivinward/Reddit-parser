import sys, re, json
import datetime as dt

# importing Reddit's API
import praw

## ---------------------------- ##
##            METHODS           ##
## ---------------------------- ##

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

# figure out how to use this
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

# # selecting which post to scrape based on its ID
# which_post = raw_input("\nWhich post would you like to get data from?\nInsert post ID: ")

# # sub = reddit.submission(url='https://www.reddit.com/r/politics/comments/969lx1/what_happened_in_charlottesville_was_terrorism/?sort=controversial')
# sub = reddit.submission(id=which_post)

sub = reddit.submission(id='969lx1')
sub.comment_sort = 'controversial'
sub.comments.replace_more(limit=None, threshold=0)

input_data = []
replacements = [
    (r'\n', ' '),
    (r'^\n', ''),
    (r'\s{2,}', ' '),
    (r'#+', '')
]
for i, comment in enumerate(sub.comments):
    # if i is 20:
    #     print vars(comment).items()

    body = comment.body
    for old, new in replacements:
        body = re.sub(old, new, body)
    score = comment.score

    # list of desired keys to save from comment's metadata
    valid_meta = ['ups', 'downs', 'controversiality', 'id', 'created_local', 'created_utc']
    comment_meta = get_meta(comment, valid_meta)

    comment_id_no = str(i)
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
        comment_id_no = str(str(i) + "." + str(t+1))

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
        # print input_data

## checking that everything's right before writing data to file
# print input_data

# formatting data to JSON before output
output_data = json.dumps(input_data, sort_keys=False, indent=2, ensure_ascii=False).encode('utf-8')
output_file = sys.argv[2]

# writing data to JSON file
with open(output_file, 'w') as fo:
    fo.write(output_data)

end_string = "Done writing " + str(len(input_data)) + " entries in " + output_file + "."
print "-" * len(end_string)
print end_string
print "=" * len(end_string)

## checking that everything's right in what's been written on file
# print output_data