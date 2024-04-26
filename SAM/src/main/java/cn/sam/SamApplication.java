package cn.sam;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletComponentScan;

@ServletComponentScan
@SpringBootApplication
public class SamApplication {

    public static void main(String[] args) {
        SpringApplication.run(SamApplication.class, args);
    }

}
