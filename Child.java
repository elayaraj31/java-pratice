package program;

public class Child extends Parent
{

	public static void main(String[] args)
	{
		Child cc = new Child();
		//Parent ss= new Parent();
		
		cc.pay();
		

	}
	public void pay() 
	{
		super.pay();
		System.out.println("CAR");

	}

}
