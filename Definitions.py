#!/usr/bin/python3.6
# encoding:utf-8
from copy import deepcopy
import math


class Stack(object):
    """
    栈类(DS的数据类型)
    """
    
    def __init__(self):
        self.stack = []

    def push(self, v):
        self.stack.append(v)

    def pop(self):
        if self.stack:
            return self.stack.pop(-1)
        else:
            raise LookupError('Stack is empty!')

    def is_empty(self):
        return bool(self.stack)

    def top(self):
        if self.stack:
            return self.stack[-1]
        else:
            raise LookupError('Stack is empty!')

    def find(self, v):
        return v in self.stack


class TreeNode:
    """
    空间树的结点
    """

    global_node_id = 0
    def __init__(self, _inf=0, _sup=0, _parent=None):
        if _parent == None:
            self.level = 1
        else:
            self.level = _parent.level + 1
        self.inf = _inf
        self.sup = _sup # 地址下标上界，例如这个节点如果指示了地址向量数组中[i...j]位置的地址向量，那么inf为i，
                        # sup为j
        self.parent = _parent
        self.childs = []
        self.prefix = ''
        TreeNode.global_node_id += 1
        self.node_id = TreeNode.global_node_id  #结点编号（每次产生新结点，自动递增）
        self.DS = Stack()
        
    def isLeaf(self):
        return self.childs == []

    def Steady(self, delta, V):
        """
        判断结点中的所有向量序列是否在维度delta上有相同值

        Args：
            delta：待判断维度
            V：所有种子向量序列

        Return：
            same：结点中向量序列在delta维度上熵为0时为True
        """

        v1 = V[self.inf]
        same = True
        for v2 in V[self.inf + 1: self.sup + 1]:
            if v1[delta - 1] != v2[delta - 1]:
                same = False
                break
        return same


    def  OutputNode(self, V):
        """
        输出一个结点的信息

        Args:
            node:当前结点
            V：地址向量序列
        """

        print('[+]Parent:', end = ' ')
        if self.parent == None:
            print('None')
        else:
            print(self.parent.node_id)
        print('[+]%d Address(es):' % (self.sup - self.inf + 1))
        for i in range(self.inf, self.sup + 1):
            print(V[i])
        print('[+]Childs:', end = ' ')
        if self.childs == []:
            print('None')
        else:
            for child in self.childs:
                print(child.node_id, end = ' ')
            print()
        print('[+]DS:')
        print(self.DS.stack)
        print('[+]Prefix:')
        print(self.prefix)
        print('\n')

def Intersection(l1, l2):
    """
    计算两个列表的重复成员

    """
    intersection = [v for v in l1 if v in l2]
    return intersection
