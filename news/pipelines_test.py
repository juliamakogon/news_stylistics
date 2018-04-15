import unittest
from news.pipelines import convert_to_xml
from news.pipelines import check_path

class NewsPipelineTest(unittest.TestCase):
    def test_00_convert_to_xml(self):
        item = {'autocategory': ['news'],
            'date': ['Неділя, 8 квітня 2018, 18:25'],
            'tags_array': [['Росія'], ['Велика Британія']],
            'text': 'Генпрокуратура\nкерівництва.',
            'title': ['РФ обіцяє'],
            'url': ['https://www.pravda.com.ua/news/2018/04/8/7177119/']}
        expected = '<url>https://www.pravda.com.ua/news/2018/04/8/7177119/</url>\n<title>РФ обіцяє</title>\n<date>Неділя, 8 квітня 2018, 18:25</date>\n<authors></authors>\n<autocategory>news</autocategory>\n<tags><tag>Росія</tag> <tag>Велика Британія</tag> </tags>\n<body>\nГенпрокуратура\nкерівництва.\n</body>\n'
        actual = convert_to_xml(item)
        self.assertEqual(expected, actual)

    def test_01_check_path(self):
        url = 'https://www.pravda.com.ua/news/2018/04/8/7177119/'
        category = 'news'
        expected = r'www_pravda_com_ua\news\www_pravda_com_ua_news_2018_04_8_7177119.txt'
        actual = check_path(url, category)
        self.assertEqual(actual, expected)
    
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()