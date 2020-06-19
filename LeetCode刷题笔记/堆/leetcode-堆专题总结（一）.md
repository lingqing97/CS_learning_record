### 剑指offer40.最小的K个数
#### 题目描述
![avatar](/image/leetcode_堆_最小的k个数.jpg)
#### 思路
我们用一个大根堆实时维护数组的前 $k$ 小值。首先将前 $k$ 个数插入大根堆中，随后从第 $k+1$ 个数开始遍历，如果当前遍历到的数比大根堆的堆顶的数要小，就把堆顶的数弹出，再插入当前遍历到的数。最后将大根堆里的数存入数组返回即可。在下面的代码中，由于C++语言中的堆（即优先队列）为大根堆，我们可以这么做。而 Python 语言中的对 为小根堆，因此我们要对数组中所有的数取其相反数，才能使用小根堆维护前 $k$ 小值。
#### 题解
```c++
class Solution {
public:
    vector<int> getLeastNumbers(vector<int>& arr, int k) {
        vector<int> ans(k,0);
        if(k==0) return ans;
        priority_queue<int> numQueue;
        int i;
        for(i=0;i<k;i++) numQueue.push(arr[i]);
        for(;i<(int)arr.size();i++){
            if(arr[i]<numQueue.top()){
                numQueue.pop();
                numQueue.push(arr[i]);
            }
        }
        for(int i=0;i<k;i++){
            ans[i]=numQueue.top();
            numQueue.pop();
        }
        return ans;
    }
};
```
#### 复杂度
* 时间复杂度:$O(n \log k),$ 其中 $n$ 是数组 $\operatorname{arr}$ 的长度。由于大根堆实时维护前 $k$ 小值，所以插入删除都是 $O(\log k)$ 的时间复杂度，最坏情况下数组里 $n$ 个数都会插入，所以一共需要 $O(n \log k)$ 的时间复杂度。
* 空间复杂度:$O(k),$ 因为大根堆里最多 $k$ 个数。