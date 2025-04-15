public class Perfect
{
    public static void main(String[] args)
    {
        int no = 6;
        int div = 1;

        while(div < no) {
            if(no % div == 0)
                System.out.println(div);
            div = div + 1;
        }

        div = 1; 
        int sum = 0;

        while(div < no) {
            if(no % div == 0) {
                sum = sum + div;
            }
            div = div + 1;
        }

        if(sum == no) 
            System.out.println("Perfect");
        else
            System.out.println("not perfect");
    }
}

