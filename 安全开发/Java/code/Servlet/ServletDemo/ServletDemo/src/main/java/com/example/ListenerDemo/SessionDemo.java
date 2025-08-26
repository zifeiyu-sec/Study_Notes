package com.example.ListenerDemo;

import jakarta.servlet.annotation.WebListener;
import jakarta.servlet.http.HttpSession;
import jakarta.servlet.http.HttpSessionEvent;
import jakarta.servlet.http.HttpSessionListener;

@WebListener("/admin")
public class SessionDemo implements HttpSessionListener {
    public void sessionCreated(HttpSessionEvent se) {
        System.out.println("Session Created");
    }
    public void sessionDestroyed(HttpSessionEvent se) {
        System.out.println("Session Destroyed");
    }

}
