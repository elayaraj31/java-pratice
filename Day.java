public class Day 
{
 public static void main(String[] args)
{
day1();
}
public static void day1()
{
int day = 1;
    switch (day){

    case 1:
        System.out.println("sun");
        break;
    case 2:
        System.out.println("mon");
        break;
    case 3:
        System.out.println("thu");
        break;
    case 4:
        System.out.println("wen");
        break;
   default:
      System.out.println("hello");
        break;
}
}
}

/*Qustion:
1)+ve case:
2)-ve case:
5)default statement remove.
4)remove break and default.
6)we will give float value.
5)give a default statement for last in the code.
remove curly brase.*/
 /*OUTPUT:
1)sun
2)hello
3)wen
4)sun
  mon
  thu
  wen
5)Day.java:25: error: unreachable statement
      System.out.println("hello");
      ^
1 error

6)Day.java:102: error: method day4() is already defined in class Day
public static void day4()
                   ^
Day.java:106: error: selector type float is not allowed
    switch (day)
           ^
2 errors
7)Day.java:10: error: '{' expected
    switch (day)
                ^
Day.java:28: error: reached end of file while parsing
}
 ^
*/

