# -*- coding:utf-8 -*-

import os
import sys
import time
import shutil
import logging
import multiprocessing

#测试后，时间要改回2*60*60
#测试后改回时间20190520
TIME_INTERVAL = 2*60*60  #两小时
START_TIME = "20190520"
# VIDEOS_ORIGINAL_PATH = r"/home/8T-Disk/yzfbscc/yxsz/CCTV-13新闻"
# VIDEOS_TARGET_PATH = r"/media/fbscc/weixing/573"
CHANNEL_ID = 3694

###########测试用，正式运行请注释掉5行
# TIME_INTERVAL = 5  #n秒
# START_TIME = "20190517"  #正式测试需要注释这行
VIDEOS_ORIGINAL_PATH = r"/home/wjl/Desktop/07-CCTV-13"
VIDEOS_TARGET_PATH = r"/home/wjl/Desktop/weixing/573"
# CHANNEL_ID = 3694
##########注释到这里


logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("./auto_copy_script_log%s.txt"%(time.strftime("%Y-%m-%d", time.localtime() )))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def print_ts(messg):
    print("[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), messg))
    logger.info(messg)

class auto_copy(object):
    def __init__(self, original_path=VIDEOS_ORIGINAL_PATH, target_path=VIDEOS_TARGET_PATH, time_interval=TIME_INTERVAL):
        self.original_path = original_path
        self.target_path = target_path
        self.videos_name_path = []
        self.copy_flag = True
        self.time_interval = time_interval
        self.copied_video = []

    #定义延时模块
    #这里有问题
    def timer(self):
        try:
            # sleep for the remaining seconds of TIME_INTERVAL
            # time_remaining = self.time_interval - time.time()%self.time_interval
            time_remaining = self.time_interval
            print_ts("Sleeping until %s (remaining %s seconds)..."\
                     %((time.ctime(time.time()+time_remaining)), time_remaining)
                     )
            time.sleep(time_remaining)
            # print_ts("Starting copy.")
            self.copy_flag= True

            # execute the command
            # status = os.system(command)
        except Exception as e:
            print_ts("ERROR_INFO", e)

    def make_store_path(self, abs_video_name_path):
        # dir, strfile = os.path.split(abs_video_name_path)
        _list = abs_video_name_path.split("/")[-2:]
        _y, _m, _d = _list[0].split("-")

        # VIDEOS_TARGET_PATH = "/media/fbscc/weixing/573/年月/日/channel_id/视频名.mp4"
        _path_right =  "/" + _y + _m + "/" + _d + "/" +str(CHANNEL_ID) + "/" + _list[1]
        # print("--------------self.target_path%s"%self.target_path)  #4test
        return self. target_path + _path_right

    def check_video_exist(self):
        """在每次拷贝前查找本地是否已经有了视频"""
        # for dirpath, dirnames, filenames in os.walk(self.target_path):
        #     print("========dirpath", dirpath)
        #     print("********dirnames", dirnames)
        #     print("--------filenames", filenames)

        #先遍历一遍目标文件夹中的视频
        _temp_exit_video_list = []
        for dir in os.walk(self.target_path):
            print("========dir", dir)
            if dir[-1]:
                for i in dir[-1]:
                    _temp_exit_video_list.append(dir[0]+"/"+i)

        print("final++++", _temp_exit_video_list)  #4test

        #保存要删除的视频路径
        _videopath_to_delete_list = []
        for i in self.videos_name_path:
            # print("----",self.make_store_path(i))
            if self.make_store_path(i) in _temp_exit_video_list:
                _videopath_to_delete_list.append(i)
            # else: 4test
            #     print("else ",  _temp_exit_video_list)  #4test
            #     print("else ", self.make_store_path(i))  #4test

        # print("~~~~~", _videopath_to_delete_list)  #4test

        for j in _videopath_to_delete_list:
            self.videos_name_path.remove(j)
            # print("已经存在的视频", j)  #4test


    def copy_fun(self):
        #先检查要拷贝的视频是否已经存在
        self.check_video_exist()

        _temp_path = self.videos_name_path[0]
        # #先判断是不是MP4等视频格式的路径
        # if _temp_path.rfind(".mp4") >= 0  \
        #         or _temp_path.rfind(".mpeg") >= 0 \
        #         or _temp_path.rfind(".mpeg") >= 0 :
            #调用下自己的方法
        store_path = self.make_store_path(_temp_path)
        print_ts(" 源文件的绝对路径:{}".format(_temp_path))  #4test
        print_ts("存放文件的绝对路径:{}".format(store_path))  #4test
        #拷贝文件

        _dir, _fname = os.path.split(store_path)
        if not os.path.exists(_dir):
            print_ts("要创建文件的绝对路径:%s"%store_path)  #4test
            try:
                os.makedirs(_dir)
            except FileExistsError:
                pass
            except Exception as err:
                print_ts("创建文件路径时候的错误%s"%err)

        try:
            shutil.copy(_temp_path, store_path)
        except Exception as err:
            print_ts("拷贝文件时候的错误%s"%err)
        # else:
        #     #视频存放格式只有.mp4 .mpeg .ts三种
        #     #不是这三种，在删了非视频的文件路径
        #     self.videos_name_path.remove(_temp_path)
        #     print("删除的非视频文件是：",_temp_path)

        # print_ts("Starting copy.")
        # self.copied_video.append("filename")
        self.videos_name_path.pop(0)
        self.copy_flag = False
        print_ts("Finished copy.")

    def chek_date_in_0601_to_0607(self, str_path):
        """对输入的地址判断日期是否在6月1日到7日之间"""
        star_date_time = 20180601
        end__date_time = 20180607
        #切出来日期字符串
        str_path = str_path.split("/")[-1]
        str_path = "".join(str_path.split("-"))
        #返回格式如20180601，int格式
        data_int = int(str_path)

        if data_int >=star_date_time and data_int <= end__date_time:
            return True
        return False

    def get_videos_list(self):
        if not os.path.exists(self.original_path):
            print("视频源文件夹不存在")
        else:
            for dirpath, dirnames, filenames in os.walk(self.original_path):
                for filename in filenames:
                    # print("filenames",filenames)
                    # print(dirpath)
                    # print(dirnames)
                    #判断下是否在指定日期里
                    # print_ts("dirpath%s"%dirpath)
                    # print_ts("result", self.chek_date_in_0601_to_0607(dirpath))
                    if self.chek_date_in_0601_to_0607(dirpath):
                        #判断是不是指定的文件类型（.mpeg .ts .mp4)
                        if filename.rfind(".mp4") >= 0 \
                                or filename.rfind(".mpeg") >= 0 \
                                or filename.rfind(".ts") >= 0 :

                            self.videos_name_path.append(dirpath + '/' + filename)
                            # print_ts("filename", filename)  #4tst

        # for i in self.videos_name_path:
        #     print_ts(i)

        #增加按照日期排序功能
        def date_int(date_str):
            return int(date_str.split("/")[-1][:8] + date_str.split("/")[-1][9:15])
        self.videos_name_path.sort(key=date_int, reverse= False)

        for i in self.videos_name_path:
            print_ts(i)  #4test

    def start(self):
        #先遍历目标文件夹,生成viedos清单
        self.get_videos_list()

        while True:
            time_now = time.strftime("%Y%m%d", time.localtime())  #本地时间
            #内部文件计数
            _filenum = 0
            #本地日期大于等于指定日期开始执行,并且列表里有地址时候
            if int(time_now) >= int(START_TIME) and self.videos_name_path:
                self.copy_fun()
                _filenum += 1
                # while True and self.videos_name_path:
                #列表中有地址时复制
                while self.videos_name_path:
                   #延时默认时间
                    self.timer()
                    if self.copy_flag:
                        self.copy_fun()
                        _filenum += 1
                        print_ts("拷贝完成第%d个视频"%_filenum)
                else:
                    print_ts("全部%s个视频复制完毕"%_filenum)
                    sys.exit()

            elif int(time_now) < int(START_TIME):
                print_ts("现在是%s,脚本开始执行日期%s"%(time_now, START_TIME))
                #每隔两秒判断一次本地时间
                time.sleep(5)



if __name__ == "__main__":

    auto_copy = auto_copy()
    auto_copy.start()

    #
    # auto_copy.get_videos_list()
    # auto_copy.check_video_exist()
    # auto_copy.get_videos_list()
