
import os, time
from threading import Lock, Thread
import ctypes
from ctypes import byref, POINTER, cast, sizeof, memset

import pandas as pd
import numpy as np

import platform
if platform.system() == "Linux":
    hikpath = "HikSDK_lin"

if platform.system() == "Windows":
    hikpath = "HikSDK_win"

import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), hikpath))
import MvCameraControl_class as hiksdk

_lock_name_to_lock = {}

class Camera(hiksdk.MvCamera):
    
    def __ip2int(self, ip):
        return sum([int(s) << shift for s, shift in zip(ip.split("."), [24, 16, 8, 0])])

    def __int2ip(self, i):
        return f"{(i & 0xff000000) >> 24}.{(i & 0x00ff0000) >> 16}.{(i & 0x0000ff00) >> 8}.{i & 0x000000ff}"

    def __find_ip(self):
        deviceList = hiksdk.MV_CC_DEVICE_INFO_LIST()
        tlayerType = hiksdk.MV_GIGE_DEVICE
        assert not hiksdk.MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if deviceList.nDeviceNum > 0:
            mvcc_dev_info = cast(deviceList.pDeviceInfo[0], POINTER(hiksdk.MV_CC_DEVICE_INFO)).contents
            ip = self.__int2ip(mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp)
        else:
            ip = None
        return ip

    def __get_host_ip(self, target_ip):
        import socket
        return [(s.connect((target_ip, 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    def __create_camera_handle(self):
        stDevInfo = hiksdk.MV_CC_DEVICE_INFO()
        stGigEDev = hiksdk.MV_GIGE_DEVICE_INFO()

        stGigEDev.nCurrentIp = self.__ip2int(self.__ip)
        stGigEDev.nNetExport = self.__ip2int(self.__host_ip)
        stDevInfo.nTLayerType = hiksdk.MV_GIGE_DEVICE
        stDevInfo.SpecialInfo.stGigEInfo = stGigEDev
        assert not self.MV_CC_CreateHandle(stDevInfo)
        a = 0

    def MV_CC_CreateHandle(self, mvcc_dev_info):
        self.mvcc_dev_info = mvcc_dev_info
        self.__ip = self.__int2ip(mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp)
        assert not super().MV_CC_CreateHandle(mvcc_dev_info)

    def __get_setting_df():
        
        data = pd.read_csv(os.path.join(os.path.dirname(__file__), hikpath + "/MvCameraNode-CH.csv"))
        setting_df = pd.DataFrame()

        def to_key(key):
            if "[" in key:
                key = key[: key.index("[")]
            return key.strip()

        def get_depend(key):
            key = key.strip()
            if "[" in key:
                return key[key.index("[") + 1 : -1]
            return ""

        setting_df["key"] = data[list(data)[1]].map(to_key)
        setting_df["depend"] = data[list(data)[1]].map(get_depend)
        setting_df["dtype"] = data[list(data)[2]].map(lambda x: x.strip().lower())
        return setting_df

    high_speed_lock = Lock()
    setting_df = __get_setting_df()

    def __get_frame_to_buf(self):
        with self.__lock:
            assert not self.MV_CC_SetCommandValue("TriggerSoftware")
            assert not self.MV_CC_GetOneFrameTimeout(
                byref(self.data_buf),
                self.nPayloadSize,
                self.stFrameInfo,
                self.TIMEOUT_MS,
            ), self.__ip
        self.last_time_get_frame = time.time()

    def __get_configured_frame(self):
        config = self.__config if self.__config else {}
        lock_name = config.get("lock_name")
        lock = (
            _lock_name_to_lock[lock_name]
            if lock_name in _lock_name_to_lock
            else _lock_name_to_lock.setdefault(lock_name, Lock())
        )
        repeat_trigger = config.get("repeat_trigger", 1)
        with lock:
            for i in range(repeat_trigger):
                self.__get_frame_to_buf()

    def __set_item(self, key, value):
        df = self.setting_df
        dtype = df[df.key == key]["dtype"].iloc[0]
        if dtype == "iboolean":
            set_func = self.MV_CC_SetBoolValue
        if dtype == "icommand":
            set_func = self.MV_CC_SetCommandValue
        if dtype == "ienumeration":
            if isinstance(value, str):
                set_func = self.MV_CC_SetEnumValueByString
            else:
                set_func = self.MV_CC_SetEnumValue
        if dtype == "ifloat":
            set_func = self.MV_CC_SetFloatValue
        if dtype == "iinteger":
            set_func = self.MV_CC_SetIntValue
        if dtype == "istring":
            set_func = self.MV_CC_SetStringValue
        if dtype == "register":
            set_func = self.MV_CC_RegisterEventCallBackEx
        with self.__lock:
            assert not set_func(
                key, value
            ), f"{set_func.__name__}('{key}', {value}) not return 0"

    def __get_item(self, key):
        df = self.setting_df
        dtype = df[df.key == key]["dtype"].iloc[0]
        if dtype == "iboolean":
            get_func = self.MV_CC_GetBoolValue
            value = ctypes.c_bool()
        if dtype == "icommand":
            get_func = self.MV_CC_GetCommandValue
        if dtype == "ienumeration":
            get_func = self.MV_CC_GetEnumValue
            value = ctypes.c_uint32()
        if dtype == "ifloat":
            get_func = self.MV_CC_GetFloatValue
            value = ctypes.c_float()
        if dtype == "iinteger":
            get_func = self.MV_CC_GetIntValue
            value = ctypes.c_int()
        if dtype == "istring":
            get_func = self.MV_CC_GetStringValue
            value = (ctypes.c_char * 50)()
        if dtype == "register":
            get_func = self.MV_CC_RegisterEventCallBackEx
        with self.__lock:
            assert not get_func(
                key, value
            ), f"{get_func.__name__}('{key}', {value}) not return 0"
        return value.value

    __getitem__ = __get_item
    __setitem__ = __set_item

    def __setup(self):
        try:
            self.pixel_format = "RGB8Packed"
            self.__set_item("PixelFormat", self.pixel_format)
        except AssertionError:
            pass
        self.__set_item("ExposureAuto", "Continuous")

    def __del__(self):
        self.MV_CC_DestroyHandle()

    def __init__(self, ip=None, host_ip=None):

        super().__init__()
        self.__lock = Lock()
        self.TIMEOUT_MS = 40000
        if ip is None:
            ip = self.__find_ip()
        if host_ip is None:
            host_ip = self.__get_host_ip(ip)

        self.__ip = ip
        self.__host_ip = host_ip
        #
        self.__setting_items = None
        self.__config = None
        #
        self.__create_camera_handle()
        self.__is_opened = False
        self.__last_time_get_frame = 0

    def open(self):
        assert not self.MV_CC_OpenDevice(hiksdk.MV_ACCESS_Exclusive, 0)

        self.__set_item("TriggerMode", hiksdk.MV_TRIGGER_MODE_ON)
        self.__set_item("TriggerSource", hiksdk.MV_TRIGGER_SOURCE_SOFTWARE)
        self.__set_item("AcquisitionFrameRateEnable", False)

        self.__setup()
        if self.__setting_items is not None:
            if isinstance(self.__setting_items, dict):
                self.__setting_items = self.__setting_items.values()
            for key, value in self.__setting_items:
                self.__set_item(key, value)

        stParam = hiksdk.MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(hiksdk.MVCC_INTVALUE))

        assert not self.MV_CC_GetIntValue("PayloadSize", stParam)
        self.nPayloadSize = stParam.nCurValue
        self.data_buf = (ctypes.c_ubyte * self.nPayloadSize)()

        self.stFrameInfo = hiksdk.MV_FRAME_OUT_INFO_EX()
        memset(byref(self.stFrameInfo), 0, sizeof(self.stFrameInfo))

        assert not self.MV_CC_StartGrabbing()
        self.__is_opened = True
        #return self

    def close(self):
        self.__set_item("TriggerMode", hiksdk.MV_TRIGGER_MODE_OFF)
        self.__set_item("AcquisitionFrameRateEnable", True)
        assert not self.MV_CC_StopGrabbing()
        self.MV_CC_CloseDevice()

        self.__is_opened = False

    def set_exposure(self, t):
        assert not self.MV_CC_SetEnumValueByString("ExposureAuto", "Off")
        assert not self.MV_CC_SetFloatValue("ExposureTime", t)

    def get_frame(self):
        stFrameInfo = self.stFrameInfo

        self.__get_configured_frame()

        h, w = stFrameInfo.nHeight, stFrameInfo.nWidth
        self.bit = bit = self.nPayloadSize * 8 // h // w
        self.shape = h, w
        if bit == 8:
            img = np.array(self.data_buf).copy().reshape(*self.shape)
        elif bit == 24:
            self.shape = (h, w, 3)
            img = np.array(self.data_buf).copy().reshape(*self.shape)
        elif bit == 16:
            raw = np.array(self.data_buf).copy().reshape(h, w, 2)
            img = raw[..., 1].astype(np.uint16) * 256 + raw[..., 0]
        elif bit == 12:
            self.shape = h, w
            arr = np.array(self.data_buf).copy().astype(np.uint16)
            arr2 = arr[1::3]
            arrl = (arr[::3] << 4) + ((arr2 & ~np.uint16(15)) >> 4)
            arrr = (arr[2::3] << 4) + (arr2 & np.uint16(15))

            img = np.concatenate([arrl[..., None], arrr[..., None]], 1).reshape(
                self.shape
            )
        return img

if __name__ == '__main__':
    
    import cv2 

    cam = Camera()
    cam.open()
    #cv2.namedWindow("test")
    frame = cam.get_frame()
    cv2.imwrite("test1.jpg", frame)
    #cv2.waitKey(0)
    cam["ExposureAuto"] = "Off"
    cam["ExposureTime"] = 9999320
    cam.set_exposure(9999320)
    frame = cam.get_frame()
    cv2.imwrite("test2.jpg", frame)

    cam.close()
    