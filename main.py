from logging import raiseExceptions
import praw
import os

def main():
    try:
        # Dev environment on local machine
        # reddit = praw.Reddit(
        #     client_id=secret.client_id,
        #     client_secret=secret.client_secret,
        #     user_agent=secret.user_agent,
        #     username=secret.username,
        #     password=secret.password
        # )

        reddit = praw.Reddit(
            client_id=os.environ['CLIENT_ID'],
            client_secret=os.environ['CLIENT_SECRET'],
            user_agent=os.environ['USER_AGENT'],
            username=os.environ['USERNAME'],
            password=os.environ['PASSWORD']
        )

    except:
        raise ConnectionError("Network connection could not be established")

    # The standard bot_message as a reply to new posts
    bot_message = '''Hi there! Thanks for posting to r/EngineeringResumes. If you haven't already, make sure to check out these posts and edit your resume accordingly: \n
- [Wiki](https://www.reddit.com/r/EngineeringResumes/comments/m2cc65/new_and_improved_wiki/) \n
- [Resume critique videos](https://www.reddit.com/r/EngineeringResumes/comments/j0ujid/resume_critique_videos_5_6/) \n
- [Resume redline albums](https://www.reddit.com/r/EngineeringResumes/comments/p5y5at/resume_redline_imgur_albums/) \n
- [Learn how to apply the STAR method](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) \n
- [Learn how to apply the XYZ method](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html) \n
*Beep, boop - this is an automated reply. If you've got any questions surrounding my existance, please [contact the moderators of this subreddit](https://www.reddit.com/message/compose/?to=/r/engineeringresumes&subject=Problem%20or%20question%20regarding%20bot&message=)!*
'''

    submission_limit = int(os.environ['SUBMISSION_LIMIT'])

    if submission_limit > 20:
        print("Submission limit is too high at {} and therefore automatically set to 20".format(submission_limit))
        submission_limit = 20

    # Are we able to only read but not edit comments? -> False, if we can edit them, too
    # print(reddit.read_only)

    subreddit = reddit.subreddit("engineeringresumes")
    # print(subreddit.display_name, subreddit.title)

    # Assume you have a Subreddit instance bound to variable `subreddit`
    for submission in subreddit.new(limit=submission_limit):
        # We'll go through each submission in the subreddit up until the set limit
        # print(submission.title, submission.score, submission.url, submission.id)

        # State for if the bot has already replied to the submission
        # Necessary, because Heroku Dynos don't allow persistance for any kind of data
        already_answered = False
        print("Currently checking submission {} with the title '{}...'".format(str(submission.id), str(submission.title)[:15]))

        while not already_answered: 

            # The bot will only make top-level replies to a post, so we only look for those top-level comments on each post
            for comment in submission.comments:
                # Check if the author of current top-level comment is our bot
                if comment.author == str(os.environ['USERNAME']):
                    # Was already answered -> exit loop and exit the routine as we don't need to check any more comments
                    already_answered = True
                    break
            
            # There is no top-level comment from our bot -> We now need to comment with the bot_message
            if not already_answered:
                bot_comment = submission.reply(bot_message)
                bot_comment.mod.distinguish(how='yes', sticky=True)
                bot_comment.mod.lock()
                print('Added a locked bot_message and stickied it on the post "' + submission.title[0:15] + '..."')
                already_answered = True

            else: 
                print('Submission has already been answered')
            
            # Now that we added the bot_message to the comments, we can continue with the next submission

if __name__ == "__main__":
    main()