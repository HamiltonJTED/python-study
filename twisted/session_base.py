#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#from twisted.internet.protocol import ClientCreator, Protocol
from twisted.internet.protocol import Protocol  
import struct
import logging
import uuid

def pack_splitter(bytestream):
    """
    """
    next_index = 0
    remaining_len = len(bytestream)
    while remaining_len >= 24:
        obf = struct.unpack('!I2H16s',bytestream[next_index:next_index+24])
        # get body_size
        body_size = obf[0]
        if remaining_len < 24 + body_size:
            raise StopIteration
        current_index = next_index
        next_index = next_index + 24 + body_size
        package_stream = bytestream[current_index:next_index]
        yield next_index, package_stream
        remaining_len = remaining_len - 24 - body_size
    raise StopIteration

class SessionBase(Protocol):
    """Once connected, send a message, then print the result."""
    def __init__(self):
        self.connectcnt_ = 0
        self._remaining = '' 
        
    def SendCmdDataCustmer(self, sys_type, pack_type, pb_obj = None, request_id = None):
        '''
        @sys_type:系统区号
        @pack_type:包子类型
        @request_id:请求ID
        @pb_obj:pb对象
        '''
        format='!I2H16s'
        if not request_id:
            request_id = uuid.uuid1().bytes
        body_len = 0
        body = ''
        if pb_obj:
            body = pb_obj.SerializeToString()
            body_len = len(body)
        buffer = struct.pack(format, body_len, sys_type, pack_type, request_id)
        if body_len > 0:
            buffer = buffer + body
        self.transport.write(buffer)
        
    def HeartBeat(self, system_type = 0):#心跳包应答
        self.SendCmdDataCustmer(system_type, 0x8fff)
        
    def connectionMade(self):
        self.factory.sessionConnected(self)
        
    def ProcessPack(self, sysType, packType, request_id, body):
        '''
        需要在子类里面重写该方法
        '''
        
    def DealOnePack(self, data):
        '''
        '''
        obf = struct.unpack('!I2H16s',data[0:24])
        if obf[2] == 0x0fff:
            self.HeartBeat(obf[1])
        else:
            self.ProcessPack(obf[1], obf[2], obf[3], data[24:])

    def dataReceived(self, data):
        next_pos = 0
        data = self._remaining + data
        for n_pos, pack_stream in pack_splitter(data):
            next_pos = n_pos
            self.DealOnePack(pack_stream)
        self._remaining = data[next_pos:]

    def connectionLost(self, reason):
        self.factory.sessionDisconnected(self)
#        logging.error("connection lost:%s"%str(self.transport.getPeer()))
if __name__ == '__main__':
    request_id = uuid.uuid1()
    b = request_id.bytes
    i = 0
    mystr = ''
    while i < len(b):
        mystr += '%02x' % ord(b[i])
        i+=1
    print request_id
    print mystr


        

        
