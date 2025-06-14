package program;

import java.io.File;
import java.io.IOException;

public class FileDemo {

	public static void main(String[] args) throws IOException 
	{
		File ff = new File("/home/elayaraja/Documents/JAVA PROGRAMMING/file/elayi.txt");
		boolean b = ff.createNewFile();
		System.out.println(b);
		System.out.println(ff.canExecute());
		System.out.println(ff.canRead());
		System.out.println(ff.canWrite());
	//	System.out.println(ff.delete());
		System.out.println(ff.exists());
		System.out.println(ff.getAbsolutePath());
		System.out.println(ff.getCanonicalPath());
		System.out.println(ff.getName());
		System.out.println(ff.isDirectory());
		System.out.println(ff.isFile());

	}

}
