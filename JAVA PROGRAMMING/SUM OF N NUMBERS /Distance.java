public class Distance
{

public static void main(String[] args)
{

int total=50,day=0;     
int up=3,down=1;
int position=0;
while(position<total)
{
  position=position+(up-down);
  day=day+1;
  System.out.println(day);
}
//System.out.println(day);
}
}

