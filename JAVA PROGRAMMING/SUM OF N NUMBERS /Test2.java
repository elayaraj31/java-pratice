public class Test2
{
public  static void main(String[] args)
        {
    int no=9;
    int squar = no*no;
    Test2 obj = new Test2();
    int result = obj.sum_of(squar);
    System.out.println("Sum of digits of square: " + result);
    }
public int sum_of(int no)
{
int sum=0;
while(no>0){
sum=sum+(no%10);
no=no/10;
}
return sum;
}
}
