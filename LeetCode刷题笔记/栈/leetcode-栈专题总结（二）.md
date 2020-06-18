### 856.括号的分数
#### 题目描述
![avatar](/image/leetcode_栈_括号的分数.jpg)
#### 思路
- 构建一个栈
- 如果遇到`(`就往栈里面添加
- 如果遇到`)`就去寻找最近的左括号抵消，同时计算里面的分数
```
[(]                # 遇到 ( 往栈添加
[(, (]             # 继续添加
[(, 1]             # 遇到 ） 合成一个1
[(, 1, (]          # 遇到 ( 往栈添加
[(, 1, (, (]       # 继续添加
[(, 1, (, 1]       # 遇到 ） 合成一个1
[(, 1, 2]          # 遇到 ） ，结构就是（1）， 所以计算的话是 1 * 2
[6]                # 遇到 ） ，结构是（1，2）， 所以计算的话是 （1 + 2） * 2
```
#### 题解
```c++
class Solution {
public:
    int scoreOfParentheses(string S) {
        stack<int> score;
        for(char ch:S){
            if(ch=='('){
                score.push(-1);
            }
            else{
                if(score.top()==-1){
                    score.pop();
                    score.push(1);
                }
                else{
                    int tmp=0;
                    while(score.top()!=-1){
                        tmp+=score.top();
                        score.pop();
                    }
                    score.pop();
                    score.push(2*tmp);
                }
            }
        }
        int ans=0;
        while(!score.empty()){
            ans+=score.top();
            score.pop();
        }
        return ans;
    }
};
```
#### 复杂度分析
* 时间复杂度:O(N)
* 空间复杂度:O(N)

### 946.验证栈序列
#### 题目描述
![avatar](/image/leetcode_栈_验证栈序列.jpg)
#### 思路
将`pushed`队列中的每个数都`push`到栈中，同时检查这个数是不是`popped`序列中下一个要`pop`的值，如果是就把它`pop`出来。
最后，检查不是所有的该`pop`出来的值都是`pop`出来了
#### 题解
```c++
class Solution {
public:
    bool validateStackSequences(vector<int>& pushed, vector<int>& popped) {
        int i=0,j=0;
        for(int k=0;k<pushed.size();k++){
            pushed[i++]=pushed[k];  //这里我们不另外开辟栈空间，直接使用pushed
            while(i>0&&pushed[i-1]==popped[j]){
                i--;
                j++;
            }
        }
        return i==0;
    }
};
```
#### 复杂度分析
* 时间复杂度:O(N)
* 空间复杂度:O(1)