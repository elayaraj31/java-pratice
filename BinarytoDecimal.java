public class BinarytoDecimal {
	public static void main(String[] args)
	{
        int no = 100;        
        int base = 2;         
        int power = 0;        
        int decimal = 0;  
		while(no>0)
		{
			int rem=no%10;
			int result=rem*find_power(base,power);
			decimal=decimal+result;
			no=no/10;
			power++;
		}
		System.out.println(decimal);

	}
	public static int find_power(int base,int power)
	{
		int result=1;
		while(power>0)
		{
			result=result*base;
			power--;
		}
		return result;
	}

}

