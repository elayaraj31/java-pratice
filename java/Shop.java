public class Shop {
    static String name;  // Removed static
    int price;

    public static void main(String[] args) {
float f = 10/3;
System.out.println(f);
        Shop prod1 = new Shop();
        prod1.name = "abc";
        prod1.price = 20;

        Shop prod2 = new Shop();
        prod2.name = "bcd";
        prod2.price = 50;

        prod1.buy();
        prod2.buy();  // Fixed: Call buy() on prod2 instead of Shop.buy()
    }

    public double buy() {

        System.out.println(name);
        System.out.println(price);
return 5.3;
    }
}

