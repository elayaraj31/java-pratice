public class Num
{
 public static void main(String[] args)
{
test1();
test2();
test3();
test4();
test5();
test6();
test7();
}
public static void test1()
{
System.out.println("-----------test1-----------");
    int no = 1576;
        while(no>0)
{
System.out.println(no%10);
 no/=10;
        }
System.out.println(no);
    }
public static void test2()
{
System.out.println("-----------test2-----------");
    int no = 1576;
        while(no>=1)
{

System.out.println(no%10);
 no/=10;
        }
}
public static void test3()
{
System.out.println("-----------test3-----------");
    int no = 47056;
        while(no>0)
{

System.out.println(no%10);
 no/=10;
        }
}
public static void test4()
{
System.out.println("-----------test4-----------");
    int no = 04756;
        while(no>0)
{

System.out.println(no%10);
 no/=10;
        }
}
public static void test5()
{
System.out.println("-----------test5-----------");
    int no = 04756;
        while(no>0)
{

System.out.println(no%100);
 no/=10;
        }
}
public static void test6()
{
System.out.println("-----------test6-----------");
    int no = 04756;
        while(no>0)
{

System.out.println(no%10);
 no/=100;
        }
}
public static void test7()
{
System.out.println("-----------test7-----------");
    int no = 04756;
        while(no>0)
{

System.out.println(no%100);
 no/=1000;
        }
}
}

/*OUTPUT:
-----------test1-----------
6
7
5
1
0
-----------test2-----------
6
7
5
1
-----------test3-----------
6
5
0
7
4
-----------test4-----------
2
4
5
2
-----------test5-----------
42
54
25
2
-----------test6-----------
2
5
-----------test7-----------
42
2*/


