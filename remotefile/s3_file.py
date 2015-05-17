from remotefile.remote_file import RemoteFile

import os, re, logging, glob

import boto.s3 as s3
from boto.utils import get_instance_metadata
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
from boto.exception import S3ResponseError

class S3File(RemoteFile):
    def __init__(self, url, cache_dir='/tmp/s3', region_name=None):
        self.url = url
        self.region_name = self.__get_region_name(region_name)
        self.cache_dir = cache_dir
        self.local_path = self.get_local_path()

    def get_local_path(self):
        return os.path.join(self.cache_dir, self.region_name, self.url.netloc, re.sub('^/', '', self.url.path))

    def exists(self):
        return self.__get_s3_object() != None

    def download(self):
        self.mkdir_p()
        obj = self.__get_s3_object()
        if obj == None: return False
        with open(self.local_path, 'wb') as f:
            obj.get_contents_to_file(f, cb=lambda current, total: logging.info('Downloading {} ({:d}/{:d})'.format(self.local_path, current, total)))
        logging.info('Downloading {} has been completed.'.format(self.local_path))
        return True

    def upload(self, src, dir_path=False):
        key = Key(self.__get_s3_bucket())
        if dir_path:
            key.key = re.sub('/?$', '/', self.url.path) + os.path.basename(src.get_file_path())
        else:
            key.key = self.url.path
        key.set_contents_from_filename(src.get_file_path())
        return True

    def __get_region_name(self, region_name):
        if region_name == None: region_name = self.__get_region_name_using_metadata()
        if region_name == None: raise Exception('Region name is required! Please use region option (--region <region name>).')
        return region_name

    def __get_s3_instance(self):
        return s3.connect_to_region(self.region_name, calling_format=OrdinaryCallingFormat())

    def __get_s3_bucket(self):
        return self.__get_s3_instance().get_bucket(self.url.netloc)

    def __get_s3_object(self):
        try:
            return self.__get_s3_bucket().get_key(self.url.path)
        except S3ResponseError as err:
            logging.info('Returns error from S3 for {}. {}'.format(self.url.geturl(), err))

    def __get_region_name_using_metadata(self):
        return get_instance_metadata(timeout=1, num_retries=2).get('placement', {}).get('availability-zone')
