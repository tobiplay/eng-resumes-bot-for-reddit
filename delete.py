import logging
import asyncpraw
import asyncio
import os
from dotenv import load_dotenv


def set_up_logger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    # Log all messages to the terminal, because we don't want to clutter the
    # repo for now with log files.
    # TODO: Add log files to the repo.
    logging.basicConfig(level=logging.INFO)


async def main():
    """Deletes all bot comments from the last 20 posts in the subreddit.

    The sorting is done by new, so the last 20 posts are the newest 20 posts.
    This is a safety-method in case the bot tests do something weird, or the message gets linted into the wrong format. It's only ever called on a local
    machine for debugging purposes when tweaking the test suite or main method."""
    try:
        set_up_logger()

        logging.info("Starting bot and loading environment variables.")

        load_dotenv()

        logging.info("Assigning env vars to Python vars.")
        try:
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            user_agent = os.getenv("USER_AGENT")
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")

            logging.info("Creating a Reddit instance via PRAW.")
            reddit = asyncpraw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password,
            )

        except:
            raise ConnectionError("Network connection could not be established")

        logging.info("Successfully connected to Reddit via PRAW Reddit instance.")
        logging.info("Describing standard output message of bot.")
        bot_message = """Hi there! Thanks for posting to r/EngineeringResumes. If you haven't already, make sure to check out these posts and edit your resume accordingly: \n
- [Wiki](https://www.reddit.com/r/EngineeringResumes/comments/m2cc65/new_and_improved_wiki/) \n
- [Resume critique videos](https://www.reddit.com/r/EngineeringResumes/comments/j0ujid/resume_critique_videos_5_6/) \n
- [Resume redline albums](https://www.reddit.com/r/EngineeringResumes/comments/p5y5at/resume_redline_imgur_albums/) \n
- [Learn how to apply the STAR method](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) \n
- [Learn how to apply the XYZ method](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html) \n
*Beep, boop - this is an automated reply. If you've got any questions surrounding my existance, please [contact the moderators of this subreddit](https://www.reddit.com/message/compose/?to=/r/engineeringresumes&subject=Problem%20or%20question%20regarding%20bot&message=)!*"""

        logging.info("Creating a subreddit instance.")
        subreddit = await reddit.subreddit("engineeringresumes", fetch=True)
        logging.info(f"Grabbed 'r/{subreddit.display_name}'.")

        # Althugh I'm not a huge fan of magic numbers, hardcoding the limit
        # as 20 is sufficient for now.
        logging.info("Iterating through the stream of new 20 submissions.")
        async for submission in subreddit.new(limit=20):
            # We can't store information about previously answered submissions,
            # so we have to check if the bot has already replied to the
            # submission.
            logging.info(
                f"Checking if submission {str(submission.id)} with the title '{str(submission.title[:15])}...' has already been replied to."
            )

            # The bot will only make top-level replies to a post, so we
            # look for those top-level comments on each post:
            comments = await submission.comments()

            # If the submission has no comments, or there's no comment by the
            # bot, then we obviously don't have to delete anything.
            if not comments:
                logging.info("No comments found. Nothing to delete.")

            else:
                logging.info("Found comments and checking for bot replies.")

                # By specifying a limit of 0, we remove all instances of `MoreComments` from the comment forest and only get the top-level comments in the submission.
                await comments.replace_more(limit=0)

                for top_level_comment in comments:
                    # "Beep, boop" is only ever found in the bot's replies.
                    if "Beep, boop" in top_level_comment.body:
                        await top_level_comment.delete()
                    else:
                        logging.info("Not a bot reply. Won't delete it.")

        # Kill the connection to Reddit.
        await reddit.close()
        logging.info("Finished running the bot.")

        return True

    except Exception as e:
        logging.error(f"Error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())
