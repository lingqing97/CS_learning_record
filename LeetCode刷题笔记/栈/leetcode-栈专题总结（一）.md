### 496.下一个更大元素（一）
#### 题目描述
![avatar](/image/leetcode_栈_下一个更大元素(一).jpg)
#### 思路
先忽略数组nums1,之后通过**单调栈**将nums2中每一个元素的下一个更大的元素找出。
我们维护一个单调栈，栈中的元素从栈顶到栈底是**单调不降的**。
#### 题解
```c++
class Solution {
public:
    vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
        stack<int> mystack;
        unordered_map<int,int> mymap;
        for(int i=0;i<nums2.size();i++){
            //细节:nums2[i]>mystack.top(),没有等于，题目是找下一个更大的元素，不包括等于
            while((!mystack.empty())&&(nums2[i]>mystack.top())){
                mymap[mystack.top()]=nums2[i];
                mystack.pop();
            }
            mystack.push(nums2[i]);
        }
        while(!mystack.empty()){
            mymap[mystack.top()]=-1;
            mystack.pop();
        }
        vector<int> ans;
        for(int i=0;i<nums1.size();i++){
            ans.push_back(mymap[nums1[i]]);
        }
        return ans;
    }
};
```
#### 复杂度分析
* 时间复杂度:O(M+N),其中M和N分别是nums1和nums2的长度
* 空间复杂度:O(N),用来存储nums2的栈和哈希表

#### 下一个更大元素(二)
![avatar](/image/leetcode_栈_下一个更大元素(二).jpg)
##### 题解
```c++
class Solution {
public:
    vector<int> nextGreaterElements(vector<int>& nums) {
        vector<int> ans(nums.size(),0);
        stack<int> mystack;
        int L=nums.size();
        //通过取余来实现循环
        for(int i=2*L-1;i>=0;i--){
            while((!mystack.empty())&&(nums[i%L]>=mystack.top())){
                mystack.pop();
            }
            ans[i%L]=(mystack.empty()?-1:mystack.top());
            mystack.push(nums[i%L]);
        }
        return ans;
    }
};
```
##### 复杂度分析

* 时间复杂度:O(N),其中N为nums数组的大小
* 空间复杂度:O(N)