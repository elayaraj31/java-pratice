public class KFC
{
    int price;
    String qty;
//    char ch;    
//    boolean b;
//    float fl;
//
public KFC(int price ,String qty)
{
    this.price = price;
    this.qty = qty;
}
public KFC()
{

}
public static void main(String[] args)
{
    int i;
    KFC wings = new KFC(150,"large");
    KFC zinger = new KFC(100,"small");
    KFC periperi = new KFC();

    System.out.println(wings.price);
    System.out.println(wings.qty);
    System.out.println(zinger.price);
    System.out.println(zinger.qty);

    System.out.println(periperi.qty);
    System.out.println(periperi.price);
//     System.out.println(periperi.ch);
//    System.out.println(periperi.b);
//     System.out.println(periperi.fl);
//   
    


}

}
