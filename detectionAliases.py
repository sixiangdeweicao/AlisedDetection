#coding:utf-8
import os
import ipaddress
from copy import deepcopy 
import random
import re
from AddrsToSeq import AddrVecList, InputAddrs
from DHC import InitializeDSAndPrefix, SpaceTreeGen, OutputSpaceTree
import queue
import argparse


def DectetoinBGP(bgpfile, bgpresult):
    '''
    Function:
        check perfix alias in  BGP
    Args:
        bgpfile: the bgp prefix filename
        bgpresult:the file store the result
    return
        ipv6_aliases (set): the ipv6 alias prefix
    '''
    print("bgein check the aliax in bgp")
    ipv6_aliases = set()
    ipv6_noaliases=set()
    for line in open(bgpfile, 'r'):
        if line.split(" ")[0] == ";":
            continue
        if line == "\n":
            continue
        line = line.split()[0]
        print(line)
        bgp_prefix = deepcopy(line)
        bl = ipv6_probes(line)
        if bl == True:
            ipv6_aliases.add(bgp_prefix)
        else:
            ipv6_noaliases.add(bgp_prefix)
    with open(bgpresult,'w') as f:
        for x in ipv6_aliases:
            f.write(x+"\n")
    print('bgp check Over!')


def DetectionHitlist(hitlist, hitlistresult,ipcount=100):
    '''
    Function:
        check perfix alias in  hitlist
    Args:
        hitlist: the hitlist filename
        hitlistresult:the file store the result
    return 
        ipv6_aliases (set): the ipv6 alias prefix 
    '''
    print("bgein check in hitlist")
    ipv6_aliases=set()
    ipv6_noaliases=set()

    # ipv6_probes("2600:9000:3079::5")
    # detec the alias in hitlist map the prefix
    V = InputAddrs(input=hitlist,beta=16)
    root = SpaceTreeGen(V, beta=ipcount)
    InitializeDSAndPrefix(root, V, beta = 16)
    del V[:]
    # OutputSpaceTree(root, V)
    # 广度优先遍历
    que = queue.Queue()
    que.put(root)
    while not que.empty():
        node = que.get()
        print("probe {}".format(node.prefix))
        bl = ipv6_probes(node.prefix)
        if bl == True:
            ipv6_aliases.add(node.prefix)
        else:
            ipv6_noaliases.add(node.prefix)
            childs = node.childs
            for child in childs:
                que.put(child)
   
    with open(hitlistresult,'w') as f:
        for x in ipv6_aliases:
            f.write(x+"\n")
    print('hitlist check Over!')


def ipv6_probes(bgp_prefix):
    '''
    Function:
        check perfix alias in bgp prefix
    Args:
        bgp_prefix: the bgp prefix  
    return 
        bool 
    '''
    # 构造探测地址（伪随机）
    ipv6_probes=set()
    lines=bgp_prefix.split("/")
    bgp_ip=lines[0]
    bgpspace=int(lines[1])
    bgp_ip=ipaddress.IPv6Address(bgp_ip)
    bgp_ip=str(bgp_ip.exploded)
    nybbles=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    if bgpspace>=124:
        return False
    else:
        bgp_ip=bgp_ip.replace(":","")
        ipv6=list(bgp_ip)
        
        for i in range(16):
            temp=0
            if bgpspace%4==0:
                temp=int(bgpspace/4)
            else:
                temp=int(bgpspace/4)+1
            ipv6[temp]=nybbles[i]
            temp+=1
            while temp<32:
                nybble=random.sample(nybbles,1)
                ipv6[temp]=nybble[0]
                temp+=1
            # 数组转换为标准的ipv6地址
            ipv6_str=""
            for j in  range(1,33):
                if j%4==0 and j!=32:
                    ipv6_str+=ipv6[j-1]
                    ipv6_str=ipv6_str+":"
                else:
                    ipv6_str+=ipv6[j-1]
            #print(ipv6)
            ipv6_probes.add(ipv6_str)
        target="zmaptarget.csv"
        result_icmp="zmapscanp_icmp.csv"
        result_80="zmapscanp_80.csv"
        ipv6_probes=list(ipv6_probes)
        with open(target,'w') as f:
            for ip in ipv6_probes:
                f.write(ip+"\n")
            for ip in ipv6_probes:
                f.write(ip+"\n")
            for ip in range(len(ipv6_probes)):
                if ip<len(ipv6_probes)-1:
                    f.write(ipv6_probes[ip]+"\n")
            else:
                f.write(ipv6_probes[ip])
        ipresult = set()
        command="sudo zmap --ipv6-source-ip=2001:da8:ff:212::10:3 --ipv6-target-file="+target+" -M icmp6_echoscan -o "+result_icmp +" >outfile.txt"
        os.system(command)
        for res in open(result_icmp,'r'):
            if res=="\n":
                continue
            res=res.replace("\n","")
            ipresult.add(res)
            # res=res.replace("{","")
            # res=res.replace("}","").strip().split(": ")[1].replace("\"","").replace("\"","")
        command="sudo zmap --ipv6-source-ip=2001:da8:ff:212::10:3 --ipv6-target-file="+target+" -M icmp6_echoscan -o "+result_80
        os.system(command)
        
        for res in open(result_80,'r'):
            if res=="\n":
                continue
            res=res.replace("\n","")
            ipresult.add(res)
            # res=res.replace("{","")
            # res=res.replace("}","").strip().split(": ")[1].replace("\"","").replace("\"","")
        return  len(ipresult)==len(ipv6_probes)



