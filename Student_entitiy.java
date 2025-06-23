package com.example.demo.Student_entitiy;


import jakarta.persistence.Entity; 
import jakarta.persistence.Id;     

@Entity 
public class Student_entitiy {

    @Id 
    private int roll_no;

    private String name;

    //@Column(unique = true)
    
    private String last_name;

    public Student_entitiy() {

    }

    public int getRoll_no() {
        return roll_no;
    }

    public void setRoll_no(int roll_no) {
        this.roll_no = roll_no;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getLast_name() {
        return last_name;
    }

    public void setLast_name(String last_name) {
        this.last_name = last_name;
    }

    
    public int getstu_no() { 
        return roll_no;
    }

    public void setEmp_id(int roll_no) { 
        this.roll_no = roll_no;
    }
}