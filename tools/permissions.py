import os
import sys
import stat


IS_WINDOWS = sys.platform.startswith("win")

class PermissionModel:
    UNIX_FLAGS = [
        ("owner_read",   stat.S_IRUSR, 0o400),
        ("owner_write",  stat.S_IWUSR, 0o200),
        ("owner_exec",   stat.S_IXUSR, 0o100),
        ("group_read",   stat.S_IRGRP, 0o040),
        ("group_write",  stat.S_IWGRP, 0o020),
        ("group_exec",   stat.S_IXGRP, 0o010),
        ("other_read",   stat.S_IROTH, 0o004),
        ("other_write",  stat.S_IWOTH, 0o002),
        ("other_exec",   stat.S_IXOTH, 0o001),
    ]

    WIN_FLAGS = [
        ("readonly", stat.FILE_ATTRIBUTE_READONLY if hasattr(stat, "FILE_ATTRIBUTE_READONLY") else 0x1),
        ("hidden",   stat.FILE_ATTRIBUTE_HIDDEN   if hasattr(stat, "FILE_ATTRIBUTE_HIDDEN")   else 0x2),
        ("system",   stat.FILE_ATTRIBUTE_SYSTEM   if hasattr(stat, "FILE_ATTRIBUTE_SYSTEM")   else 0x4),
        ("archive",  stat.FILE_ATTRIBUTE_ARCHIVE  if hasattr(stat, "FILE_ATTRIBUTE_ARCHIVE")  else 0x20),
    ]


def read_permissions(path: str) -> dict:
    st = os.stat(path)
    mode = st.st_mode

    unix = {}
    for name, bit, _ in PermissionModel.UNIX_FLAGS:
        unix[name] = bool(mode & bit)

    result = {
        "mode_octal": format(mode & 0o777, "03o"),
        "unix": unix,
        "win": {},
        "is_windows": IS_WINDOWS,
    }

    if IS_WINDOWS:
        attrs = getattr(st, "st_file_attributes", 0)
        for name, flag in PermissionModel.WIN_FLAGS:
            result["win"][name] = bool(attrs & flag)

    return result


def apply_permissions(path: str, unix_flags: dict = None,
                      win_flags: dict = None) -> None:
    if not IS_WINDOWS and unix_flags is not None:
        mode = 0
        for name, _, oct_val in PermissionModel.UNIX_FLAGS:
            if unix_flags.get(name):
                mode |= oct_val
        os.chmod(path, mode)
        return

    if IS_WINDOWS:
        if win_flags is not None and "readonly" in win_flags:
            try:
                current = os.stat(path).st_mode
                if win_flags["readonly"]:
                    os.chmod(path, current & ~stat.S_IWRITE)
                else:
                    os.chmod(path, current | stat.S_IWRITE)
            except OSError:
                pass

        if win_flags is not None:
            _apply_windows_attributes(path, win_flags)


def _apply_windows_attributes(path: str, win_flags: dict) -> None:
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return

    kernel32 = ctypes.windll.kernel32
    SetFileAttributesW = kernel32.SetFileAttributesW
    SetFileAttributesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
    SetFileAttributesW.restype = wintypes.BOOL
    GetFileAttributesW = kernel32.GetFileAttributesW
    GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
    GetFileAttributesW.restype = wintypes.DWORD

    INVALID = 0xFFFFFFFF
    current = GetFileAttributesW(path)
    if current == INVALID:
        return

    for name, flag in PermissionModel.WIN_FLAGS:
        current &= ~flag

    for name, flag in PermissionModel.WIN_FLAGS:
        if win_flags.get(name):
            current |= flag

    SetFileAttributesW(path, current)


def mode_to_rwx(mode_octal: str) -> str:
    try:
        mode = int(mode_octal, 8)
    except ValueError:
        return "---------"

    result = ""
    bits = [
        (0o400, "r"), (0o200, "w"), (0o100, "x"),
        (0o040, "r"), (0o020, "w"), (0o010, "x"),
        (0o004, "r"), (0o002, "w"), (0o001, "x"),
    ]
    for bit, ch in bits:
        result += ch if (mode & bit) else "-"
    return result