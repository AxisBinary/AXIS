from flask import Flask, jsonify, send_file
import platform
import psutil
import socket
import datetime
import GPUtil
import cpuinfo
import ctypes
import os

app = Flask(__name__)

def get_drive_type_windows(mountpoint):
    """Detect drive type (SSD/HDD) on Windows"""
    try:
        drive_letter = mountpoint[:2]  # Get 'C:' from 'C:\\'
        kernel32 = ctypes.windll.kernel32
        buf = ctypes.create_string_buffer(1024)
        flags = ctypes.c_ulong()
        
        if kernel32.GetVolumeInformationA(
            ctypes.c_char_p(drive_letter.encode()),
            None, 0,
            None, ctypes.byref(flags), None,
            None, 0
        ):
            if flags.value & 0x00000020:  # FILE_FLASH_SSD
                return "SSD"
            return "HDD"
    except Exception:
        pass
    return "Unknown"

def get_system_specs():
    # CPU Info
    cpu_info = cpuinfo.get_cpu_info()
    cpu_model = cpu_info.get('brand_raw', 'Unknown CPU')
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    
    # Memory Info
    memory = psutil.virtual_memory()
    memory_total = round(memory.total / (1024 ** 3), 1)
    memory_used = round(memory.used / (1024 ** 3), 1)
    memory_percent = memory.percent
    
    # Storage Info
    storage_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = round(usage.total / (1024 ** 3), 1)
            used_gb = round(usage.used / (1024 ** 3), 1)
            free_gb = round(usage.free / (1024 ** 3), 1)
            
            drive_type = "Unknown"
            if platform.system() == "Windows":
                drive_type = get_drive_type_windows(partition.mountpoint)
            
            storage_info.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'type': drive_type,
                'total': total_gb,
                'used': used_gb,
                'free': free_gb,
                'percent': usage.percent
            })
        except Exception as e:
            print(f"Error reading partition {partition.mountpoint}: {e}")
    
    # Get primary storage (usually C: on Windows)
    primary_storage = storage_info[0] if storage_info else {
        'type': 'Unknown',
        'total': 0,
        'used': 0,
        'free': 0,
        'percent': 0
    }
    
    # Network Info
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    net_info = psutil.net_if_stats()
    net_adapter = list(net_info.keys())[0] if net_info else "Unknown"
    net_speed = net_info[net_adapter].speed if net_adapter in net_info else 0
    
    # GPU Info
    gpus = GPUtil.getGPUs()
    gpu_info = {}
    if gpus:
        gpu = gpus[0]
        gpu_info = {
            'model': gpu.name,
            'vram': f"{gpu.memoryTotal} MB",
            'core_clock': f"{gpu.load * 100}%",
            'temperature': f"{gpu.temperature}°C"
        }
    else:
        gpu_info = {
            'model': 'No GPU detected',
            'vram': 'N/A',
            'core_clock': 'N/A',
            'temperature': 'N/A'
        }
    
    # Current timestamp
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return {
        'cpu': {
            'model': cpu_model,
            'cores': cpu_cores,
            'threads': cpu_threads,
            'base_clock': f"{cpu_freq.current/1000:.1f} GHz" if cpu_freq else "N/A",
            'last_updated': now
        },
        'memory': {
            'total': f"{memory_total} GB",
            'type': 'DDR4',
            'speed': 'N/A',
            'used': f"{memory_used} GB ({memory_percent}%)",
            'last_updated': now
        },
        'storage': {
            'type': primary_storage['type'],
            'total': f"{primary_storage['total']} GB",
            'used': f"{primary_storage['used']} GB",
            'free': f"{primary_storage['free']} GB",
            'percent': primary_storage['percent'],
            'last_updated': now
        },
        'network': {
            'adapter': net_adapter,
            'speed': f"{net_speed} Mbps" if net_speed > 0 else "Unknown",
            'type': 'Wireless' if 'wireless' in net_adapter.lower() else 'Wired',
            'ip_address': ip_address,
            'last_updated': now
        },
        'gpu': {
            'model': gpu_info['model'],
            'vram': gpu_info['vram'],
            'core_clock': gpu_info['core_clock'],
            'temperature': gpu_info['temperature'],
            'last_updated': now
        },
        'system': {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    }

@app.route('/')
def serve_technology():
    return send_file('technology.html')

@app.route('/api/specs')
def get_specs():
    return jsonify(get_system_specs())

if __name__ == '__main__':
    app.run(debug=True)