public class Fibonacci {
    public static void main(String[] args) {
        int f = 0;
        int s = 1;
        int t = 0;

        System.out.println(f);
        System.out.println(s);

        while (t < 13) {
            t = f + s;
            if (t >= 13) {
                break;
            }
            System.out.println(t);
            f = s;
            s = t;
        }
    }
}

output:

0
1
1
2
3
5
8

