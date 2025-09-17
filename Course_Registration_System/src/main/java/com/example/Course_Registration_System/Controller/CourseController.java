package com.example.Course_Registration_System.Controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.Course_Registration_System.Model.Course;
import com.example.Course_Registration_System.Model.CourseRegistry;
import com.example.Course_Registration_System.Service.CourseService;

@RestController
@CrossOrigin(origins = "http://127.0.0.1:5500")
public class CourseController {
	
	@Autowired
	CourseService courseService;
	
	@GetMapping("/courses")
	public List<Course> availableCourses(){
		
	return courseService.availableCourses();
		
	}
	
	@GetMapping("/courses/enrolled")
	public List<CourseRegistry> enrolledStudents(){
		return courseService.enrolledStudents();
	}
	
	@PostMapping("/courses/enrolled/register")
	public String enrollCourse(@RequestParam("name") String name,
			@RequestParam("emailId")String emailId,@RequestParam("courseName")String courseName) {
		courseService.enrollCourse(name,emailId,courseName);
		return "Congratulation "+name+" Enrollment Successfully For "+courseName;
	}

}
