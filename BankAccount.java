public class BankAccount
{
String acountholder;
int balance;
    public static void main(String args[])
    {
       BankAccount account1 =  new BankAccount("elayi",1000);
       account1.deposite(2000);

}
public void deposite(int amount)
{
    this.balance = balance + amount;
System.out.println("successfully deposited RS:"+amount);
System.out.println("Balance RS:"+balance);
}
public BankAccount(String acountholder,int balance )
{
this.acountholder = acountholder;
this.balance = balance;
}
}
