package cn.sam.controller;

import cn.sam.common.R;
import cn.sam.entity.User;
import cn.sam.service.UserService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.DigestUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@Slf4j
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    /***
     * 用户登录
     * @param request
     * @param user
     * @return
     */
    @PostMapping("/login")
    public R<User> login(HttpServletRequest request, @RequestBody User user){
        //1.加密
        String password = user.getPassword();
        password= DigestUtils.md5DigestAsHex(password.getBytes());

        //2.查询数据库
        LambdaQueryWrapper<User> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(User::getUsername,user.getUsername());
        User getUser = userService.getOne(queryWrapper);

        if(getUser == null) return R.error("登陆失败");

        if(!getUser.getPassword().equals(password)) return R.error("密码错误");

        //登陆成功并返回结果
        request.getSession().setAttribute("user",getUser.getId());
        return R.success(getUser);
    }

    @PostMapping("/logout")
    public R<String> logout(HttpServletRequest request){
        request.getSession().removeAttribute("user");
        return R.success("退出成功");
    }
}
