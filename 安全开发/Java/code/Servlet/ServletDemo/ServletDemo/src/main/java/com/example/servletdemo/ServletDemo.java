    package com.example.servletdemo;

    import jakarta.servlet.ServletException;
    import jakarta.servlet.annotation.WebServlet;
    import jakarta.servlet.http.HttpServlet;
    import jakarta.servlet.http.HttpServletRequest;
    import jakarta.servlet.http.HttpServletResponse;

    import java.io.IOException;
    import java.io.PrintWriter;

    @WebServlet(name="demo",value="/demo")
    public class ServletDemo extends HttpServlet {
        @Override
        public void init() throws ServletException {
            System.out.println("init over!");
        }

        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            String name=req.getParameter("name");
            resp.setContentType("text/html;charset=utf-8");
            PrintWriter out=resp.getWriter();
            out.println(name);
            System.out.println("doGet over!");
        }

        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            System.out.println("dopost over!");
        }

        public ServletDemo() {
            System.out.println("contractor over!");
        }
    }
