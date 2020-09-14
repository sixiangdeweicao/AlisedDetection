from Definitions import Stack, TreeNode
from AddrsToSeq import AddrVecList, InputAddrs
import math
from copy import deepcopy

"""
使用DHC算法生成一棵空间树
"""

lamda = 128 #IPv6地址的二进制长度


def SpaceTreeGen(V, beta=16):
    """
    空间树生成

    Args:
        V:有序的种子地址向量序列
        beta:叶子结点中地址数量的上限

    Return：
        root：空间树的根结点
    """
    
    root = TreeNode(0, len(V) - 1)   #初始化根结点，内容为种子地址向量序列
    DHC(root, beta, V)
    # DHC(root, 2, V)
    return root


def DHC(node, beta, V,base=16):
    """
    层次聚类算法

    Args；
        node：当前待聚类的结点
        beta：叶结点中向量个数上限
        V:所有种子地址向量的序列

    """
    vecNum = node.sup - node.inf + 1    #当前结点中的向量个数
    if vecNum <= beta:
        return

    same = True
    delta = 1   #记录当前结点所有向量中熵不为0的最小维度
    for delta in range(0, int(lamda/math.log(base, 2))):
        v1 = V[node.inf]
        for v2 in V[node.inf + 1: node.sup + 1]:
            if v1[delta] != v2[delta]:
                same = False
                break
        if same == False:
            break
    if same == True:
        #所有向量都相等？删到只剩一个
        return
    
    node.diff_delta = delta + 1
    subSeqs = SplitVecSeq(node.inf, node.sup, delta, V)
    for sub in subSeqs:
        newNode = TreeNode(sub[0], sub[1], _parent=node)
        node.childs.append(newNode)
    for child in node.childs:
        DHC(child, beta, V)


def SplitVecSeq(inf, sup, delta, V):
    """
    将V[inf]到V[sup]范围内的序列分割成在维度delta上有相同值的子序列

    Args：
        inf：序列起点
        sup：序列终点
        delta：当前结点所有向量中熵不为0的最低维度
        V:种子向量序列

    Return：
        subSeqs：二维列表，列表中每一个元素形如[subInf, subSup]，
        记录了每一个子序列的起止位置
    """

    subSeqs = []
    subInf = inf    #子序列的起点
    subSup = subInf + 1 #子序列的终点
    while subInf <= sup:
        while subSup <= sup and V[subInf][delta] == V[subSup][delta]:
            subSup += 1
        subSeqs.append([subInf, subSup - 1])
        subInf = subSup
        subSup = subInf + 1
            
    return subSeqs


def OutputSpaceTree(root, V):
    """
    层次遍历输出空间树

    Args：
        root：空间树的根结点
        V:种子地址向量序列
    """

    print('******LEVEL 1******')
    childs = root.childs
    root.OutputNode(V)
    # OutputNode(root, V)
    level = 2
    while childs != []:
        print('******LEVEL %d******' % level)
        while childs != [] and childs[0].level == level:
            child = childs.pop(0)
            childs.extend(child.childs)
            child.OutputNode(V)
            # OutputNode(child, V)
        level += 1
        

def InitializeDSAndPrefix(node, V, parent_stack=Stack(), beta=16):
    """
    对结点node的DS进行初始化

    Args：
        node：当前DS待初始化的结点
        V：所有种子向量序列
        parent_stack：父结点的DS            
        beta：向量每一维度的基数
    """

    # pdb.set_trace()
    # prefix=deepcopy(parent_prefix)
    stack = deepcopy(parent_stack)  # 注意要将父结点的DS做拷贝
    vecDim = int(128 / math.log(beta, 2))
    if node.isLeaf() == False:
        #stack = deepcopy(parent_stack)  # 注意要将父结点的DS做拷贝
        for delta in range(1, vecDim + 1):
            if node.Steady(delta, V) and stack.find(delta) == False:
                #prefix = prefix+str(V[node.inf][delta-1])
                stack.push(delta)
                # if node.level == 1:
                #     pass
                # else:
                #     break
            if node.Steady(delta, V) == False:
                break
        for child in node.childs:
            InitializeDSAndPrefix(child, V, stack, beta)
    else:
         for delta in range(1, vecDim + 1):
            if node.Steady(delta, V) and stack.find(delta) == False:
                #prefix = prefix+str(V[node.inf][delta-1])
                stack.push(delta)
    node.DS = stack
    nybbles=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    prefix_index=[]
    
    for i in range(32):
        if node.DS.find(i+1):
            prefix_index.append(i+1)
        else:
            break
    l=len(prefix_index)
    p=V[node.inf]
    prefix=''
    for i in prefix_index:
        prefix = prefix + nybbles[p[i-1]]
        if i % 4 == 0:
            if i!=32:
                prefix = prefix + ":"
    if l==32:
        prefix = prefix + "/" + str(l * 4)
    elif l > 28:
        prefix = prefix + "1/" + str(l * 4)
    else:
        if  i % 4 != 0:
            prefix = prefix +"::"+ "/" + str(l * 4)
        else:
            prefix = prefix +":"+ "/" + str(l * 4)



    
    node.prefix=prefix
    # pdb.set_trace()

        
        
if __name__ == '__main__':
    # V = InputAddrs('responsive-addresses.txt')
    V = InputAddrs(input="/home/liguo/6Tree_no_APD_new/6Tree.result10000000",beta=16)
    root = SpaceTreeGen(V, beta=1)
    InitializeDSAndPrefix(root, V, beta=16)
    OutputSpaceTree(root, V)
    print('Over!')
