package cn.sam.entity;

import lombok.Data;
import java.time.LocalDateTime;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;


@Entity
@Data
public class User {
@Id
private Long id;
    private String username;
    private String password;
    private String email;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    // Getters and setters
}
