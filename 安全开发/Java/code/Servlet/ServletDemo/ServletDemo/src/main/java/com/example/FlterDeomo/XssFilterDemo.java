package com.example.FlterDeomo;


import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServletRequest;

import java.io.IOException;


@WebFilter(urlPatterns = "/demo")
public class XssFilterDemo implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        System.out.println("xss filter doFilter");
        HttpServletRequest req = (HttpServletRequest) request;
        String name = req.getParameter("name");
        if(!name.contains("script")){
            chain.doFilter(request,response);
        }else {
            System.out.println("Attack!!!!!!!!!!!");
        }

    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        System.out.println("xss filter init");
    }

    @Override
    public void destroy() {
        System.out.println("xss filter destroy");
    }
}
