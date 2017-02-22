# coding:utf-8
from date_utils import get_cur_time


class Media:
    """
    主要用来管理上传的资源
    """

    def __init__(self, default_config):
        self.collection = default_config['UPDATE_INFO']

    def get_all(self):
        cursor = self.collection.find()
        for item in cursor:
            pass

    def set_img_info(self, address, img_filename, describe):
        """
        保存用户上传的图片信息
        :return:
        """
        cur_time = get_cur_time()
        tt = dict()
        tt['optime'] = cur_time
        tt['address'] = address
        tt['filename'] = img_filename
        tt['describe'] = describe
        self.collection.insert(tt)
