import asyncpraw
import logging
import unittest
from main import set_up_logger, instatiate_reddit
from dotenv import load_dotenv
import os


class LoggerTestCase(unittest.TestCase):
    '''Tests that check the logger instantiation and levels.

    The logger should be set up to log all messages to the terminal. We're also interested in the logger levels for the PRAW and PRAWCore loggers.'''

    def setUp(self):
        set_up_logger()

    def testLoggerLevel(self):
        self.assertTrue(isinstance(logging.getLogger("praw"), logging.Logger))
        self.assertTrue(isinstance(
            logging.getLogger("prawcore"), logging.Logger))
        self.assertTrue(isinstance(logging.getLogger(), logging.Logger))


class RedditInstanceTestCase(unittest.IsolatedAsyncioTestCase):
    '''Tests that check the Reddit instance creation and connection to the Reddit API.'''
    reddit: asyncpraw.Reddit

    async def testCreateSubredditInstance(self):
        '''Tests the connection to and interaction with the Reddit API.

        We should be able to create a Reddit instance and connect to the Reddit API.'''

        return_array = await instatiate_reddit()

        self.reddit = return_array[0]
        username = return_array[1]

        self.assertTrue(isinstance(self.reddit, asyncpraw.Reddit))
        self.assertTrue((username != None))

        await self.reddit.close()


if __name__ == "__main__":
    unittest.main()
