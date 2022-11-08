import logging
import praw
import os
from dotenv import load_dotenv


def main():
    # Log all messages to the terminal, because we don't want to clutter the
    # repo for now with log files.
    # TODO: Add log files to the repo.
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting bot and loading environment variables.")
    load_dotenv()

    try:
        logging.info("Assigning env vars to Python vars.")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        user_agent = os.getenv("USER_AGENT")
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")

        logging.info("Creating a Reddit instance via PRAW.")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

    except:
        raise ConnectionError("Network connection could not be established")

    logging.info("Successfully connected to Reddit via PRAW Reddit instance.")
    logging.info("Describing standard output message of bot.")
    bot_message = '''Hi there! Thanks for posting to r/EngineeringResumes. If you haven't already, make sure to check out these posts and edit your resume accordingly: \n
- [Wiki](https://www.reddit.com/r/EngineeringResumes/comments/m2cc65/new_and_improved_wiki/) \n
- [Resume critique videos](https://www.reddit.com/r/EngineeringResumes/comments/j0ujid/resume_critique_videos_5_6/) \n
- [Resume redline albums](https://www.reddit.com/r/EngineeringResumes/comments/p5y5at/resume_redline_imgur_albums/) \n
- [Learn how to apply the STAR method](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) \n
- [Learn how to apply the XYZ method](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html) \n
*Beep, boop - this is an automated reply. If you've got any questions surrounding my existance, please [contact the moderators of this subreddit](https://www.reddit.com/message/compose/?to=/r/engineeringresumes&subject=Problem%20or%20question%20regarding%20bot&message=)!*
'''

    logging.info("Creating a subreddit instance.")
    subreddit = reddit.subreddit("engineeringresumes")

    logging.info("Creating a stream of new submissions with a limit of 20.")
    for submission in subreddit.new(limit=20):
        # We can't store information about previously answered submissions,
        # so we have to check if the bot has already replied to the submission.
        logging.info(
            f"Checking if submission {str(submission.id)} with the title '{str(submission.title[:15])}...' has already been replied to.")
        already_answered = False

        while not already_answered:

            # The bot will only make top-level replies to a post, so we only
            # look for those top-level comments on each post:
            for comment in submission.comments:
                # Check if the author of current top-level comment is our bot:
                if comment.author == str(username):
                    # If the post was already replied to, we set the flag to
                    # True and break out of the loop.
                    already_answered = True
                    break

            # There is no top-level comment from our bot, so we now need to
            # comment with the defined message.
            if not already_answered:
                bot_comment = submission.reply(bot_message)
                bot_comment.mod.distinguish(how='yes', sticky=True)
                bot_comment.mod.lock()
                logging.info(
                    f'Added a locked bot message to submission {submission.id}.')

                already_answered = True

            else:
                logging.info(
                    f'Submission {submission.id} has already been answered.')

    logging.info("Finished running the bot.")


if __name__ == "__main__":
    main()
