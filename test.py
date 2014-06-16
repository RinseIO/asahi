import unittest
from django.conf import settings


if __name__ == '__main__':
    settings.configure(
        ELASTICSEARCH_URL='http://localhost:9200',
    )

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
