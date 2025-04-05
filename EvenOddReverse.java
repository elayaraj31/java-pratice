import java.util.Scanner;

public class EvenOddReverse {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int num = sc.nextInt();

        if (num % 2 == 0) {
            int reversed = 0, n = num;
            while (n != 0) {
                reversed = reversed * 10 + n % 10;
                n /= 10;
            }
            System.out.println("Reversed: " + reversed);
        } else {
            System.out.println("Odd number, no reverse: " + num);
        }
    }
}

