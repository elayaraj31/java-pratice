public class KFC
{
String qty = "large";
int price = 390;
KFC wings = new KFC();
//variable
//static block
//non-static block
public KFC(String,int)
{
}
public static void main(String[] args)
{
    KFC popcorn = new KFC("elayi",10);
    KFC periperi = new KFC();
//method calling statement
    popcorn.buy();
    KFC.feedBack();
    popcorn.feedBack();
    feedBack();
    periperi.buy();
}
public static void feedBack()
{
    System.out.println("good");
}

//method definition
public void buy()
{
    System.out.println("buy-method");
    this.pay();
//this refers to current object
}
public void pay()
{
    System.out.println("pay-390");
}

}
