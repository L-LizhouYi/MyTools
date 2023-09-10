#!/usr/bin/env python3

import re
import argparse
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich import box

from contextlib import redirect_stdout
from io import StringIO

from collections import Counter

class ProcessedData:
    def __init__(self, time, ip, domain):
        self.time = time
        self.ip = ip
        self.domain = domain

class LogInitData:
    def __init__(self):
        self.file_path = "access.log"
        self.filter_keywords = ['vless', '127.0.0.1', 'udp', 'inbound']
        self.data_ip = defaultdict(list)
        self.data_domain = defaultdict(list)
        self.data_list = []

    def read_lines_from_file(self):
        try:
            with open(self.file_path, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            print("File not found:", self.file_path)
            return []
        except Exception as e:
            print("An error occurred:", str(e))
            return []

    def process_line(self, line):
        line = line.strip()
        if any(keyword in line for keyword in self.filter_keywords):
            return None
        else:
            parts = line.split(" ")
            time = parts[0] + " " + parts[1]
            ip = parts[2][:-2]
            domain = re.search(r"tcp:(.*?):\d+", parts[-1]).group(1)
            return ProcessedData(time, ip, domain)

    def run(self):
        lines = self.read_lines_from_file()
        for line in lines:
            data = self.process_line(line)
            if data:
                entry_ip = {"time": data.time, "domain": data.domain}
                entry_domain = {"time": data.time, "ip": data.ip}

                self.data_ip[data.ip].append(entry_ip)
                self.data_domain[data.domain].append(entry_domain)
                self.data_list.append(data)


class GetInfo(LogInitData):

    def __init__(self):
        super().__init__()

        self.i = []
        self.e = []

    def getAll(self):
        pass

    def dataExt(self, i):
        if self.i and self.e:
            if any(keyword in i for keyword in self.i) and not any(keyword in i for keyword in self.e):
                return i
        elif self.i:
            if any(keyword in i for keyword in self.i):
                return i
        elif self.e:
            if not any(keyword in i for keyword in self.e):
                return i
        else:
            return i

    #获取日志中所有的IP地址
    def getIPs(self):
        IPs = list(self.data_ip.keys())
        print("IPs:")
        for i in IPs:
            print("\t",i)
        return IPs

    #获取日志中出现的所有域名
    def getDomains(self):
        Domains = list(self.data_domain.keys())

        dict_domians = []
        for i in Domains:
            dict_domians.append((i,len(self.data_domain[i])))

        sorted_items = sorted(dict_domians, key=lambda x: x[1], reverse=True)

        print("Domains:")
        for item,count in sorted_items:
            res = self.dataExt(item)
            if res:
                print("\t",count,res)

        return Domains

    def getTextIp(self,ip):
        result = self.data_ip[ip]

        for i in result:
            res = self.dataExt(i['domain'])
            if res:
                print(i['time'],res)

    def getTextDomain(self,domain):
        temp_data = defaultdict(list)
        for i in self.data_domain.keys():
            if domain in i:
                print(i)
                for s in self.data_domain[i]:
                    res = self.dataExt(s['ip'])
                    if res:
                        print("\t",s['time'],res)
                        temp_data[i].append({"time":s['time'],"ip":res})
        return temp_data

    # 扩展 添加计数 Emmmm
    def getTextIpExt(self,ip):
        result = self.data_ip[ip]

        counter = Counter([i['domain'] for i in result])
        sorted_items = sorted(counter.items(),key=lambda x: x[1],reverse=True)

        console = Console()
        table = Table(box=box.MINIMAL_HEAVY_HEAD,title=f"{ip} Get Url")
        table.add_column("ID")
        table.add_column("Domain")
        table.add_column("Count")

        num = 1

        for item,count in sorted_items:
            item = self.dataExt(item)
            if item:
                table.add_row(str(num),item,str(count))
                num += 1

        console.print(table)

    def getTextDomainExt(self,domain):

        temp_stdout = StringIO()

        console = Console()
        table = Table(box=box.MINIMAL_HEAVY_HEAD,title="Domain to IP")
        table.add_column("ID")
        table.add_column("Domain")
        table.add_column("IP")

        with redirect_stdout(temp_stdout):
            result = self.getTextDomain(domain)

        for count, i in enumerate(result.keys()):
            a = set([s['ip'] for s in result[i]])
            table.add_row(str(count+1),i,"\n".join(a))

        console.print(table)

def run():

    parser = argparse.ArgumentParser()

    # 可选参数
    parser.add_argument('-i',"--ext_i" ,type=str, help='Ext i',required=False)
    parser.add_argument('-e',"--ext_e",type=str, help='Ext e',required=False)
    parser.add_argument('-f', "--file_path", type=str, help='log file path',required=False)
    
    parser.add_argument('-s',"--command",type=str,help='function')

    # 功能函数调用
    args = parser.parse_args()
    if args.command:
    
        obj_log = GetInfo()
        if args.ext_i:
            obj_log.i = args.ext_i.split(',')
        if args.ext_e:
            obj_log.e = args.ext_e.split(',')
        if args.file_path:
            obj_log.file_path = args.file_path
            
        command = args.command.split(':')
        obj_log.run()
        
        if command[0] == 'gi':
            obj_log.getIPs()
        elif command[0] == 'gd':
            obj_log.getDomains()
        elif command[0] == 'gil':
            obj_log.getTextIp(command[1])
        elif command[0] == 'gdl':
            obj_log.getTextDomain(command[1])
        elif command[0] == 'gie':
            obj_log.getTextIpExt(command[1])
        elif command[0] == 'gde':
            obj_log.getTextDomainExt(command[1])
            
    else:
        Test_text = '''
            ** optional **
            
            -f access.log
            -i 192.168.1.1,114.114
            -e www.google,com
            
            ** required **
            
            -s gi
            -s gd

            -s gil:192.168.1.1
            -s gdl:google.com

            -s gie:192.168.1.1
            -s gde:192.168.1.1
        '''
        print("Test:")
        print("\t",Test_text)
        
if __name__ == "__main__":
    run()
