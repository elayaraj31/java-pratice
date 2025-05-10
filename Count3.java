public class Count
{
public static void main(String[] args)
    {
    int i=153;
    int c=count(i);
        System.out.println(c);
    }
   public static  int count(int i)
    {
    int c=0;
    while(i>0){
    i=i/10;
    c=c+1;
    }
return c;
    }
}
