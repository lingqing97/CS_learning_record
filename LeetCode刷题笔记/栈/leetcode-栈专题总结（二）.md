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