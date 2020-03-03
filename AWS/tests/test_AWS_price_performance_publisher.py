import os

import pandas as pd

import decisionengine_modules.AWS.publishers.AWS_price_performance as AWSPPublisher

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

expected_reply =  pd.read_csv(os.path.join(DATA_DIR,
                                           'expected_AWS_price_perf_pub.csv'))

consumes = ['AWS_Price_Performance']


def create_datablock():
    data_block = {}
    data_block['AWS_Price_Performance'] = pd.read_csv(os.path.join(DATA_DIR, 'expected_price_performance.csv'))
    return data_block


class TestAWSPPPublisher:

    def test_consumes(self):
        pp_p = AWSPPublisher.AWSPricePerformancePublisher({'publish_to_graphite': False,
                                                'graphite_host': 'fifemondata.fnal.gov',
                                                'graphite_port': 2104,
                                                'graphite_context':'hepcloud.aws',
                                                'output_file': 'AWS_price_perf_pub.csv'})

        assert pp_p.consumes() == consumes

    def test_transform(self):
        pp_p = AWSPPublisher.AWSPricePerformancePublisher({'publish_to_graphite': False,
                                                'graphite_host': 'fifemondata.fnal.gov',
                                                'graphite_port': 2104,
                                                'graphite_context':'hepcloud.aws',
                                                'output_file': 'AWS_price_perf_pub.csv'})

        data_block = create_datablock()
        pp_p.publish(data_block)
        opd = pd.read_csv('AWS_price_perf_pub.csv')
        assert opd.equals(expected_reply)

