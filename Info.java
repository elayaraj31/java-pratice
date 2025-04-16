public class Info
{
String name;
int age;
String nat;
public Info(String name,int age,String nat)
{
    this.name=name;
    this.age = age;
    this.nat = nat;
// System.out.println("hello");
}
public Info(String name,int age)
{
    this(name,age,"indian");
//  new Info("abc",20,"indian");
    System.out.println(name+""+age+""+nat);
}
public static void main(String[] args)
{
    Info p1 = new Info("abc",20);
    Info p2 = new Info("xyz",25);
}
}


