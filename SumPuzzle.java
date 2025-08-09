import java.util.Scanner;

public class SumPuzzle {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int num = sc.nextInt();

        int sum = 0, n = num;
        while (n > 0) {
            sum += n % 10;
            n /= 10;
        }

        if (sum % 2 == 0) {
            System.out.println("Double Sum: " + (sum * 2));
        } else {
            System.out.println("Half Sum: " + (sum / 2.0));
        }
    }
}

