public class Prime
{
    public static void main(String[] args)
    {
        int no = 3;
        int div = 2;

        if (no % div == 0) {
            System.out.println("not prime");
        } else {
            div = div + 1;
            if (no % div == 0) {
                System.out.println("not prime");
            } else {
                System.out.println("prime");
            }
        }
    }
}

