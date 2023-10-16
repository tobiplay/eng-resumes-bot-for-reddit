"""Module as the main entry point for the bot."""
import asyncio
import logging
import os

import asyncpraw
from dotenv import load_dotenv


def set_up_logger() -> None:
    """Set up the logger."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    # Log all messages to the terminal, because we don't want to clutter the
    # repo for now with log files.
    # TODO(TobiPlay): Add log files to the repo.
    logging.basicConfig(level=logging.INFO)

    logging.info("Logger set up. Starting bot.")


async def instatiate_reddit() -> list:
    """Instantiate the Reddit instance."""
    set_up_logger()

    logging.info("Loading environment variables.")
    load_dotenv()

    logging.info("Assigning env vars to Python vars.")
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

    return [reddit, username]


async def main() -> bool:
    """Run the bot.

    The bot will reply with a pre-defined message to a set of previous posts.

    """
    try:
        return_array = await instatiate_reddit()

        reddit = return_array[0]
        username = return_array[1]

        logging.info(
            "Successfully connected to Reddit via PRAW Reddit instance. Returning Reddit instance and username.",
        )

        logging.info("Describing standard output message of bot.")
        bot_message = """Hi there! Thanks for posting to r/EngineeringResumes. If you haven't already, make sure to check out these posts and edit your resume accordingly: \n
- [Wiki](https://reddit.com/r/EngineeringResumes/wiki/) \n
- [Learn how to apply the STAR method](https://www.careereducation.columbia.edu/resources/resumes-impact-creating-strong-bullet-points) \n
- [Learn how to apply the XYZ method](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html) \n
- [Resume critique photo albums](https://www.reddit.com/r/EngineeringResumes/comments/p5y5at/resume_redline_imgur_albums/) \n
- [Resume critique videos](https://www.reddit.com/r/EngineeringResumes/comments/j0ujid/resume_critique_videos_5_6/) \n
*Beep, boop––this is an automated reply. If you've got any questions surrounding my existance, please [contact the moderators of this subreddit](https://www.reddit.com/message/compose/?to=/r/engineeringresumes&subject=Problem%20or%20question%20regarding%20bot&message=)!*
"""

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
                f"Checking if submission {str(submission.id)} with the title '{str(submission.title[:15])}...' has already been replied to.",
            )

            # The bot will only make top-level replies to a post, so we
            # look for those top-level comments on each post:
            comments = await submission.comments()

            # If the submission has no comments, or there's no comment by the
            # bot, then we can reply to the submission.
            if not comments:
                logging.info("No comments found. Reply with bot message.")
                bot_comment = await submission.reply(bot_message)
                await bot_comment.mod.distinguish(how="yes", sticky=True)
                await bot_comment.mod.lock()

            else:
                already_replied = False

                logging.info("Found comments and checking for bot replies.")
                # The bot will only make top-level replies to a post, so we
                # look for those top-level comments on each post:
                for comment in comments:
                    if comment.author == str(username):
                        logging.info(
                            f"Submission {submission.id} has already been answered.",
                        )
                        already_replied = True
                        break

                if not already_replied:
                    logging.info("No bot replies found. Reply with bot message.")
                    bot_comment = await submission.reply(bot_message)
                    await bot_comment.mod.distinguish(how="yes", sticky=True)
                    await bot_comment.mod.lock()

        # Kill the connection to Reddit.
        await reddit.close()
        logging.info("Finished running the bot.")

        return True

    except Exception as e:
        logging.error(f"Error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())
