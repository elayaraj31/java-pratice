public class Test1
{
public Test1(String couse,int i)
{
System.out.println(couse+""+i);
//System.out.println(i);
}
    
public static void main(String[] args)
{

 Test1 sam=new Test1("java",10);
sam.display(5,10);


 }
public int display(int i,int j)
    {
        int sam= i+j;
        System.out.println(sam);
    return sam;

    }

}
