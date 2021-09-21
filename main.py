import praw
import secret

reddit = praw.Reddit(
    client_id=secret.client_id,
    client_secret=secret.client_secret,
    user_agent=secret.user_agent,
    username=secret.username,
    password=secret.password
)

print(reddit.read_only)

subreddit = reddit.subreddit("engineeringresumes")