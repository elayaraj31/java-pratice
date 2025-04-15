public class BankAccount
{
String acountholder;
int balance;
    public static void main(String args[])
    {
       BankAcoount account1 =  new BankAcoount("elayi",1000);
       account1.deposite(2000);

}
public void deposite(int amount)
{
    this.blance = balance + amount;
System.ount.println("successfully deposited"+amount);
}
public BankAcoount(String acountholder,int balance )
{
this.accountholder = acountholder;
this.balance = balance;
}
}
