# coding:utf-8
from blog_app.share.date_utils import get_cur_time


class Media:
    """
    主要用来管理上传的资源
    """

    def __init__(self, default_config=None):
        if default_config:
            self.collection = default_config['UPDATE_INFO']

    def init(self,default_config):
        self.collection = default_config['UPDATE_INFO']

    def get_all(self):
        cursor = self.collection.find()
        rst = []
        for item in cursor:
            tt = dict()
            tt['optime'] = item.get('optime')
            tt['status'] = item.get('status')
            tt['address'] = item.get('address')
            tt['filename'] = item.get('filename')
            tt['describe'] = item.get('describe')
            rst.append(tt)
        return rst

    def set_img_info(self, address, img_filename, describe):
        """
        保存用户上传的图片信息
        :return:
        """
        cur_time = get_cur_time()
        tt = dict()
        tt['optime'] = cur_time
        tt['status'] = 'use'
        tt['address'] = address
        tt['filename'] = img_filename
        tt['describe'] = describe
        self.collection.insert(tt)

    def update_img_status(self,):
        pass