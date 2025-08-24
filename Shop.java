public class Shop
{
    static String shop_name = "sugumar";
    String name;
    int price;
public static void main(String[] args)
{
    Shop prod1 = new Shop();
        prod1.name = "abc";
        prod1.price = 20;
    Shop prod2 = new Shop();
        prod2.name = "bcd";
        prod2.price = 200;
    prod1.shop_name = "elayaraj";

    System.out.println(shop_name);
    System.out.println(Shop.shop_name);
    System.out.println(prod1.shop_name);

//    prod1.buy();
//    Shop.buy();
}

public static void buy()
{
   System.out.println("hii");
}

}
