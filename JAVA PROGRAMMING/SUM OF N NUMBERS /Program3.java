public class Program3
{

public static void main(String[] args)
{

int total=50,day=1;     
int up=3,down=1;
int position=0;
while(position<total)
{
  position=position+(up-down);
  day=day+1;
 System.out.println(day);
}
}
}

