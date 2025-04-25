import java.util.Scanner;

public class BankingApp {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        BankAccount account = null;

        int choice;
        do {
            System.out.println("\n--- Banking System ---");
            System.out.println("1. Create Account");
            System.out.println("2. Deposit");
            System.out.println("3. Withdraw");
            System.out.println("4. Check Balance");
            System.out.println("5. Account Info");
            System.out.println("6. Exit");
            System.out.print("Enter your choice: ");
            choice = sc.nextInt();

            switch (choice) {
                case 1:
                    if (account != null) {
                        System.out.println("Account already created.");
                    } else {
                        System.out.print("Enter Name: ");
                        sc.nextLine(); // consume newline
                        String name = sc.nextLine();
                        System.out.print("Enter Account Number: ");
                        int accNo = sc.nextInt();
                        account = new BankAccount(name, accNo);
                        System.out.println("Account created successfully!");
                    }
                    break;

                case 2:
                    if (account == null) {
                        System.out.println("Create an account first.");
                    } else {
                        System.out.print("Enter amount to deposit: ₹");
                        double dep = sc.nextDouble();
                        account.deposit(dep);
                    }
                    break;

                case 3:
                    if (account == null) {
                        System.out.println("Create an account first.");
                    } else {
                        System.out.print("Enter amount to withdraw: ₹");
                        double wd = sc.nextDouble();
                        account.withdraw(wd);
                    }
                    break;

                case 4:
                    if (account == null) {
                        System.out.println("Create an account first.");
                    } else {
                        account.checkBalance();
                    }
                    break;

                case 5:
                    if (account == null) {
                        System.out.println("Create an account first.");
                    } else {
                        account.displayAccountInfo();
                    }
                    break;

                case 6:
                    System.out.println("Thank you for using our banking system!");
                    break;

                default:
                    System.out.println("Invalid choice!");
            }
        } while (choice != 6);

        sc.close();
    }
}
