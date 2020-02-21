import unittest
import warnings

from spacer import tasks


@unittest.skip
class TestDeploy(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        pass

    @unittest.skip
    def test_deploy_simple(self):

        payload = {
            'bucketname': 'coralnet-beijbom-dev',
            'im_url': 'https://coralnet-beijbom-dev.s3-us-west-2.amazonaws.com/media/images/04yv0o1o88.jpg',
            'modelname': 'vgg16_coralnet_ver1',
            'rowcols': [[100, 100], [200, 200]],
            'model': 'media/classifiers/15.model',
        }

        results = tasks.deploy(payload)
        self.assertEqual(results['ok'], 1)

        storage = storage_factory(payload.storage_type, payload.bucketname)

    @unittest.skip
    def test_deploy_error(self):

        payload = {
            'bucketname': 'coralnet-beijbom-dev',
            'im_url': 'https://nothing_here.jpg',
            'modelname': 'vgg16_coralnet_ver1',
            'rowcols': [[100, 100], [200, 200]],
            'model': 'media/classifiers/15.model',
        }

        results = tasks.deploy(payload)
        self.assertEqual(results['ok'], 0)


if __name__ == '__main__':
    unittest.main()