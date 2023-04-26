#make sure this file can be imported from the root folder of the project

import tarfile, re
import os, random

destination_folder = '~/Documents/extracted/'

def extract_file(file_):
    log_id = destination_folder + str(random.randint(100000, 999999))
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    print(log_id)
    print(file_.name)
#    with tarfile.open(file_.name, 'r:gz') as tar:
#        tar.extractall(path=destination_folder)

    return log_id


def extract_cpuInfo(folder_):
    system_info = {}
    with open(folder_ + '/lscpu', 'r') as f:
        for line in f:
            if line.startswith('Architecture:'):
                system_info['Architecture'] = line.split(':')[1].strip()
            elif line.startswith('Byte Order:'):
                system_info['Byte Order'] = line.split(':')[1].strip()
            elif line.startswith('CPU(s):'):
                system_info['CPU(s)'] = int(line.split(':')[1].strip())
            elif line.startswith('Thread(s) per core:'):
                system_info['Thread(s) per core'] = int(line.split(':')[1].strip())
            elif line.startswith('Model name:'):
                system_info['Model name'] = line.split(':')[1].strip()
            elif line.startswith('CPU MHz:'):
                system_info['CPU MHz'] = float(line.split(':')[1].strip())
            elif line.startswith('Hypervisor vendor:'):
                system_info['Hypervisor vendor'] = line.split(':')[1].strip()
    return system_info


def meminfo(folder_):
    mem_info = {}

    with open(folder_ + '/free_m', 'r') as f:
        for line in f:
            if 'Mem:' in line:
                line = line.split()
                mem_info['total_mem'] = line[1]
                mem_info['used_mem'] = line[2]
                mem_info['free_mem'] = line[3]
                mem_info['available_mem'] = line[6]
            elif 'Swap:' in line:
                line = line.split()
                mem_info['swap_total'] = line[1]
                mem_info['swap_used'] = line[2]
                mem_info['swap_free'] = line[3]
    return mem_info


def uptime(folder_):
    with open(folder_ + '/uptime', 'r') as file:
        input_str = file.readline().strip()

    system_time = re.search(r'^\S+ \S+', input_str).group()
    up_time = re.search(r'up (.*?),', input_str).group(1)
    users = int(re.search(r'(\d+) user', input_str).group(1))
    load_average = re.search(r'load average: (.*)', input_str).group(1)

    return {
        'system_time': system_time,
        'up_time': up_time,
        'users': users,
        'load_average': load_average
    }

def extract_services(folder_):
    services_dict = {}
    with open(folder_ + '/gitlab_status', 'r') as f:
        for line in f:
            if line:
                words = line.split()
                if len(words) >= 2:
                    status = words[0]
                    service = words[1].rstrip(':')
                    services_dict[service] = status

    return services_dict

def failed_migrations(folder_):
    matching_lines = []
    failed_migration = []
    with open(folder_ + '/gitlab_migrations', 'r') as file:
        for line in file:
            #print(line.strip().startswith('down'))
            if line.strip().startswith('down'):
                matching_lines.append(line.rstrip('\n'))
        for x, line in enumerate(matching_lines):
            match = re.search(r'(\w+)\s+(\d+)\s+(.+)', line)
            if match:
                status, migration_id, migration_msg = match.groups()
                failed_migration.append({
                    "status": status,
                    "migration_id": migration_id,
                    "migration_msg": migration_msg
                })
    return failed_migration


def parse_df_hT_output(folder_):
    file1 = open(folder_ + '/df_hT', 'r')
    file_content = file1.read()
    file1.close()
    lines = file_content.splitlines()
    headers = lines[0].split()
    headers[6] = ' '.join(headers[6:])

    filesystems = []

    for line in lines[1:]:
        parts = line.split(maxsplit=6)
        
        if len(parts) < len(headers) - 1: 
            continue
        
        filesystem = {headers[i]: parts[i] for i in range(len(parts))}
        filesystems.append(filesystem)

    sorted_filesystems = sorted(filesystems, key=lambda x: parse_size(x['Size']), reverse=True)
    return sorted_filesystems[:5]

def parse_size(size_str):
    size = float(size_str[:-1])
    unit = size_str[-1]
    
    if unit == 'G':
        size *= 1024 
    return size



def pressure_results(folder_):
    cpu_results = {"some": {}, "full": {}}
    mem_results = {"some": {}, "full": {}}
    file1 = open(folder_ + '/pressure_cpu.txt', 'r')
    file_content = file1.read()
    file1.close()
    lines = file_content.split("\n")
    
    for line in lines:
        if not line:
            continue
        parts = line.split(" ")
        if parts[0] == "some":
            cpu_results["some"] = {
                "avg10": float(parts[1].split("=")[1]),
                "avg60": float(parts[2].split("=")[1]),
                "avg300": float(parts[3].split("=")[1]),
                "total": int(parts[4].split("=")[1])
            }

        if parts[0] == "full":
            cpu_results["full"] = {
                "avg10": float(parts[1].split("=")[1]),
                "avg60": float(parts[2].split("=")[1]),
                "avg300": float(parts[3].split("=")[1]),
                "total": int(parts[4].split("=")[1])
            }
    file1 = open(folder_ + '/pressure_mem.txt', 'r')
    file_content = file1.read()
    file1.close()
    lines = file_content.split("\n")
    
    for line in lines:
        if not line:
            continue
            
        parts = line.split(" ")

        if parts[0] == "some":
            mem_results["some"] = {
                "avg10": float(parts[1].split("=")[1]),
                "avg60": float(parts[2].split("=")[1]),
                "avg300": float(parts[3].split("=")[1]),
                "total": int(parts[4].split("=")[1])
            }

        if parts[0] == "full":
            mem_results["full"] = {
                "avg10": float(parts[1].split("=")[1]),
                "avg60": float(parts[2].split("=")[1]),
                "avg300": float(parts[3].split("=")[1]),
                "total": int(parts[4].split("=")[1])
            }
    return [cpu_results, mem_results]



def extract_top_processes(folder_):
    with open(folder_ + '/top_cpu', 'r') as f:
        lines = f.readlines()

    process_lines = []

    for line in lines:
        if line.strip().startswith("PID"):
            process_lines.append(line.strip())
        elif len(process_lines) > 0 and len(process_lines) <= 10:
            if not line.isspace():
                process_lines.append(line.strip())
    return process_lines[:11]
