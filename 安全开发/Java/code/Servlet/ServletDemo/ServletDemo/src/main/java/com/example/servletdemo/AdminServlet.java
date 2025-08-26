package com.example.servletdemo;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

@WebServlet("/admin")
public class AdminServlet extends HttpServlet {
    @Override
    public void init() throws ServletException {
        //
        System.out.println("Admin init");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        //
        System.out.println("AdminServlet doGet");
        //销毁session
        req.getSession().invalidate();
        //运行此处自动触发监听器的sessionDestroyed方法
    }

    @Override
    public void destroy() {
        //
        super.destroy();
    }
}
