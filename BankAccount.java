package com.indianBank;
public class BankAccount
{

 int age = 25;


 BankAccount(String accountHolder,int balance)
{
    this.accountHolder = accountHolder;
    this.balance = balance;
}
public static void main(String[] args)
{
    BankAccount account1 = new BankAccount("vijay",1000);
    BankAccount account2 = new BankAccount("chandru",10000);

    account1.showBalance();
    System.out.println(account1.age);
   

}

 void showBalance()
{
    System.out.println("current balance = > "+this.balance);
}


}
