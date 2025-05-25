package regexjava;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegexDemo {

	public static void main(String[] args, Object pattern) {
		String input ="my moblie is 98765476";
		Pattern patternObj = Pattern.compile("[A-Za-z]");
		Matcher matcherObj = patternObj.matcher(input);
		while(matcherObj.find())
		{
			System.out.println(matcherObj.group());
//			System.out.println(matcherObj.start());
//			System.out.println(matcherObj.end());

		}

	}

}
