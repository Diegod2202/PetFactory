"""
Memory Reader Module
Handles all Windows API calls and memory reading operations for Origin.exe processes
"""
import ctypes
from ctypes import wintypes

# Windows API constants
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]


class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", wintypes.HMODULE),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260)
    ]


kernel32 = ctypes.windll.kernel32


def get_all_process_ids(process_name):
    """
    Get all PIDs for a specific process name
    
    Args:
        process_name (str): Name of the process (e.g., "Origin.exe")
    
    Returns:
        list: List of process IDs (PIDs)
    """
    pids = []
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == -1:
        return pids
    
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    if kernel32.Process32First(snapshot, ctypes.byref(pe32)):
        while True:
            if pe32.szExeFile.decode('ascii', errors='ignore').lower() == process_name.lower():
                pids.append(pe32.th32ProcessID)
            if not kernel32.Process32Next(snapshot, ctypes.byref(pe32)):
                break
    
    kernel32.CloseHandle(snapshot)
    return pids


def get_module_base_address(pid):
    """
    Get base address of the main module for a process
    
    Args:
        pid (int): Process ID
    
    Returns:
        int: Base address of the module, or 0 if failed
    """
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    if snapshot == -1:
        return 0
    
    me32 = MODULEENTRY32()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32)
    
    base_addr = 0
    if kernel32.Module32First(snapshot, ctypes.byref(me32)):
        base_addr = ctypes.cast(me32.modBaseAddr, ctypes.c_void_p).value
    
    kernel32.CloseHandle(snapshot)
    return base_addr


def read_player_name(pid, base_address):
    """
    Read player name from memory
    
    Args:
        pid (int): Process ID
        base_address (int): Base address of the module
    
    Returns:
        str: Player name or error message
    """
    handle = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not handle:
        return "[Access Denied]"
    
    # Offset from CheatEngine
    offset = 0x11B6158
    address = base_address + offset
    
    buffer = ctypes.create_string_buffer(256)
    bytes_read = ctypes.c_size_t(0)
    
    name = "[Unable to read]"
    if kernel32.ReadProcessMemory(handle, ctypes.c_void_p(address), buffer, 256, ctypes.byref(bytes_read)):
        try:
            name = buffer.value.decode('ascii', errors='ignore').strip('\x00')
        except:
            pass
    
    kernel32.CloseHandle(handle)
    return name if name else "[Unable to read]"
