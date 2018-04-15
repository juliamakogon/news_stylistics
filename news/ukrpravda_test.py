import unittest
from news.spiders.ukrpravda import UkrpravdaSpider

class UkrpravdaSpiderTest(unittest.TestCase):
    def test_00_get_autocategory(self):
        urls = [r'https://www.pravda.com.ua/news/2018/04/7/7177080/',
                r'http://life.pravda.com.ua/society/2018/04/8/230065/']
        expected = ['news', 'society']
        for i in range(len(urls)):
            actual = UkrpravdaSpider.get_autocategory(urls[i])
            self.assertEqual(expected[i], actual)

    
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()