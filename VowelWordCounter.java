package array;

public class VowelWordCounter 
{
    public static void main(String[] args) 
    {
    	int i =12345;
    	int sum =0;
    	while(i>0)
    	{
    	int	digit=i%10;
    	sum=sum*10+digit;
    		i=i/10;
    		
    			
    	}
    	System.out.println(sum);
    	
    	
        
    }
}

