#!/usr/bin/python3.6
# encoding:utf-8
from AddrsToSeq import InputAddrs
from Definitions import Stack
from DHC import SpaceTreeGen, OutputSpaceTree
from copy import deepcopy
import math
import pdb

def ScanPre(root, V):
    """
    动态扫描开始前的准备工作

    Args:
        root:空间树的根结点
        V：种子地址向量序列
    """

    InitializeDS(root, V)


def InitializeDS(node, V, parent_stack = Stack(), beta=16):
    """
    对结点node的DS进行初始化

    Args：
        node：当前DS待初始化的结点
        V：所有种子向量序列
        parent_stack：父结点的DS            
        beta：向量每一维度的基数
    """    
    
    # pdb.set_trace()

    stack = deepcopy(parent_stack) #注意要将父结点的DS做拷贝

    vecDim = int(128 / math.log(beta, 2))

    for delta in range(1, vecDim + 1):        
        if node.Steady(delta, V) and stack.find(delta) == False:
            stack.push(delta)

    if not node.isLeaf():
        for child in node.childs:
            InitializeDS(child, V, stack, beta)
    else:
        for delta in range(1, vecDim + 1):
            if stack.find(delta) == False:
                stack.push(delta)
    
    node.DS = stack
    # pdb.set_trace()

if __name__ == '__main__':
    V = InputAddrs(input="hitlist.txt")
    root = SpaceTreeGen(V, beta=1)
    ScanPre(root, V)
    # InitializeDS(root, V)
    # InitializeTS(root, V)
    OutputSpaceTree(root, V)
    print('Over')
