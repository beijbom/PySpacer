"""
This file provides scripts for
1) listing all extracted data in spacer-trainingdata bucket.
2) Re-train a classifier and compared to performance on CoralNet

To use do:

python classifier_training_regression.py list

python classifier_training_regression.py source_id ~/tmp_folder

where source_id is an integer defining which source to train.
"""


import json
import os

import fire

import warnings

from spacer import config
from scripts.regression.utils import build_traindata, \
    start_training, \
    cache_local


class ClassifierRegressionTest:
    """
    This runs a training on exported features from CoralNet.
    It assumes read permission on the "spacer-trainingdata" bucket.

    All data is formatted per the management command in
    https://github.com/beijbom/coralnet/blob/107257fd34cd2c16714b369ec7146ae7222af2c6/project/vision_backend/management/commands/vb_export_spacer_data.py
    ...
    """
    @staticmethod
    def train(source_id: int,
              local_path: str,
              n_epochs: int = 5,
              export_name: str = 'beta_export',
              clf_type: str = 'MLP') -> None:

        # Sci-kit learns calibration step throws out a ton of warnings.
        # That we don't need to see here.
        warnings.simplefilter('ignore', RuntimeWarning)
        config.filter_warnings()

        source_root = os.path.join(local_path, 's{}'.format(source_id))
        image_root = os.path.join(source_root, 'images')

        # Download all data to local.
        # Train and eval will run much faster that way...
        print('-> Downloading data for source id: {}.'.format(source_id))
        cache_local(source_root, image_root, export_name, source_id,
                    cache_image=False, cache_feats=True)

        # Build traindata
        print('-> Assembling train and val data for source id: {}'.format(
            source_id))
        train_labels, val_labels = build_traindata(image_root)

        # Perform training
        print("-> Training...")
        start_training(source_root, train_labels, val_labels, n_epochs, clf_type)

    @staticmethod
    def list(export_name: str = 'beta_export') -> None:
        """ Lists sources available in export. """

        conn = config.get_s3_conn()
        bucket = conn.get_bucket('spacer-trainingdata', validate=True)

        source_keys = bucket.list(prefix='{}/s'.format(export_name),
                                  delimiter='images')
        meta_keys = [key for key in source_keys if key.name.endswith('json')]
        meta_keys.sort(key=lambda key: int(key.name.split('/')[1][1:]))

        header_format = '{:>30}, {:>4}, {:>6}, {}\n{}'
        print(header_format.format('Name', 'id', 'n_imgs', 'acc (%)', '-'*53))
        entry_format = '{:>30}, {:>4}, {:>6}, {:.1f}%'

        for meta_key in meta_keys:
            md = json.loads(meta_key.get_contents_as_string().decode('UTF-8'))

            if not'pk' in md:
                # One source "Mestrado" was deleted before we could
                # refresh the export metadata. So get pk from the path.
                print(entry_format.format(
                    md['name'][:20],
                    meta_key.name.split('/')[1][1:],
                    md['nbr_confirmed_images'], 0) + ' Old metadata!!')
            else:
                print(entry_format.format(
                    md['name'][:20],
                    md['pk'],
                    md['nbr_confirmed_images'],
                    100*float(md['best_robot_accuracy'])))


if __name__ == '__main__':
    fire.Fire(ClassifierRegressionTest)
