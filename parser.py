import praw
# import pandas as pd
# import datetime as dt

reddit = praw.Reddit(client_id='WSLpAk1pojs9bg',
    client_secret='5qay_6Hr3RjA041rfHbYH_5Zij8',
    user_agent='ward_scraper',
    username='drivinward',
    password='6qHnx9zZZ[#J2tayf%4tFq=m')

print(reddit.user.me())