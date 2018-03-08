#!/usr/bin/env python
"""
Fill in data from another channel data block
"""
import pprint
import sys
import os
import time
import csv
import numpy as np
import pandas as pd

from decisionengine.framework.modules import Source
import decisionengine.framework.dataspace.dataspace as dataspace
import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.modules.de_logger as de_logger
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.modules.load_config as load_config

RETRIES = 5
RETRY_TO = 60
PRODUCES=['Job_Limits']
must_have = ('channel_name', 'Dataproducts')

class SourceProxy(Source.Source):
    """
    Source Proxy
    Channel configuration using source proxy
    must have in parameters 'channel_name', defining foreign channel name and
    'Dataproducts', defining foreign (and optionally local) data keys.
    See consumes() doc.
    Example of source proxy configuration:
        "AWSJobLimits" : {
        "module" : "modules.source_proxy",
        "name"   : "SourceProxy",
        "parameters": {"channel_name": "channel_aws_config_data",
		      "Dataproducts":[("aws_instance_limits", "Job_Limits")],
		      "retries": 3,
		      "retry_timeout": 20,
        	      },
       	"schedule": 360,
    },

    """
    must_have = ('channel_name', 'Dataproducts')
    def __init__(self, *args, **kwargs):
        if not set(must_have).issubset(set(args[0].keys())):
            raise RuntimeError('SourceProxy misconfigured. Must have %s defined'%(must_have,))
        self.source_channel = args[0]['channel_name']
        self.data_keys = args[0]['Dataproducts']
        self.retries = args[0].get('retries', RETRIES)
        self.retry_to = args[0].get('retry_timeout', RETRY_TO)
        self.logger = de_logger.get_logger()
        config_manager = configmanager.ConfigManager()
        config_manager.load()
        global_config = config_manager.get_global_config()
        self.dataspace = dataspace.DataSpace(global_config)

    def consumes(self):
        """
        Assumes that self.datakeys has the following structure:
          is a list of tuples or singletons:
          [
          (data_product_name, data_product_name_translation),
          ....
          ]
          or
          [
          data_product_name,
          ....
          ]
        """

        l = []
        for key in self.data_keys:
            if isinstance(key, tuple):
                d = key[0]
            else:
                d = key
            l.append(d)
        return l

    def produces(self):
        """
        Assumes that self.datakeys has the following structure
          data_keys[key1] = (data_product_name, data_product_name_translation)
          ....
          or
         
          data_keys[key1] = data_product_name
          ....
        """

        l = []
        for key in self.data_keys:
            if isinstance(key, tuple):
                d = key[1]
            else:
                d = key
            l.append(d)
        return l

    def _get_data(self, data_block, key):
        while True:
            try:
                data = data_block.get(key)
                break
            except KeyError, detail:
                if data_block.generation_id > 1:
                    data_block.generation_id -= 1
                else:
                    raise KeyError, detail
        return data

    def acquire(self):
        """
        Overrides Source class method
        """
        retry_cnt = 0
        data_block = None
        while retry_cnt < self.retries:
            try:
                tm = self.dataspace.get_taskmanager(self.source_channel)
                self.logger.debug('task manager %s'%(tm,))
                if tm['taskmanager_id']:
                    # get last datablock
                    data_block = datablock.DataBlock(self.dataspace,
                                                     self.source_channel,
                                                     taskmanager_id = tm['taskmanager_id'],
                                                     sequence_id = tm['sequence_id'])
                    break
                else:
                    retry_cnt += 1
                    time.sleep(self.retry_to)
            except Exception, detail:
                self.logger.error('Error getting datablock for %s %s'%(self.source_channel, detail))

        if not data_block:
            raise RuntimeError, ('Could not get data.')
        rc = {}
        retry_cnt = 0
        filled_keys = []
        retry = True
        while retry and retry_cnt < self.retries:
            if len(filled_keys) != len(self.data_keys):
                retry = True
                for k in self.data_keys:
                    if isinstance(k, tuple):
                        k_in = k[0]
                        k_out = k[1]
                    else:
                       k_in = k
                       k_out = k
                    if k_in not in filled_keys:
                        try:
                            rc[k_out] = pd.DataFrame(self._get_data(data_block, k_in))
                            filled_keys.append(k)
                        except KeyError, detail:
                            print "KEYERROR", detail
                            retry = True
            if len(filled_keys) == len(self.data_keys):
                break
            if retry:
                # expected data is not ready yet
                retry_cnt += 1
                time.sleep(self.retry_to)
                retry = False

        if retry_cnt == self.retries and len(filled_keys) != len(self.data_keys):
            raise RuntimeError, ('Could not get all data. Expected %s Filled %s'%(self.data_keys, filled_keys))
        return rc

def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"source_proxy1": {
        "module" :  "modules.source_proxy",
        "name"   :  "SourceProxy",
                    "parameters": {
                        "channel_name": "source_channel_name",
                        "Dataproducts": "list of data keys to retrieve from source channel data",
                        "retries": "<number of retries to acquire data>",
                        "retry_timeout": "<retry timeout>"
                    },
        "schedule": 60*60,
        }
    }

    print "Entry in channel cofiguration"
    pprint.pprint(d)

def module_config_info():
    """
    print this module configuration information
    """
    print "produces: available dynamically based on configuration"
    module_config_template()



def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--configtemplate',
                        action='store_true',
                        help='prints the expected module configuration')

    parser.add_argument('--configinfo',
                        action='store_true',
                        help='prints config template along with produces and consumes info')
    args = parser.parse_args()
    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()

if __name__ == "__main__":
    main()
