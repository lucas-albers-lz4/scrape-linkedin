
import unittest
from scrape import parse_job_listing

class TestJobScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load test cases"""
        cls.test_cases = {
    