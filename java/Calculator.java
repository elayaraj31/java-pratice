public class Calculator {

    public static void main(String[] args) {
        Calculator cc = new Calculator(); // Fixed typo in class name
        cc.add(10,10);
        cc.add(12,4);
        cc.add(6,8);
    }

    public void add(int no1,int no2)
 {
      //  int no1 = 10;
      //  int no2 = 15;
        int total = no1 + no2;
        System.out.println(total);
    }
}

