### 313.超级丑数
#### 问题描述
![avatar](/image/leetcode_栈_超级丑数.jpg)
#### 思想
因为丑数就是一堆质数的乘积，比如例题`[2,7,13,19]`,那么丑数就是$2^x7^y13^z19^k$的一系列数。
- 这里我们采用动态规划的思想，以例题为例。
  - 初始化四个指针`i2`,`i7`,`i13`,`i19`和存储丑数的数组nums。
  - 循环计算所有丑数:
    - 在`nums[i2]*2`,`nums[i7]*7`,`nums[i13]*13`,`nums[i19]*19`选出最小的数添加到数组nums中。
    - 将该数字对应的因子的指针向前移动一步。

#### 题解
```c++
class Solution {
public:
    int nthSuperUglyNumber(int n, vector<int>& primes) {
        vector<int> dp(primes.size(),0);    //初始化指针，其中dp[0]为指向primes[0]的指针
        vector<int> nums(n,0);
        nums[0]=1;
        for(int i=1;i<n;i++){
            int min=INT_MAX;
            for(int j=0;j<primes.size();j++){
                if(nums[dp[j]]*primes[j]<min){  //找最小值
                    min=nums[dp[j]]*primes[j];
                }
            }
            nums[i]=min;
            //移动指针
            for(int j=0;j<primes.size();j++){
                if(nums[dp[j]]*primes[j]==min){
                    dp[j]++;
                }
            }
        }
        return nums[n-1];
    }
};
```

#### 相似题目
![avatar](/image/leetcode_栈——丑数二.jpg)
##### 题解
```c++
class Solution {
public:
    int nthUglyNumber(int n) {
        vector<int> helper;
        helper.push_back(1);
        int i2=0,i3=0,i5=0;
        for(int i=1;i<n;i++){
            int min_=min(helper[i2]*2,min(helper[i3]*3,helper[i5]*5));
            if(min_==helper[i2]*2) i2++;
            if(min_==helper[i3]*3) i3++;
            if(min_==helper[i5]*5) i5++;
            helper.push_back(min_);
        }
        return helper.back();
    }
}
```



