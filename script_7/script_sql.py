import pymysql
import os
import socket
from pymysql.cursors import DictCursor
# from log import Logging
import logging
import time


# logfile = os.path.join('/logs', socket.gethostname(), 'video_query_db.log')
# logger = Logging(os.path.basename(__file__), logfile).logger

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("./script_database_log%s.txt"%(time.strftime("%Y-%m-%d", time.localtime() )))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class OcrDB(object):
    def __init__(self, user="root", password="123456", database="video_data_info", table="video_data_copy", host='127.0.0.1', port=3306):  # 这里的域名看数据库在哪里机器上写成哪个机器
        self.table = table
        self.connect = pymysql.connect(host=host, port=port, database=database, user=user, password=password, charset='utf8')
        self.cursor = self.connect.cursor(DictCursor)

    def ping(self):

        try:
            self.connect.ping(reconnect=True)
        except Exception as e:
            logger.error('\n ----- 数据库重连失败 {} ----- '.format(e))

    def update_vd_end(self,p_k,n_1,c_1,n_2,c_2,n_3,c_3,n_4,c_4):


        #ocr_db.update_vd_status(task_info['id'],'ocr_status',6,'counter_word',counter_word,'counter_sentence',counter_sentence,'counter_frames',counter_frames)

        self.ping()
        sql = "update ocr_status set {}={},{}={},{}={},{}={} where task_id={}".format(n_1,c_1,n_2,c_2,n_3,c_3,n_4,c_4,p_k)
        try:
            self.cursor.execute(sql)
            self.connect.commit()
            return True
        except Exception as e:
            logger.error("\n ----- 更新视频状态报错 {} ----- ".format(e))
            return False


    def update_vd_status(self, _id, status,field):

        self.ping()
        sql = "update ocr_status set {}={} where task_id={}".format(field,status,_id)
        try:
            self.cursor.execute(sql)
            self.connect.commit()
            return True
        except Exception as e:
            logger.error("\n ----- 更新视频状态报错 {} ----- ".format(e))
            return False

    def query_video_reset(self, _id):

        self.ping()
        #xiugai
        sql = "update ocr_status set ocr_status=0, data_err=data_err + 1 where task_id={}".format(_id)
        try:
            self.cursor.execute(sql)
            self.connect.commit()
            logger.info("重置 {} 视频记录成功".format(_id))
            return True
        except Exception as e:
            logger.error('\n ----- 重置 {} 视频记录错误 {} ----- '.format(_id, e))
            return False

    def query_video_and_change_status(self, channel_form):
        '''channel_form: tuple ('2222','3333', ...)
        '''
        self.ping()
        self.connect.begin()
        try:
            sql = "select * from video_data_copy where face_status=0 and chan_num in {} and data_err < 5 order by id desc limit 1 for update".format(
                str(channel_form))
            if not self.cursor.execute(sql):
                return None

            one_video_data = self.cursor.fetchone()
            sql = "update `%s` set face_status='1' where id='%s'" % (self.table, one_video_data['id'])
            self.cursor.execute(sql)

            return one_video_data

        except Exception as e:
            self.connect.rollback()
            logger.error("\n ----- 取视频报错 {} ----- ".format(e))
            return

        finally:
            self.connect.commit()

    def __del__(self):
        try:
            self.connect.close()
            logger.info("关闭数据库连接 {}".format(self.table))
        except Exception as e:
            logger.error("\n ----- 关闭数据库连接失败 {} ----- ".format(e))
            return


    def select_data_err(self,id):
        self.ping()
        try:
            sql = 'select data_err from video_face_status where task_id={}'.format(id)
            self.cursor.execute(sql)
            data_err = self.cursor.fetchone()['data_err']
            return data_err
        except Exception as e:
            logger.error("查询data_err报错，报错信息:{}".format(e))
            return

    def insert_task(self,task_info):
        # 插入
        sql = 'insert video_data_copy (date,chan_num,video_path,data_source,end_date,video_url,chan_name) values ("{}","{}","{}","{}","{}","{}","{}")' \
            .format(task_info['date'],task_info['chan_num'],task_info['video_path'],task_info['data_source'],task_info['end_date'],task_info['video_url'],task_info['chan_name'])

        print(sql)
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as e:
            logger.error('插入数据库失败，{}'.format(e))
            logger.error('插入数据库失败的信息{}'.format(sql))


if __name__ == "__main__":
    db = OcrDB()
    pass

