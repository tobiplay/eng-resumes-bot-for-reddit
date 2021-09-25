import praw
import secret

reddit = praw.Reddit(
    client_id=secret.client_id,
    client_secret=secret.client_secret,
    user_agent=secret.user_agent,
    username=secret.username,
    password=secret.password
)

# The standard bot_message as a reply to new posts
bot_message = "Hello, this is our bot message!"

# Are we able to only read but not edit comments? -> False, if we can edit them, too
print(reddit.read_only)

subreddit = reddit.subreddit("engineeringresumes")
# print(subreddit.display_name, subreddit.title)

# Assume you have a Subreddit instance bound to variable `subreddit`
for submission in subreddit.new(limit=10):
    # Print information about each submission in the subreddit up until the set limit
    # print(submission.title)
    # print(submission.score)
    # print(submission.id)
    # print(submission.url)

    already_answered = False

    while not already_answered: 
        print("Current submission: " + str(submission.id))
        # The bot will only make top-level replies to a post, so we only look for those
        for comment in submission.comments:
            if comment.author == "TobiPlay":
                print("The Thread with the title " + submission.title[0:15] + "... has already been answered!")
                already_answered = True
        
        # There is not a top-level comment from our bot -> We now need to comment with the bot_message
        print("Bot replied with our message.")

        # Now that we added the bot_message to the comments, we can continue with the next submission
        already_answered = True

        # print(comment.body)