import matplotlib.pyplot as plt
from IPython import display
import torchvision 
import torch
import sys
from torch import nn
import torch.nn.functional as F
import time

def use_svg_display():
    # 用矢量图显示
    display.set_matplotlib_formats('svg')
#定义生成锚框的函数
def MultiBoxPrior(feature_map,sizes=[0.75,0.5,0.25],ratios=[1,2,0.5]):
    '''
        参数说明:
            feature_map:torch tensor,shape:[N,C,H,W]
            size:缩放比例
            ratio:宽高比
        返回值:
            anchors of shape (1,num_anchors,4).每个batch里每个都一样，所以第一维为1
    '''
    pairs=[] #pair of (size,sqrt(ratio))
    for r in ratios:
        pairs.append([sizes[0],math.sqrt(r)])
    for s in sizes[1:]:
        pairs.append([s,math.sqrt(ratios[0])])
    
    pairs=np.array(pairs)
    
    ss1=pairs[:,0]*pairs[:,1] #size*sqrt(ratio)
    ss2=pairs[:,0]/pairs[:,1] #size/sqrt(ratio)
    
    base_anchors=np.stack([-ss1,-ss2,ss1,ss2],axis=1)/2
    
    h,w=feature_map.shape[-2:]
    shifts_x=np.arange(0,w)/w
    shifts_y=np.arange(0,h)/h
    shift_x,shift_y=np.meshgrid(shifts_x,shifts_y)
    shift_x=shift_x.reshape(-1)
    shift_y=shift_y.reshape(-1)
    shifts=np.stack((shift_x,shift_y,shift_x,shift_y),axis=1)
    
    anchors=shifts.reshape((-1,1,4))+base_anchors.reshape((1,-1,4))
    
    return torch.tensor(anchors,dtype=torch.float32).view(1,-1,4)
#绘制边界框
def bbox_to_rect(bbox,color):
    return plt.Rectangle(
        xy=(bbox[0],bbox[1]),width=bbox[2]-bbox[0],height=bbox[3]-bbox[1],
        fill=False,edgecolor=color,linewidth=2)
#定义描绘以某个像素为中心的所有锚框
def show_bboxes(axes,bboxes,labels=None,colors=None):
    def _mask_list(obj,default_values=None):
        if obj is None:
            obj=default_values
        elif not isinstance(obj,(list,tuple)):
            obj=[obj]
        return obj
    
    labels=_mask_list(labels)
    colors=_mask_list(colors,['b','g','r','m','c'])
    for i,bbox in enumerate(bboxes):
        color=colors[i%len(colors)]
        rect=bbox_to_rect(bbox.detach().cpu().numpy(),color)
        axes.add_patch(rect)
        if labels and len(labels) > i:
            text_color = 'k' if color == 'w' else 'w'
            axes.text(rect.xy[0], rect.xy[1], labels[i],
                      va='center', ha='center', fontsize=6, color=text_color,
                      bbox=dict(facecolor=color, lw=0))
# 参考https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Object-Detection/blob/master/utils.py#L356
def compute_intersection(set_1, set_2):
    """
    计算anchor之间的交集
    Args:
        set_1: a tensor of dimensions (n1, 4), anchor表示成(xmin, ymin, xmax, ymax)
        set_2: a tensor of dimensions (n2, 4), anchor表示成(xmin, ymin, xmax, ymax)
    Returns:
        intersection of each of the boxes in set 1 with respect to each of the boxes in set 2, shape: (n1, n2)
    """
    # PyTorch auto-broadcasts singleton dimensions
    lower_bounds = torch.max(set_1[:, :2].unsqueeze(1), set_2[:, :2].unsqueeze(0))  # (n1, n2, 2)
    upper_bounds = torch.min(set_1[:, 2:].unsqueeze(1), set_2[:, 2:].unsqueeze(0))  # (n1, n2, 2)
    intersection_dims = torch.clamp(upper_bounds - lower_bounds, min=0)  # (n1, n2, 2)
    return intersection_dims[:, :, 0] * intersection_dims[:, :, 1]  # (n1, n2)


def compute_jaccard(set_1, set_2):
    """
    计算anchor之间的Jaccard系数(IoU)
    Args:
        set_1: a tensor of dimensions (n1, 4), anchor表示成(xmin, ymin, xmax, ymax)
        set_2: a tensor of dimensions (n2, 4), anchor表示成(xmin, ymin, xmax, ymax)
    Returns:
        Jaccard Overlap of each of the boxes in set 1 with respect to each of the boxes in set 2, shape: (n1, n2)
    """
    # Find intersections
    intersection = compute_intersection(set_1, set_2)  # (n1, n2)

    # Find areas of each box in both sets
    areas_set_1 = (set_1[:, 2] - set_1[:, 0]) * (set_1[:, 3] - set_1[:, 1])  # (n1)
    areas_set_2 = (set_2[:, 2] - set_2[:, 0]) * (set_2[:, 3] - set_2[:, 1])  # (n2)

    # Find the union
    # PyTorch auto-broadcasts singleton dimensions
    union = areas_set_1.unsqueeze(1) + areas_set_2.unsqueeze(0) - intersection  # (n1, n2)

    return intersection / union  # (n1, n2)
#定义softmax函数
def softmax(X):
    X_exp=X.exp()
    partition=X_exp.sum(dim=1,keepdim=True)
    return X_exp/partition

#定义平方损失函数
def squared_loss(y_hat,y):
    return (y_hat-y.view(y_hat.size()))**2/2

#定义cross_entropy损失函数
def cross_entropy(y_hat,y):
    return -torch.log(y_hat.gather(1,y.view(-1,1)))

