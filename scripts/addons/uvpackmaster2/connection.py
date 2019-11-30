
import struct
import io
import time

from .utils import *


def force_read_bytes(stream, bytes_cnt):
    output = bytes()

    while len(output) != bytes_cnt:
        buf = stream.read(bytes_cnt - len(output))

        if len(buf) == 0:
            raise RuntimeError('Not enough output from the UVP process')

        output += buf

    return output


def force_read_int(stream):
    buf = force_read_bytes(stream, 4)
    return struct.unpack('i', buf)[0]


def force_read_float(stream):
    buf = force_read_bytes(stream, 4)
    return struct.unpack('f', buf)[0]


def force_read_ints(stream, count):
    buf = force_read_bytes(stream, 4 * count)
    return struct.unpack('i' * count, buf)


def force_read_floats(stream, count):
    buf = force_read_bytes(stream, 4 * count)
    return struct.unpack('f' * count, buf)


def read_int_array(stream):
    count = force_read_int(stream)
    return force_read_ints(stream, count)


def connection_rcv_message(stream):
    msg_size = force_read_int(stream)
    msg_bytes = force_read_bytes(stream, msg_size)
    return io.BytesIO(msg_bytes)


def connection_thread_func(stream, queue):
    try:
        while True:
            queue.put(connection_rcv_message(stream))
    except Exception as ex:
        return