package com.example.CURD_opration.Controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.CURD_opration.Serivec.StudentSerivce;
import com.example.CURD_opration.model.Student;

@RestController
public class StudentController {
	
	@Autowired
	StudentSerivce studentserivce;
	
	
	@GetMapping("std")
	public List<Student> getStudents(){
		return studentserivce.getStudents();
	}

}
