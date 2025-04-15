public class Payilagam
{
 String course;
 int age;
 String address;
public Payilagam(String course,int age,String address)
{
       this.course = course;
       this.age = age;
       this.address=address;
System.out.println(course +" "+ age +" " +address);
}
public Payilagam(int age)
{ 
int i = age;
System.out.println(i);
}
public static void main(String[] args)
{
Payilagam ram = new Payilagam("java",21,"chennai");
Payilagam sam = new Payilagam(21);
sam.displayinfo();
}
public void  displayinfo()
{
System.out.println(course +" "+ age +" " +address);
}
}
