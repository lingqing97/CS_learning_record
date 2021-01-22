### Chapter6

#### 条款32:确定你的`public`继承塑模出`is-a`关系

* "public继承"意味`is-a`.适用于`base classes`身上的每一件事情一定也适用于`derived classes`身上，因为每一个`derived class`对象也都是一个`base class`对象.

#### 条款33：避免遮掩继承而来的名称

* `derived classes`内的名称会遮掩`base class`内的名称。只要名称相同就会被覆盖，无论函数参数是否相同，也无论是`virtual`还是`non-virtual`(见下例)
* 为了让被遮掩的名称再见天日，可使用`using`声明式或转交函数(forwarding functions)

```cpp
//例子一：名称相同即被覆盖

class Base{
    private:
        int x;
    public:
        virtual void mf1() =0;
        virtual void mf1(int);
        virtual void mf2();
        void mf3();
        void mf3(double);
        ...
};

class Derived:public Base{
    public:
        //mf1覆盖Base::mf1(),Base::mf1(int)
        virtual void mf1();
        //mf3覆盖Base::mf3(),Base::mf3(double)
        void mf3();
        void mf4();
        ...
};

int main(){
    Derived d;
    int x;
    ...
    d.mf1();    //没问题，调用Derived:mf1
    d.mf1(x);   //错误！因为Derived::mf1覆盖了Base::mf1
    d.mf2();    //没问题，调用Base::mf2
    d.mf3();    //没问题，调用Derived::mf3
    d.mf3(x);   //错误！因为Derived::mf3遮掩了Base::mf3
}

//例子二：使用using声明式，使得被覆盖的函数在derived class中可见

class Base{
    private:
        int x;
    public:
        virtual void mf1() =0;
        virtual void mf1(int);
        virtual void mf2();
        void mf3();
        void mf3(double);
        ...
};

class Derived:public Base{
    public:
        using Base::mf1();      //让Base class内名为mf1和mf3的所有东西
        using Base::mf3();      //在Derived作用域内都可见(并且public)
        virtual void mf1();
        void mf3();
        void mf4();
};

int main(){
    Derived d;
    int x;
    ...
    d.mf1();    //没问题，调用Derived::mf1
    d.mf1(x);   //没问题，调用Base::mf1
    d.mf2();    //没问题，调用Base::mf2
    d.mf3();    //没问题，调用Derived::mf3
    d.mf3(x);   //没问题，调用Base::mf3
}
```

#### 条款34：区分接口继承和实现继承

* `public`继承包含两个方面的概念：函数接口(function interfaces)继承和函数实现(function implementations)继承
    1. 声明一个`pure virtual`函数的目的是为了让`dervied classes`只继承函数接口
    2. 声明简朴的（非纯）`impure virtual`函数的目的，是让`derived classes`继承该函数的接口和缺省实现
    3. 声明`non-virtual`函数的目的是为了令`derived classes`继承函数的接口及一份强制性实现。任何`derived class`都不应该尝试改变继承而来的`non-virtual`函数

