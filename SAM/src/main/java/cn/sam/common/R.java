package cn.sam.common;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;


/***
 * 通用返回结果，返回成对象
 * @param <T>
 */
@Data
public class R<T> {
    private Integer code;

    private String msg;

    private T data;

    private Map map=new HashMap();  //动态数据

    public static <T> R<T> success(T object){
        R<T> r = new R<>();
        r.data = object;
        r.code = 1;
        r.msg="success";
        return r;
    }

    public static <T> R<T> error(String message){
        R r = new R();
        r.msg = message;
        r.code = 0;
        return r;
    }

    public R<T> add(String key, Object value){
        this.map.put(key,value);
        return this;
    }



}
