public class Perfect2 {
	public static void main(String[] args)
	{
		int no = 29;
		int div = 1;
		int sum = 0;
		while (div<0);
		{
			if(no%div==0)
			{
				sum = sum + div;
			}
			div = div+1;
		}
		System.out.println(sum);
		if(sum==no)
			System.out.println("PERFECT");
		if(sum==1)
			System.out.println("NOT PRIME");
	}

}

