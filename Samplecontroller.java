package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class Samplecontroller
{
	@RequestMapping("elayaraj")
	public String display() 
	{
		System.out.println("=========hii er========");
		return "index";
	}

}
