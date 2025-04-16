public class Strong_number
{
public static void main(String args[])
{
int num=145;
int no=num;
int total=0;
while(no>0)
{
int sum=0;
int res=no%10;
no=no/10;
sum=find_fact(res);
total=total+sum;

}
if(total==num)
System.out.println("strong number");
else
System.out.println("not strong number");


}
public static int find_fact(int no)
{
int total=1;
for(int i=no;i>0;i--)
{
total=total*i;

}
return total;
}



}
