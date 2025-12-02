# -*- coding: utf-8 -*-
"""
Encoding Fix for Windows Console
Fixes Unicode encoding issues on Windows systems
"""
import sys
import io
import locale


def setup_console_encoding():
    """
    Setup proper UTF-8 encoding for Windows console
    This fixes UnicodeEncodeError when printing Unicode characters
    """
    if sys.platform == 'win32':
        try:
            # Wrap stdout and stderr with UTF-8 encoding
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
            
            # Set console code page to UTF-8
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleOutputCP(65001)  # UTF-8
                kernel32.SetConsoleCP(65001)  # UTF-8
            except:
                pass
            
            return True
        except Exception as e:
            print(f"Warning: Could not setup UTF-8 encoding: {e}")
            return False
    
    return True


def safe_print(text, end='\n', flush=False):
    """
    Safely print text, handling encoding errors
    
    Args:
        text: Text to print
        end: End character (default newline)
        flush: Whether to flush immediately
    """
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII, replacing non-ASCII chars
        safe_text = str(text).encode('ascii', 'replace').decode('ascii')
        print(safe_text, end=end, flush=flush)


def safe_str(obj):
    """
    Safely convert object to string, handling encoding issues
    
    Args:
        obj: Object to convert to string
        
    Returns:
        Safe string representation
    """
    try:
        return str(obj)
    except:
        try:
            return repr(obj)
        except:
            return '<unprintable>'


# Auto-setup on import
setup_console_encoding()


if __name__ == "__main__":
    # Test encoding
    print("Testing encoding...")
    print(f"System encoding: {sys.getdefaultencoding()}")
    print(f"Stdout encoding: {sys.stdout.encoding}")
    print(f"Locale encoding: {locale.getpreferredencoding()}")
    
    # Test Unicode
    try:
        print("Testing Unicode: Đăng nhập vào X")
        print("✅ UTF-8 encoding is working!")
    except UnicodeEncodeError as e:
        print(f"❌ Encoding error: {e}")
        print("Using safe fallback...")
        safe_print("Testing Unicode: Dang nhap vao X")

