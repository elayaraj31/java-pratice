package com.example.Course_Registration_System.Model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Course {
	@Id
	private String CourseId;
	private String courseName;
	private String trainer;
	private int durationInWeek;
	public String getCourseId() {
		return CourseId;
	}
	public void setCourseId(String courseId) {
		CourseId = courseId;
	}
	public String getCourseName() {
		return courseName;
	}
	public void setCourseName(String courseName) {
		this.courseName = courseName;
	}
	public String getTrainer() {
		return trainer;
	}
	public void setTrainer(String trainer) {
		this.trainer = trainer;
	}
	public int getDurationInWeek() {
		return durationInWeek;
	}
	public void setDurationInWeek(int durationInWeek) {
		this.durationInWeek = durationInWeek;
	}
	
	


}