#定义随机梯度下降算法SGD
def sgd(params,lr,batch_size):
    for param in params:
        param.data-=lr*param.grad/batch_size

#FashingMNIST相关函数

#获取FashionMNIST中的标签
def get_fashion_mnist_labels(labels):
    text_labels = ['t-shirt', 'trouser', 'pullover', 'dress', 'coat',
                    'sandal', 'shirt', 'sneaker', 'bag', 'ankle boot']
    return [text_labels[int(i)] for i in labels]

def show_fashion_mnist(images, labels):
    use_svg_display()
    # 这里的_表示我们忽略（不使用）的变量
    _, figs = plt.subplots(1, len(images), figsize=(12, 12))
    for f, img, lbl in zip(figs, images, labels):
        f.imshow(img.view((28, 28)).numpy())
        f.set_title(lbl)
        f.axes.get_xaxis().set_visible(False)
        f.axes.get_yaxis().set_visible(False)
    plt.show()

#加载FashionMNIST数据
def load_data_fashion_mnist(batch_size,resize=None):
    if sys.platform.startswith('win'):
        num_workers = 0  # 0表示不用额外的进程来加速读取数据
    else:
        num_workers = 4
    trans=[]
    
    if resize:
        trans.append(torchvision.transforms.Resize(size=resize))
    trans.append(torchvision.transforms.ToTensor())
    transform=torchvision.transforms.Compose(trans)
    #加载FashMNIST数据集
    mnist_train=torchvision.datasets.FashionMNIST(root='/home/wushukun/jupyterHome/remotePython/DeepLearning/Dataset/',
                                                                train=True,download=True,transform=transform)
    mnist_test=torchvision.datasets.FashionMNIST(root='/home/wushukun/jupyterHome/remotePython/DeepLearning/Dataset/',
                                                                train=False,download=True,transform=transform)
    
    train_iter = torch.utils.data.DataLoader(mnist_train, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    test_iter = torch.utils.data.DataLoader(mnist_test, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return train_iter,test_iter

#定义计算测试集的总体正确率
def evaluate_accuracy(data_iter,net,device=None):
    if device is None and isinstance(net,nn.Module):
        device=list(net.parameters())[0].device
    acc_sum,n=0.0,0
    for X,y in data_iter:
        if isinstance(net,torch.nn.Module):
            net.eval() #评估模式，这会关闭dropout
            acc_sum+=(net(X.to(device)).argmax(dim=1)==y.to(device)).float().sum().cpu().item()
            net.train() #改回训练模式
        else: #自定义的模型
            if('is_training' in net.__code__.co_varnames):#如果有is_training这个变量
                #将is_training设置为False
                acc_sum+=(net(X,is_training=False).argmax(dim=1)==y).float().sum().item()
            else:
                acc_sum+=(net(X).argmax(dim=1)==y).float().sum().item()
        n+=y.shape[0]
    return acc_sum/n
    
#训练softmax回归
def train_ch3(net,train_iter,test_iter,loss,num_epochs,batch_size,
             params=None,lr=None,optimizer=None):
    for epoch in range(num_epochs):
        train_l_sum,train_acc_sum,n=0.0,0.0,0
        for X,y in train_iter:
            y_hat=net(X)
            l=loss(y_hat,y).sum()

            #梯度清零
            if optimizer is not None:
                optimizer.zero_grad()
            elif params is not None and params[0].grad is not None:
                for param in params:
                    param.grad.data.zero_()
            
            l.backward()
            if optimizer is None:
                sgd(params,lr,batch_size)
            else:
                optimizer.step()
            
            train_l_sum+=l.item()
            train_acc_sum+=(y_hat.argmax(dim=1)==y).sum().item()
            n+=y.shape[0]
        test_acc=evaluate_accuracy(test_iter,net)
        print('epoch %d,loss %.4f,train acc%.3f,test acc %.3f'
             %(epoch+1,train_l_sum/n,train_acc_sum/n,test_acc))
        
class FlattenLayer(nn.Module):
    def __init__(self):
        super(FlattenLayer,self).__init__()
    def forward(self,x): # x shape:(batch,*,*,...)
        return x.view(x.shape[0],-1)
    
#定义全局平均池化层
class GlobalAvgPool2d(nn.Module):
    def __init__(self):
        super(GlobalAvgPool2d,self).__init__()
    def forward(self,x):
        return F.avg_pool2d(x,kernel_size=x.size()[2:])
    
#定义线性模型
def linreg(X,w,b):
    return torch.mm(X,w)+b

#定义训练函数
def train_ch5(net,train_iter,test_iter,num_epochs,device,optimizer):
    net=net.to(device)
    print('train on',device)
    loss=nn.CrossEntropyLoss()
    for epoch in range(num_epochs):
        train_l_sum,train_acc_sum,n,batch_count,start=0.0,0.0,0,0,time.time()
        for X,y in train_iter:
            X=X.to(device)
            y=y.to(device)
            y_hat=net(X)
            l=loss(y_hat,y)
            optimizer.zero_grad()
            l.backward()
            optimizer.step()

            train_l_sum+=l.cpu().item()
            train_acc_sum+=(y_hat.argmax(dim=1)==y).float().sum().cpu().item()
            n+=y.shape[0]
            batch_count+=1
        test_acc=evaluate_accuracy(test_iter,net)
        print('epoch %d,train loss %.4f,train acc %.4f,test acc %.4f,time %.1f sec'
                %(epoch+1,train_l_sum/batch_count,train_acc_sum/n,test_acc,time.time()-start))