```cpp
//pure virtual 函数：让derived classes继承函数接口


class Shape{
    public:
        virtual void draw() const = 0;
};


//impure virtual函数：让derived classes继承函数接口和缺省实现
//例子一：函数接口和缺省实现
class Airport {...};    //用以表现机场
class Airplane{
    public:
        virtual void fly(const Airport& destination);
};

void Airplane::fly(const Airport& destination){
    //缺省代码，将飞机飞至目的地
}

class ModelA:public Airplane {...};
class ModelB:public Airplane {...};

//例子二：函数接口和缺省实现分离
//方式一
class Airplane{
    public:
        //pure virtual提高函数接口
        virtual void fly(const Airport& destination)=0;
        ...
    protected:
        //定义protected defaultFly让derived classes继承缺省实现
        void defaultFly(const Airport& destination);
};

void Airplane:defaultFly(const Airport& destination){
    //缺省行为，将飞机飞至目的地
}

class ModelA:public Airplane{
    public:
        virtual void fly(const Airport& destination){
            defaultFly(destination);
        }
};

class ModelB:public Airplane{
    public:
        virtual void fly(const Airport& destination){
            defaultFly(destination);
        }
};

class ModelC:public Airplane{
    public:
        virtual void fly(const Airport& destination);
        ...
};

void ModelC::fly(const Airport& destination){
    //将C型飞机飞至指定目的地
}

//方式二
class Airplane{
    public:
        virtual void fly(const Airport& destination)=0;
        ...
};
void AIrplane::fly(const Airport& destination)  //pure virtual函数实现
{
    //缺省行为，将飞机飞至目的地
}

class ModelA:public Airplane{
    public:
        virtual void fly(const Airport& destination){
            Airplane::fly(destination);
        }
        ...
};

class ModelB:public Airplane{
    public:
        virtual void fly(const Airport& destination){
            Airplane::fly(destination);
        }
};

class ModelC:public Airplane{
    public:
        virtual void fly(const Airport& destination);
        ...
};
void ModelC:fly(const Airport& destination){
    //将C型飞机飞至指定目的地
}
```

#### 条款35：考虑`virtual`函数以外的其他选择

* `virtual`函数的替换方案有以下几种:
    1. 使用`non-virtual interface(NVI)`手法，那是`Template Method`设计模式的一种特殊形式。它以`public non-virtual`成员函数包裹较低访问性(`private`或`protected`)的`virtual`函数 
    2. 将`virtual`函数替换为“函数指针成员变量”，这是`Strategy`设计模式的一种分解表现形式
    3. 以`function`成员变量替换`virtual`函数，因而允许使用任何可调用物
    4. 将继承体系内的`virtual`函数替换为另一个继承体系内的`virtual`函数。这是`Strategy`设计模式的传统实现手法

```cpp
//方式一:NVI手法
class GameCharacter{
    public:
        //计算游戏中人物的健康指数
        int healthValue() const{
            ...     //做一些事情工作
            int retVal=doHealthValue();     //做真正的工作
            ...     //做一些事后工作
        }
        ...
    private:
        //derived classes可重新定义它
        //若derived classes要实现多态，可将其定义为protected
        virtual int doHealthValue() const{
            //缺省算法,计算健康指数
        }
};

//方式二：使用函数指针
class GameCharacter;
//计算健康指数的缺省算法
int defaultHealthCalc(const GameCharacter& gc);
class GameCharacter{
    public:
        typedef int (*HealthCalcFunc) (const GameCharacter&);
        explict GameCharacter(HealthCalcFunc fcf=defaultHealthCalc):healthFunc(hcf)
        {}
        int healthValue() const{
            return healthFunc(*this);
        }
    private:
        HealthCalcFunc healthFunc;
};

class EvilBadGuy:public GameCharacter{
    public:
        explict EvilBadGuy(HealthCalcFunc hcf=defaultHealthCalc):GameCharacter(hcf)
        {...}
        ...
};

int loseHealthQuickly(const GameCharacter&);    //健康指数计算函数1
int loseHealthSlowly(const GameCharacter&);    //健康指数计算函数22

//不同人物使用不同的健康计算函数
EvilBadGuy ebg1(lossHealthQuickly);
EvilBadGuy ebg2(lossHealthSlowly);


//方式三:使用function(c++11中function在头文件<functional>中)
class GameCharacter;
//计算健康指数的缺省算法
int defaultHealthCalc(const GameCharacter& gc);
class GameCharacter{
    public:
        typedef function<int(const GameCharacter&)> HealthCalcFunc;
        explict GameCharacter(HealthCalcFunc fcf=defaultHealthCalc):healthFunc(hcf)
        {}
        int healthValue() const{
            return healthFunc(*this);
        }
    private:
        HealthCalcFunc healthFunc;
};

class EvilBadGuy:public GameCharacter{
    public:
        explict EvilBadGuy(HealthCalcFunc hcf=defaultHealthCalc):GameCharacter(hcf)
        {...}
        ...
};

int loseHealthQuickly(const GameCharacter&);    //健康指数计算函数1
int loseHealthSlowly(const GameCharacter&);    //健康指数计算函数22
struct HealthCalculator{
    int operator()(const GameCharacter&) const
    { ... }
};

//不同人物使用不同的健康计算函数
EvilBadGuy ebg1(lossHealthQuickly);
EvilBadGuy ebg2(lossHealthSlowly);
EvilBadGuy ebg2(HealthCalculator());

//方式四:使用传统的strategy设计模式
class GameCharacter;
class HealthCalcFunc{
    public:
        ...
        virtual int calc(const GameCharacter& gc) const
        { ... }
        ...
};

HealthCalcFunc defaultHealthCalc;

Class GameCharacter{
    public:
        explict GameCharacter(HealthCalcFunc* phcf=&defaultHealthCalc):pHealthCalc(phcf)
        {}
        int healthValue() const
        { return pHealthCalc->calc(*this);}
    private:
        HealthCalcFunc* pHealthCalc;
};
```

