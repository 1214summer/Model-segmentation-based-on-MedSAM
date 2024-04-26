package cn.sam.service.impl;

import cn.sam.entity.User;
import cn.sam.mapper.UserMapper;
import cn.sam.service.UserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
}