def hitlistMapPrefix(hitlist, ipcount):
    '''
    Function:
        hitlist map to prefix ,and ask the prefix has ipv6 count more than ipcount
    Args:
        hitlist:the target file (include the ipv6 address)
        ipvount:the minimum number that each prefix include
    return:
        ipv6_prefix:the ipv6 prefix list
    '''
    ipv6_prefix_dic = {}  # 保存前缀和包含地址个数
    for line in open(hitlist,'r'):
        if line =="\n":
            continue
        line=line.replace("\n","")
        # 判断是否为ipv6地址
        if ipv6_addr(line)==False:
            print ("{} invaild".format(line))
            continue
        # map to  prefix in different length
        # 因为要检测前缀长度在64-124长度的别名前缀，只需要存前缀长度为64的前缀
        line=ipaddress.IPv6Address(line)
        line=list(str(line.exploded))
        # print(line)
        count=0
        prefix=""
        for i in line:
            if i==":":
                prefix=prefix+i
                continue
            else:
                count+=1
            prefix=prefix+i
            if count>=16 and count<=28:
                prefix1=deepcopy(prefix)
                prefix1=prefix1+"::/"+str(count*4)
                if prefix1 in ipv6_prefix_dic:
                    ipv6_prefix_dic[prefix1] = ipv6_prefix_dic[prefix1] + 1
                else:
                    ipv6_prefix_dic[prefix1]=1
                del prefix1
    ipv6_prefix=[]
    for key in ipv6_prefix_dic:
        if ipv6_prefix_dic[key] >=ipcount:
           ipv6_prefix.append(key)
           print(key)
    # for key in ipv6_prefix_dic:
    #     print("{} has {}".format(key,ipv6_prefix_dic[key]))
    ipv6_prefix_dic.clear()
    # for key in ipv6_prefix:
    #     print(key)
    
    return ipv6_prefix


def ipv6_addr(addr):
    '''
    Returns True if the IPv6 address (and optional subnet) are valid, otherwise
    returns False.
    '''
    # From http://stackoverflow.com/questions/6276115/ipv6-regexp-python
    ip6_regex = (r'(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,6}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,5}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,4}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,3}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,5}(:[0-9a-f]{1,4}){1,2}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,6}(:[0-9a-f]{1,4}){1,1}\Z)|'
                 r'(\A(([0-9a-f]{1,4}:){1,7}|:):\Z)|(\A:(:[0-9a-f]{1,4})'
                 r'{1,7}\Z)|(\A((([0-9a-f]{1,4}:){6})(25[0-5]|2[0-4]\d|[0-1]'
                 r'?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|'
                 r'(\A(([0-9a-f]{1,4}:){5}[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|'
                 r'[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|'
                 r'(\A([0-9a-f]{1,4}:){5}:[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|'
                 r'[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|'
                 r'(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,4}:(25[0-5]|'
                 r'2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d))'
                 r'{3}\Z)|(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,3}:'
                 r'(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?'
                 r'\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4})'
                 r'{1,2}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|'
                 r'[0-1]?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]'
                 r'{1,4}){1,1}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|'
                 r'2[0-4]\d|[0-1]?\d?\d)){3}\Z)|(\A(([0-9a-f]{1,4}:){1,5}|:):'
                 r'(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?'
                 r'\d?\d)){3}\Z)|(\A:(:[0-9a-f]{1,4}){1,5}:(25[0-5]|2[0-4]\d|'
                 r'[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)')
    return bool(re.match(ip6_regex, addr))


def Detectin6Gen():
    pass

if __name__ == "__main__":
    #DectetoinBGP("test.csv","bgpresult.csv")
    DetectionHitlist("/home/liguo/6Tree_no_APD_new/6Treeresult10000000.txt","hitlistrelust.csv")
    #ipv6_prefix=hitlistMapPrefix("hitlist.csv",4)
