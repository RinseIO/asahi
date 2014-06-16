import unittest, sys, os
from django.conf import settings


if __name__ == '__main__':
    settings.configure(
        ELASTICSEARCH_URL='http://localhost:9200',
    )

    # extend libs
    base_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.extend([
        base_dir,
        os.path.join(base_dir, 'submodules', 'couchdbkit'),
        os.path.join(base_dir, 'submodules', 'elasticsearch-py'),
    ])

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
