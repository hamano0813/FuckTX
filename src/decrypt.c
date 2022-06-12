/*
用于快速异或计算的C函数

使用MinGW-w64编译DLL
gcc decrypt.c -shared -o decrypt.dll

python中调用
from ctypes import CDLL, POINTER, byref, c_ubyte

buffer: bytes | bytearray
length = len(buffer)
c_buffer = (c_ubyte * length)(*buffer)

dll = CDLL('./decrypt')
dll.iter_xor.restype = POINTER(c_ubyte)
p_buffer = bytes(dll.iter_xor(byref(c_buffer), length, xor)[:length])
*/

unsigned char *iter_xor(unsigned char *iter, int length, unsigned char xor_val)
{
    for (int i = 0; i < length; i++)
    {
        *(iter + i) ^= xor_val;
    }
    return iter;
}