#### 条款36：绝不重新定义继承而来的`non-virtual`函数

* `non-virtual`函数的不变性凌驾其特异性，所以任何情况下都不该重新定义一个继承而来的`non-virtual`函数

#### 条款37：绝不重新定义继承而来的缺省参数值

* `virtual`函数是动态绑定的，而缺省参数值却是静态绑定的。(即在多态中，永远使用的都是`base class`的缺省参数，而不会使用`derived class`的缺省参数)

#### 条款38：通过复合塑模出`has-a`或"根据某物实现出"

* 复合的意义和`public`继承完全不同
* 在应用域，复合意味`has-a`(有一个)。在实现域，复合意味`is-implemented-in-terms-of`(根据某物实现出)(?)

#### 条款39：明智而审慎地使用`private`继承

* `private`继承意味`implemented-in-terms-of`(根据某物实现出).`private`继承意味只有实现部分被继承.
  * 如果D以`pirvate`形式继承B，意思是D对象根据B对象实现而得，再没有其他意涵了
* 使用复合(`composition`)通常可以替代`private`继承，所以尽可能使用复合，必要时才使用`private`继承(见例子)
* 和复合不同，`private`继承可以造成`empty base`最优化。这对致力于“对象尺寸最小化”的程序库开发者而言，可能很重要(见例子)

```cpp
//例子一：使用复合替代private继承
class Timer{
    public:
        explicit Timer(int tickFrequency);
        //函数每自动调用一次，定时器就滴答一次
        virtual void onTick() const;
        ...
};

//这里不能是public继承，因为Widget不是timer
class Widget:private timer{
    private:
        virtual void onTick() const;    //查看Widget的数据...等等
};


//使用复合
class Widget{
    private:
        class WidgetTimer:public Timer{
            public:
                virtual void onTick() const;
                ...
        };
        WidgetTimer timer;
};


//例子二：使用private继承进程empty base优化

//优化前:
class Empty();
class HoldAnInt{
    private:
        int x;
        Empty e;    //应该不需要任何内存
};

sizeof(Empty())==> =1 !!! //通常C++官方默默安插一个char到空对象内
sizeof(HoldAnInt)>sizeof(int)==> true

//优化后
class HoldAnInt:private Empty{
    private:
        int x;
};

sizeof(HoldAnInt)==sizeof(int)==> true      //编译器会进行`EBO`(empty base optimization;空白基类最优化)
```

#### 条款40：明智而审慎地使用多重继承

* 多重继承比单一继承复杂。它可能导致新的歧义性，以及对`virtual`继承的需要
* `virtual`继承会增加大小、速度、初始化（及赋值）等等成本。如果`virtual base classes`不带任何数据，将是最具实用价值的情况
